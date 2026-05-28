from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# the engine is the connection pool from which we'll form connections
# echo being False keeps SQL out of the logs. should be True when debugging!
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# a session tracks a connection (from the pool), open transation on that connection, and a small cache that tracks ORM objects
# if a connection exists, it'll use that. if not, it'll create another. connections stay
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False, # since we are usingt asyncio
    class_=AsyncSession
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    # async with ensures that the connection is given back to the pool once it's finished
    async with AsyncSessionLocal() as session:
        yield session # waits here until the session is done being used