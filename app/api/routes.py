from fastapi import APIRouter

root_router = APIRouter(tags=["General"])

@root_router.get("/")
def read_root():
    return {"message": "Welcome to CloudOps AI"}