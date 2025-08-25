from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings

# Create synchronous engine for migrations
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    echo=settings.LOG_LEVEL == "DEBUG"
)

# Create async engine for application use
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI).replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    echo=settings.LOG_LEVEL == "DEBUG"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_async_session() -> AsyncSession:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session():
    """Dependency to get synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_tables():
    """Create database tables."""
    async with async_engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        from app.models import user, document, progress, chat  # noqa
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
