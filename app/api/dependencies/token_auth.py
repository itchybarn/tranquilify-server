import jwt
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.errors import APIError
from app.schemas.auth import AccessTokenPayload
from datetime import datetime, timedelta, timezone

BEARER_SCHEME = HTTPBearer()
SCOPE = "Bearer"
ACCESS_TOKEN_MINUTES = 15


def create_access_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expires,
        "scope": SCOPE
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGO)

#will only pass the auth creds if they match the bearer scheme, 
# then puts into a dict thats the pydantic schema for authcredentials. 
async def get_access_token_payload(auth_credentials: HTTPAuthorizationCredentials = Depends(BEARER_SCHEME)) -> AccessTokenPayload:
    #the string part of the auth header
    token = auth_credentials.credentials

    try:
        token_data = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms = [settings.JWT_ALGO],
        )

        #The ** takes a dictionary and unpacks it to match the parameters in the object constructor with their respective data
        return AccessTokenPayload(**token_data)
    
    except jwt.ExpiredSignatureError:
        raise APIError(
            status = status.HTTP_401_UNAUTHORIZED,
            #the error frontend will look for in order to hit /api/auth/refresh?
            code = "token_expired",
            message = "Access token has expired."
        )
    
    except jwt.PyJWTError:
        raise APIError(
            status = status.HTTP_401_UNAUTHORIZED,
            code = "invalid_token",
            message = "Credentials could not be validated."
        )
    
    
    