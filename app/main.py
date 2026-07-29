from fastapi import FastAPI
from _collections_abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.health import health_router
from app.api.routes import root_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

#initialize the logger
setup_logging()

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "%s Application started in %s environment",
        settings.app_name,
        settings.environment,
    )

    yield

    logger.info("%s Application stopped", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description = settings.app_description,
    version = settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

#Routers added to app
app.include_router(root_router)
app.include_router(health_router)
