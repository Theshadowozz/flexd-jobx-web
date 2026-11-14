import ssl
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from app.configs.settings import get_settings
from app.routes import router
from app.utils.exceptions import ERROR_RESPONSES, register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    connect_args = {"connect_timeout": 3, "read_timeout": 3, "write_timeout": 3}
    if settings.db_ssl_disabled:
        connect_args["ssl_disabled"] = True
    elif settings.db_ssl_ca is not None:
        connect_args["ssl"] = ssl.create_default_context(cafile=str(settings.db_ssl_ca))
    else:
        connect_args["ssl"] = ssl.create_default_context()
    app.state.engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    try:
        yield
    finally:
        app.state.engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    debug=False,
    responses=ERROR_RESPONSES,
)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(router)
