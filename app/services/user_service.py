from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import APIError
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    creds = payload.login_credentials

    existing = await session.scalar(
        select(User).where(User.username == creds.username)
    )
    if existing is not None:
        raise APIError(
            status = 409,
            code = "username_taken",
            message = "That username is already taken"
        )
    
    user = User(
        username=creds.username,
        phone_number=payload.auth_method,
        hashed_password=hash_password(creds.password),
    )
    session.add(user)
    await session.commit()
    return user