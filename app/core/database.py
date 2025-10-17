from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

DATABASE_URL = "postgresql+asyncpg://chatadmin:password@db:5432/meduz_chat"

engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
