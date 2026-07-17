from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client

from app.db.session import get_async_session
from app.schemas.user import LoginCredentials
from app.schemas.auth import LoginResponse, PhoneAuthPayload
from app.services import auth_service
from app.api.dependencies.twilio_2FA import get_twilio_client
from app.api.dependencies.rate_limiter import login_rate_limits, code_rate_limit

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=LoginResponse ,status_code=status.HTTP_200_OK, dependencies= [login_rate_limits])
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
