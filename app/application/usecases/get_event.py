from uuid import UUID

from app.domain.entities.event import Event
from app.domain.unit_of_work import UnitOfWork


class GetEventUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, event_id: UUID) -> Event | None:
        async with self.uow:
            event = await self.uow.events.get_by_id(event_id)

        return event
