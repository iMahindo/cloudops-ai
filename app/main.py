from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.health import health_router
from app.api.routes import router
from app.api.metrics import metrics_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.request_context import request_context_middleware
from app.services.qdrant import create_knowledge_collection

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

    logger.info(
        "Initializing Qdrant collection: %s",
        settings.qdrant_collection
    )
    #create the collection if not exist
    create_knowledge_collection()

    logger.info(
        "Qdrant collection initialized successfully"
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
app.include_router(router)
app.include_router(health_router)
app.include_router(metrics_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

#add the middleware for http requests
app.middleware("http")(request_context_middleware)
