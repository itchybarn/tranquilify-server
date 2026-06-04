import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, scope: str, expire_time) -> str:
    expires = datetime.now(timezone.utc) + timedelta(seconds=expire_time)

    payload = {
        "sub": str(user_id),
        "exp": expires,
        "scope": scope, # where we shall dictate if pre_auth state or full_auth
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGO)