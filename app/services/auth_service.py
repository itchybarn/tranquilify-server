from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.api_errors import (
    invalid_credentials,
    user_not_found,
    incorrect_current_password,
    code_incorrect,
    invalid_login_method
)
from app.core.security import verify_password, hash_password
from app.api.dependencies.token_auth import create_access_token
from app.api.dependencies.refresh_auth import (
    create_refresh_token,
    hash_token,
    validate_refresh_token,
    rotate_refresh_token,
    revoke_all_user_tokens,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import LoginCredentials, LoginPayload
from app.schemas.auth import LoginResponse, PhoneAuthPayload
from app.schemas.common import Username, Password
from twilio.rest import Client
from app.api.dependencies.twilio_2FA import send_verification, check_verification

# helper function for loggin in with password
async def get_user_from_password(session: AsyncSession, username: Username, password: Password) -> User:
    user = await session.scalar(
        select(User).where(User.username == username)
    )

    if user is None or not verify_password(password, user.hashed_password):
        raise invalid_credentials()

    return user

# helper function for logging in with code
async def get_user_from_code(session: AsyncSession, username: Username, code: str, twilio_client: Client) -> User:
    user = await session.scalar(
        select(User).where(User.username == username)
        )
    if user is None:
        raise invalid_credentials()
    
    status = await check_mobile_code(twilio_client, user, code)
    if status != "approved":
        return code_incorrect()
    
    return user

async def login_user(session: AsyncSession, twilio_client: Client, payload: LoginPayload) -> LoginResponse:
    if payload.login_method == "password":
        user = await get_user_from_password(session, username=payload.username, password=payload.login_value)
    elif payload.login_method == "code":
        user = await get_user_from_code(session, username=payload.username, code=payload.login_value, twilio_client=twilio_client)
    else:
        raise invalid_login_method()

    access_token = create_access_token(user_id = str(user.id))
    refresh_token = await create_refresh_token(session, user_id = str(user.id))

    return LoginResponse(access_token = access_token, refresh_token = refresh_token)


async def send_mobile_code(session: AsyncSession, twilio_client: Client, payload: PhoneAuthPayload) -> None:
    user = await session.scalar(
        select(User).where(User.username == payload.username)
    )
    if user is None:
        raise user_not_found()
    #flow: have user, get their phone number, send number a message using the 
    # twilio client we setup within the verification methods in twilio_2FA.
    destination = user.phone_number

    await send_verification(
        twilio_client=twilio_client,
        destination=destination,
        channel="sms",
    )


async def refresh_tokens(session: AsyncSession, refresh_token_raw: str) -> LoginResponse:
    old_row = await validate_refresh_token(session, refresh_token_raw)
    access_token = create_access_token(user_id=str(old_row.user_id))
    new_refresh_raw = await rotate_refresh_token(session, old_row)
    await session.commit()

    return LoginResponse(access_token=access_token, refresh_token=new_refresh_raw)


async def logout_user(session: AsyncSession, user_id: UUID, refresh_token_raw: str) -> None:
    token_hash = hash_token(refresh_token_raw)

    token_row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )

    # silently succeed if not found, wrong owner, or already revoked.
    if token_row is None or token_row.user_id != user_id or token_row.revoked:
        return

    token_row.revoked = True
    token_row.revoked_at = datetime.now(timezone.utc)
    await session.commit()


async def change_password(session: AsyncSession, user_id: UUID, current_password: str, new_password: str) -> None:
    user = await session.scalar(
        select(User).where(User.id == user_id)
    )
    if user is None:
        raise user_not_found()

    if not verify_password(current_password, user.hashed_password):
        raise incorrect_current_password()

    user.hashed_password = hash_password(new_password)
    # Revoke all sessions so a changed password takes effect everywhere.
    await revoke_all_user_tokens(session, user.id)
    await session.commit()


async def reset_password(session: AsyncSession, twilio_client: Client, username: str, code: str, new_password: str) -> None:
    user = await session.scalar(
        select(User).where(User.username == username)
    )

    # Generic failure whether the user is missing or the code is wrong, so this
    # endpoint can't be used to discover which usernames exist.
    if user is None:
        raise code_incorrect()

    status = await check_verification(
        twilio_client=twilio_client,
        destination=user.phone_number,
        code=code
    )
    if status != "approved":
        raise code_incorrect()

    user.hashed_password = hash_password(new_password)
    # Revoke all sessions so a reset password locks out any existing (possibly attacker) sessions.
    await revoke_all_user_tokens(session, user.id)
    await session.commit()


async def check_mobile_code(twilio_client: Client, user: User, code: str) -> str:
    destination = user.phone_number

    status = await check_verification(
        twilio_client=twilio_client,
        destination=destination,
        code=code
    )

    return status
