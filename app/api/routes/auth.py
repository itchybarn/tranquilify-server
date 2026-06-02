from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.user import LoginCredentials, TokenResponse
from app.services import auth_service

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=TokenResponse ,status_code=status.HTTP_200_OK)
async def login_user(
    payload: LoginCredentials,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    return await auth_service.login_user(session,payload)

