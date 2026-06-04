from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.errors import APIError
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import LoginCredentials, TokenResponse
from twilio.rest import Client
from app.api.dependencies.twilio_2FA import send_verification

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


async def login_user(session: AsyncSession, payload: LoginCredentials) -> TokenResponse:
    user = await check_credentials(session, payload)

    lifespan = 300
    scope = "pre_auth"
    pre_auth_token = create_access_token(
        user_id = str(user.id),
        scope = scope,
        expire_time = lifespan
    )

    return TokenResponse(
        token = pre_auth_token,
        scope = scope,
        expires_in = lifespan
    )

#not throwing error for if user none, because user will be something beyond this point in the flow
async def send_auth(session: AsyncSession, user_id: UUID, twilio_client: Client) -> None:
    user = await session.scalar(
        select(User).where(User.id == user_id)
    )
    #flow: have user, get their phone number, send number a message using the twilio client we setup within the verification methods.
    destination = user.phone_number

    await send_verification(
        twilio_client=twilio_client,
        destination=destination,
        channel="sms",
    )

