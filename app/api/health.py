from fastapi import APIRouter

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
def health_check():
    return {"status": "ok"}
