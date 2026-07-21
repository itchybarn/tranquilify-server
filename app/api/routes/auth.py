from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client

from app.db.session import get_async_session
from app.schemas.user import LoginCredentials
from app.schemas.auth import (
    LoginResponse,
    AccessTokenPayload,
    LogoutRequest,
    PhoneAuthPayload,
    RefreshRequest,
)
from app.services import auth_service
from app.api.dependencies.token_auth import get_access_token_payload
from app.api.dependencies.twilio_2FA import get_twilio_client
from app.api.dependencies.rate_limiter import (
    login_rate_limits,
    code_rate_limit,
    refresh_rate_limit,
)

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=LoginResponse ,status_code=status.HTTP_200_OK, dependencies=login_rate_limits)
async def login_user(
    payload: LoginCredentials,
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponse:
    return await auth_service.login_user(session,payload)

@router.post("/auth/send", status_code=status.HTTP_200_OK, dependencies=[code_rate_limit])
async def send_auth(
    payload: PhoneAuthPayload,
    session: AsyncSession = Depends(get_async_session),
    twilio_client: Client = Depends(get_twilio_client)
) -> None:
    return await auth_service.send_mobile_code(session, payload, twilio_client)

@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK, dependencies=[refresh_rate_limit])
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponse:
    return await auth_service.refresh_tokens(session, payload.refresh_token)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    payload: LogoutRequest,
    user_token: AccessTokenPayload = Depends(get_access_token_payload),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await auth_service.logout_user(session, user_token.user_id, payload.refresh_token)
