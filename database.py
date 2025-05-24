from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from fastapi import Depends
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Utile pour SQLite
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

# Utilisé dans les dépendances FastAPI modernes
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Utilisé dans les anciens fichiers ou scripts directs
@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
