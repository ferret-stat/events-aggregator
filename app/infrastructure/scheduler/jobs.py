import logging

from app.application.services.event_sync_service import EventSyncService

logger = logging.getLogger(__name__)


async def sync_events_job(
    sync_service: EventSyncService,
) -> None:
    try:
        count = await sync_service.sync_events()

        logger.info(
            "Events synchronization completed. Processed: %s",
            count,
        )

    except Exception:
        logger.exception("Events synchronization failed")
