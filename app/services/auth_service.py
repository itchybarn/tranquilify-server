from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import APIError
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import LoginCredentials, TokenResponse

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