from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.application.services.event_sync_service import EventSyncService
from app.core.config import settings
from app.infrastructure.clients.external_api_client import ExternalAPIClient
from app.infrastructure.database import async_session_factory
from app.infrastructure.scheduler.jobs import sync_events_job
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


def create_sync_service() -> EventSyncService:
    api_client = ExternalAPIClient(
        base_url=settings.external_api_url,
        api_key=settings.external_api_key,
    )

    return EventSyncService(
        api_client=api_client,
        uow_factory=lambda: SQLAlchemyUnitOfWork(async_session_factory),
    )


async def scheduled_sync() -> None:
    sync_service = create_sync_service()

    try:
        await sync_events_job(sync_service)
    finally:
        await sync_service.api_client.close()


scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    # Первая синхронизация сразу после запуска приложения.
    scheduler.add_job(
        scheduled_sync,
        trigger="date",
        id="events_sync_initial",
        replace_existing=True,
    )

    # Последующие синхронизации по расписанию.
    scheduler.add_job(
        scheduled_sync,
        trigger="interval",
        minutes=settings.sync_interval_minutes,
        id="events_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    if not scheduler.running:
        scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
