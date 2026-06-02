import uuid
from pydantic import BaseModel, Field
from app.schemas.common import Username, Password

# BaseModel can be serialized to/from JSON
class LoginCredentials(BaseModel):
    username: Username
    password: Password

class UserCreate(BaseModel):
    login_credentials: LoginCredentials
    auth_method: str


#do we wanna move the token schemas into an auth.py file?

class TokenPayload(BaseModel):
    user_id: uuid.UUID = Field(alias="sub")
    scope: str
    exp: int

    model_config = {"populate_by_name": True}

    
class TokenResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    scope: str
    expires_in: int