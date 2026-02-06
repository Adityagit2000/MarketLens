"""
Database Connection and Session Management

PostgreSQL + TimescaleDB setup with async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.config.settings import settings

# Convert standard PostgreSQL URL to async
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and TimescaleDB extension."""
    async with engine.begin() as conn:
        # Create TimescaleDB extension if not exists
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Convert OHLCV table to hypertable for time-series optimization
        try:
            await conn.execute(text(
                "SELECT create_hypertable('ohlcv', 'date', if_not_exists => TRUE)"
            ))
        except Exception:
            pass  # Already a hypertable
        
        try:
            await conn.execute(text(
                "SELECT create_hypertable('predictions', 'created_at', if_not_exists => TRUE)"
            ))
        except Exception:
            pass


async def close_db():
    """Close database connections."""
    await engine.dispose()
