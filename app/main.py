from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.sync import router as sync_router
from app.api.routes.tickets import router as tickets_router
from app.core.logging_config import setup_logging
from app.infrastructure.database import close_database
from app.infrastructure.scheduler.scheduler import (
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    setup_logging()

    yield

    stop_scheduler()
    await close_database()


app = FastAPI(
    title="Events Aggregator",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    status_code = (
        400 if request.method == "POST" and request.url.path == "/api/tickets" else 422
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.errors()},
    )


app.include_router(health_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(tickets_router, prefix="/api")
app.include_router(sync_router, prefix="/api")
