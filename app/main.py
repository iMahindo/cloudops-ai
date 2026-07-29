from fastapi import FastAPI

from app.api.health import health_router
from app.api.routes import root_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description = settings.app_description,
    version = settings.app_version,
    debug=settings.debug,
)

#Routers added to app
app.include_router(root_router)
app.include_router(health_router)
