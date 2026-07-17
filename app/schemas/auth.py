import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import Username


class AccessTokenPayload(BaseModel):
    user_id: uuid.UUID = Field(alias="sub")
    scope: str
    exp: int

    model_config = {"populate_by_name": True}

class RefreshTokenPayload(BaseModel):
    token_raw: str
    token_hash: str
    expires_at: datetime

    
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900

class LogoutRequest(BaseModel):
    refresh_token: str

class PhoneAuthPayload(BaseModel):
    username: Username
