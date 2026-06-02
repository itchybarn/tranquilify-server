from pydantic import BaseModel
from app.schemas.common import Username, Password

# BaseModel can be serialized to/from JSON
class LoginCredentials(BaseModel):
    username: Username
    password: Password

class UserCreate(BaseModel):
    login_credentials: LoginCredentials
    auth_method: str

class TokenResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    scope: str
    expires_in: int