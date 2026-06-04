from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.user import LoginCredentials, TokenResponse, TokenPayload
from app.services import auth_service
from app.api.dependencies.token_auth import get_token_payload

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=TokenResponse ,status_code=status.HTTP_200_OK)
async def login_user(
    payload: LoginCredentials,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    return await auth_service.login_user(session,payload)

@router.post("/auth/send", status_code=status.HTTP_200_OK)
async def send_auth(
    user_token: TokenPayload = Depends(get_token_payload),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await auth_service.send_auth(session, user_token.user_id)
