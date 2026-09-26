"""
Database configuration for Neon PostgreSQL.
Uses async SQLAlchemy for FastAPI route handlers
and a sync engine for ML pipeline operations.
"""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/churndb")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql+psycopg2://localhost/churndb")

# Async engine for FastAPI endpoints
async_engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=300)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine for ML pipeline (pandas read_sql, bulk inserts, etc.)
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=300)
SyncSessionLocal = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
