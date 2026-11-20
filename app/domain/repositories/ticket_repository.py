from typing import Protocol
from uuid import UUID

from app.domain.entities.ticket import Ticket


class TicketRepository(Protocol):
    async def get_by_id(self, ticket_id: UUID) -> Ticket | None: ...

    async def create(self, ticket: Ticket) -> Ticket: ...

    async def update(self, ticket: Ticket) -> Ticket: ...
