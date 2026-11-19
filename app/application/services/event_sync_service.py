import logging
from typing import Any

from app.application.services.event_mapper import map_event
from app.infrastructure.clients.external_api_client import (
    ExternalAPIClient,
)

logger = logging.getLogger(__name__)

INITIAL_SYNC_DATE = "2000-01-01"


class EventSyncService:
    def __init__(
        self,
        api_client: ExternalAPIClient,
        uow_factory: Any,
    ) -> None:
        self.api_client = api_client
        self.uow_factory = uow_factory

    async def sync_events(
        self,
        changed_at: str = INITIAL_SYNC_DATE,
    ) -> int:
        logger.info(
            "Starting events synchronization. changed_at=%s",
            changed_at,
        )

        next_url: str | None = "/api/events/"
        params: dict[str, str] | None = {"changed_at": changed_at}

        events = []

        while next_url is not None:
            if params is not None:
                response = await self.api_client.get(
                    next_url,
                    params=params,
                )
            else:
                response = await self.api_client.get(next_url)

            if not isinstance(response, dict):
                raise ValueError("Expected paginated response from Events Provider")

            results = response.get("results")

            if not isinstance(results, list):
                raise ValueError("Invalid events response: 'results' must be a list")

            for item in results:
                events.append(map_event(item))

            next_url = response.get("next")

            if next_url is not None and not isinstance(next_url, str):
                raise ValueError("Invalid pagination URL")

            params = None

        if events:
            async with self.uow_factory() as uow:
                for event in events:
                    await uow.events.upsert(event)

        logger.info(
            "Events synchronization completed. Received %s events",
            len(events),
        )

        return len(events)
