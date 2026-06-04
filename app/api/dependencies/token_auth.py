import jwt
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import APIError
from app.schemas.user import TokenPayload

 
bearer_scheme = HTTPBearer()

#bearer scheme will look for the auth header and check if its of bearer type then make sure formatting is correct, 
# then puts into a dict thats the pydantic schema for authcredentials. 
async def get_token_payload(auth_credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> TokenPayload:
    #the string part of the auth header
    token = auth_credentials.credentials

    try:
        token_data = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithm = settings.JWT_ALGO,
        )

        #The ** takes a dictionary and unpacks it to match the parameters in the object constructor with their respective data
        return TokenPayload(**token_data)
    
    except jwt.ExpiredSignatureError:
        raise APIError(
            status = status.HTTP_401_UNAUTHORIZED,
            code = "token_expired",
            message = "Verification time limit exceeded, please login again."
        )
    
    except jwt.PyJWTError:
        raise APIError(
            status = status.HTTP_401_UNAUTHORIZED,
            code = "invalid_token",
            message = "Credentials could not be validated."
        )
    
    
    