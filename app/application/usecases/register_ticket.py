from datetime import UTC, datetime
from uuid import UUID

from app.domain.entities.ticket import Ticket
from app.domain.unit_of_work import UnitOfWork
from app.infrastructure.cache.ttl_cache import TTLCache
from app.infrastructure.clients.external_api_client import ExternalAPIClient


class EventNotFoundError(Exception):
    pass


class EventNotPublishedError(Exception):
    pass


class RegistrationDeadlinePassedError(Exception):
    pass


class SeatUnavailableError(Exception):
    pass


class RegisterTicketUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        api_client: ExternalAPIClient,
        cache: TTLCache[list[str]],
    ) -> None:
        self.uow = uow
        self.api_client = api_client
        self.cache = cache

    async def execute(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> UUID:
        async with self.uow:
            event = await self.uow.events.get_by_id(event_id)

            if event is None:
                raise EventNotFoundError("Event not found")

            if event.status != "published":
                raise EventNotPublishedError("Event is not published")

            now = datetime.now(UTC)

            if now > event.registration_deadline:
                raise RegistrationDeadlinePassedError(
                    "Registration deadline has passed"
                )

        available_seats = await self.api_client.get_seats(event_id)

        if seat not in available_seats:
            raise SeatUnavailableError("Seat is not available")

        response = await self.api_client.register(
            event_id,
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat,
            },
        )

        ticket_id = UUID(response["ticket_id"])

        ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            created_at=datetime.now(UTC),
        )

        async with self.uow:
            await self.uow.tickets.create(ticket)

        self.cache.delete(event_id)

        return ticket_id
