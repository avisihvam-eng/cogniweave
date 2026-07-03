import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = None
async_session = None
IS_SQLITE = False

def init_db_connection():
    global engine, async_session, IS_SQLITE
    sqlite_url = "sqlite+aiosqlite:///./antigravity.db"
    print(f"[Antigravity] Using SQLite database: {sqlite_url}")
    engine = create_async_engine(sqlite_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    IS_SQLITE = True

init_db_connection()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
