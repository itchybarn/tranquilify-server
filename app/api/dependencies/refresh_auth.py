from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import APIError
from app.models.refresh_token import RefreshToken
from app.schemas.auth import RefreshTokenPayload
import hashlib
import secrets

REFRESH_TOKEN_BYTES = 32
REFRESH_TOKEN_DAYS = 30

def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

def generate_refresh_token() -> RefreshTokenPayload:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    token_raw = secrets.token_urlsafe(REFRESH_TOKEN_BYTES)
    token_hash = hash_token(token_raw)

    return RefreshTokenPayload(
        token_raw = token_raw,
        token_hash = token_hash,
        expires_at = expires_at
        )

# TODO: add ip and device info (optional)
async def create_refresh_token(session: AsyncSession, user_id: str) -> str:
    refreshTokenPayload = generate_refresh_token()
    token_row = RefreshToken(
        token_hash = refreshTokenPayload.token_hash,
        user_id = user_id,
        expires_at = refreshTokenPayload.expires_at
    )

    session.add(token_row)
    await session.commit()
    return refreshTokenPayload.token_raw


# Look up a raw refresh token and confirm it's usable.
# Returns the row on success; raises APIError(401, "invalid_refresh_token") for
# unknown, revoked, or expired tokens. One error code for all three by design
# (see plan: simple reject, no reuse detection).
async def validate_refresh_token(session: AsyncSession, raw_token: str) -> RefreshToken:
    token_row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token))
    )

    now = datetime.now(timezone.utc)
    if token_row is None or token_row.revoked or token_row.expires_at <= now:
        raise APIError(
            status=401,
            code="invalid_refresh_token",
            message="Refresh token is invalid, revoked, or expired."
        )

    return token_row


# Issue a fresh refresh token and mark the old one as replaced. Caller is
# responsible for committing the transaction so the whole rotation is atomic.
async def rotate_refresh_token(session: AsyncSession, old_row: RefreshToken) -> str:
    payload = generate_refresh_token()
    new_row = RefreshToken(
        token_hash=payload.token_hash,
        user_id=old_row.user_id,
        expires_at=payload.expires_at,
    )
    session.add(new_row)
    # flush so new_row.id is populated before we reference it on the old row
    await session.flush()

    now = datetime.now(timezone.utc)
    old_row.revoked = True
    old_row.revoked_at = now
    old_row.last_used_at = now
    old_row.replaced_by_id = new_row.id

    return payload.token_raw
