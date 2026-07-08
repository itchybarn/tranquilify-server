from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
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



