from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.user import UserCreate, LoginCredentials, TokenResponse
from app.services import user_service

router = APIRouter(tags=["account"])

@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await user_service.create_user(session, payload)