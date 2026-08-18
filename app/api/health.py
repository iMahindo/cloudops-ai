from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
def health_check():
    logger.info("Healt check requested")
    return {"status": "ok"}