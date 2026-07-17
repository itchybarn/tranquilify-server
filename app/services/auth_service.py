from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.errors import APIError
from app.core.security import verify_password
from app.api.dependencies.token_auth import create_access_token
from app.api.dependencies.refresh_auth import create_refresh_token
from app.models.user import User
from app.schemas.user import LoginCredentials
from app.schemas.auth import LoginResponse
from twilio.rest import Client
from app.api.dependencies.twilio_2FA import send_verification, check_verification

#Helper function for logging in
async def check_credentials(session: AsyncSession, creds: LoginCredentials) -> User:
    user = await session.scalar(
        select(User).where(User.username == creds.username)
    )

    if user is None or not verify_password(creds.password, user.hashed_password):
        raise APIError(
            status=401,
            code="invalid_credentials",
            message="Invalid username or password"
            )
    
    return user


async def login_user(session: AsyncSession, payload: LoginCredentials) -> LoginResponse:
    user = await check_credentials(session, payload)
    access_token = create_access_token(user_id = str(user.id))
    refresh_token = await create_refresh_token(session, user_id = str(user.id))

    return LoginResponse(access_token = access_token, refresh_token = refresh_token)


#not throwing error for if user none, because user will be something beyond this point in the flow
async def send_mobile_code(session: AsyncSession, user_id: UUID, twilio_client: Client) -> None:
    user = await session.scalar(
        select(User).where(User.id == user_id)
    )
    #flow: have user, get their phone number, send number a message using the 
    # twilio client we setup within the verification methods in twilio_2FA.
    destination = user.phone_number

    await send_verification(
        twilio_client=twilio_client,
        destination=destination,
        channel="sms",
    )

async def check_mobile_code(session: AsyncSession, user_id: UUID, twilio_client: Client, code: str) -> str:
    user = await session.scalar(
        select(User).where(User.id == user_id)
    )

    destination = user.phone_number

    status = await check_verification(
        twilio_client=twilio_client,
        destination=destination,
        code=code
    )

    return status

