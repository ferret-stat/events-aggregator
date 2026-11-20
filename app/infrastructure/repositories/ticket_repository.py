from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.ticket import Ticket
from app.domain.repositories.ticket_repository import TicketRepository
from app.infrastructure.models.ticket import TicketModel


class PostgreSQLTicketRepository(TicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        model = await self.session.get(TicketModel, ticket_id)

        if model is None:
            return None

        return self._to_entity(model)

    async def create(self, ticket: Ticket) -> Ticket:
        model = TicketModel(
            id=ticket.id,
            event_id=ticket.event_id,
            first_name=ticket.first_name,
            last_name=ticket.last_name,
            email=ticket.email,
            seat=ticket.seat,
            created_at=ticket.created_at,
            cancelled_at=ticket.cancelled_at,
        )

        self.session.add(model)
        await self.session.flush()

        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: TicketModel) -> Ticket:
        return Ticket(
            id=model.id,
            event_id=model.event_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            seat=model.seat,
            created_at=model.created_at,
            cancelled_at=model.cancelled_at,
        )
