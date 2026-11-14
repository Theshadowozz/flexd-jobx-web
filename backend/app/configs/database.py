import ssl
from functools import lru_cache

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.configs.settings import get_settings


@lru_cache
def get_session_factory():
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
        connect_args={
            "connect_timeout": settings.db_connect_timeout_seconds,
            "ssl": ssl.create_default_context() if settings.db_tls_enabled else False,
        },
    )
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with get_session_factory()() as db:
        try:
            yield db
        finally:
            await db.rollback()
