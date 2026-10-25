"""Database connection, session management and health probe."""
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
from app.logging_config import logger


class Base(DeclarativeBase):
    """Base model for all VidyaSetu SQLAlchemy 2.x entities."""
    pass


# SQLite-specific connect args
engine_kwargs: Dict[str, Any] = {
    "echo": False,
    "future": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL pool settings
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection() -> Dict[str, Any]:
    """Inspect database connectivity safely for health probe without raising uncaught exceptions."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            dialect_name = engine.dialect.name
            return {
                "connected": True,
                "dialect": dialect_name,
                "message": "Database connection verified successfully",
            }
    except Exception as exc:
        logger.warning(f"Database health check failed: {type(exc).__name__}")
        return {
            "connected": False,
            "dialect": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "message": f"Database unreachable: {type(exc).__name__}",
        }
