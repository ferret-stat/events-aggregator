from app.domain.entities.event import Event
from app.domain.unit_of_work import UnitOfWork


class CreateEventUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, event: Event) -> Event:
        async with self.uow:
            created_event = await self.uow.events.create(event)

        return created_event
