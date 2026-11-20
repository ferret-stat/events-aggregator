from datetime import UTC, datetime
from uuid import UUID

from app.domain.unit_of_work import UnitOfWork
from app.infrastructure.cache.ttl_cache import TTLCache
from app.infrastructure.clients.external_api_client import (
    ExternalAPIClient,
    ExternalAPIError,
)


class TicketNotFoundError(Exception):
    pass


class TicketAlreadyCancelledError(Exception):
    pass


class EventNotFoundError(Exception):
    pass


class EventAlreadyStartedError(Exception):
    pass


class CancelTicketUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        api_client: ExternalAPIClient,
        cache: TTLCache[list[str]],
    ) -> None:
        self.uow = uow
        self.api_client = api_client
        self.cache = cache

    async def execute(self, ticket_id: UUID) -> None:
        async with self.uow:
            ticket = await self.uow.tickets.get_by_id(ticket_id)

            if ticket is None:
                raise TicketNotFoundError("Ticket not found")

            if ticket.cancelled_at is not None:
                raise TicketAlreadyCancelledError("Ticket has already been cancelled")

            event = await self.uow.events.get_by_id(ticket.event_id)

            if event is None:
                raise EventNotFoundError("Event not found")

            if event.event_time <= datetime.now(UTC):
                raise EventAlreadyStartedError(
                    "Cannot cancel registration for a started event"
                )

            event_id = ticket.event_id

        response = await self.api_client.unregister(event_id, ticket_id)

        if response.get("success") is not True:
            raise ExternalAPIError("External API did not confirm cancellation")

        async with self.uow:
            ticket = await self.uow.tickets.get_by_id(ticket_id)

            if ticket is None:
                raise TicketNotFoundError("Ticket not found")

            if ticket.cancelled_at is not None:
                raise TicketAlreadyCancelledError("Ticket has already been cancelled")

            ticket.cancelled_at = datetime.now(UTC)
            await self.uow.tickets.update(ticket)

        self.cache.delete(event_id)
