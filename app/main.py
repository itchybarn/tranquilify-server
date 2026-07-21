from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import account, auth
from app.api.dependencies.twilio_2FA import close_twilio_client
from app.core.errors import register_exception_handlers
from app.db.session import get_async_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    # Schema is owned by Alembic ("alembic upgrade head"), not created here.
    yield
    # Runs on shutdown
    await close_twilio_client()
    
app = FastAPI(title="Tranquilify Server", version="0.1.0", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(account.router)
app.include_router(auth.router)

@app.get("/health")
async def health(session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {"status": "ok", "db": db_status}