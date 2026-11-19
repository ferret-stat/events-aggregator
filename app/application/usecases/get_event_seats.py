from uuid import UUID

from app.application.usecases.get_event import GetEventUseCase
from app.infrastructure.clients.external_api_client import ExternalAPIClient


class EventNotFoundError(Exception):
    pass


class EventNotPublishedError(Exception):
    pass


class GetEventSeatsUseCase:
    def __init__(
        self,
        event_use_case: GetEventUseCase,
        api_client: ExternalAPIClient,
        cache,
    ) -> None:
        self.event_use_case = event_use_case
        self.api_client = api_client
        self.cache = cache

    async def execute(self, event_id: UUID) -> list[str]:
        event = await self.event_use_case.execute(event_id)

        if event is None:
            raise EventNotFoundError("Event not found")

        if event.status != "published":
            raise EventNotPublishedError(
                "Seats are available only for published events"
            )

        cached_seats = self.cache.get(event_id)

        if cached_seats is not None:
            return cached_seats

        seats = await self.api_client.get_seats(event_id)
        self.cache.set(event_id, seats)

        return seats
