import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_event_sync_service
from app.application.services.event_sync_service import EventSyncService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sync",
    tags=["Synchronization"],
)


@router.post(
    "/trigger",
    status_code=status.HTTP_200_OK,
)
async def trigger_sync(
    service: Annotated[
        EventSyncService,
        Depends(get_event_sync_service),
    ],
) -> dict[str, int | str]:
    try:
        processed = await service.sync_events()

        return {
            "status": "success",
            "processed": processed,
        }

    except Exception as exc:
        logger.exception("Manual synchronization failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Events synchronization failed",
        ) from exc
