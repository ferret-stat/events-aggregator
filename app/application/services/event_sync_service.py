from app.application.services.event_mapper import map_event
from app.infrastructure.clients.external_api_client import (
    ExternalAPIClient,
)


class EventSyncService:
    def __init__(
        self,
        api_client: ExternalAPIClient,
        uow_factory,
    ) -> None:
        self.api_client = api_client
        self.uow_factory = uow_factory

    async def sync_events(self) -> int:
        response = await self.api_client.get("/events")

        if not isinstance(response, list):
            raise ValueError("Expected a list of events from external API")

        events = [map_event(item) for item in response]

        async with self.uow_factory() as uow:
            for event in events:
                await uow.events.upsert(event)

        return len(events)
