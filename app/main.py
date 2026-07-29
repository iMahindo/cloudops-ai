from fastapi import FastAPI

from app.api.health import health_router
from app.api.routes import root_router

app = FastAPI(
    title="CloudOps AI",
    description = "AI-powered knowledge assistant for Cloud Operations",
    version = "0.1.0",
)

#Routers added to app
app.include_router(root_router)
app.include_router(health_router)
