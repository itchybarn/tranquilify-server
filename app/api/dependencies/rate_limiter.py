from fastapi import Depends, Request
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_limiter.depends import RateLimiter

# -- identifiers -- Used for how the limit tracking is stored in the library's DB

async def default_identifier(req: Request):
    forwarded = req.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    elif req.client:
        ip = req.client.host
    else:
        ip = "127.0.0.1"
    return ip + ":" + req.scope["path"]

async def username_identifier(req: Request):
    try:
        body = await req.json()
        username = body.get("username", "").lower().strip()
        if not username:
            return await default_identifier(req)
    except Exception:
        return await default_identifier(req)
    
    return username + ":" + req.scope["path"]


# login attempts: 5/min + 20/hr per ip , 10/15min per user
# when we define a list of dependencies for the route header, need to unpack the elements in the list so it doesnt become nested!
login_rate_limits = [
    Depends(RateLimiter(Limiter(Rate(5, Duration.MINUTE)))),
    Depends(RateLimiter(Limiter(Rate(20,Duration.HOUR)))),
    Depends(RateLimiter(Limiter(Rate(10, Duration.MINUTE * 15)), identifier= username_identifier))]

# to protect twilio :) 3/hr per ip
code_rate_limit = Depends(RateLimiter(Limiter(RateLimiter(3, Duration.HOUR))))

# refresh gen: 20/min
refresh_rate_limit = Depends(RateLimiter(Limiter(Rate(20, Duration.MINUTE * 20))))


