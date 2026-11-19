from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Backend Service",
    description="Backend service API",
    version="0.1.0",
)

app.include_router(
    health_router,
    prefix="/api",
    tags=["Health"],
)