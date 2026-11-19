from datetime import date

from app.domain.entities.event import Event
from app.domain.unit_of_work import UnitOfWork


class GetEventsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from: date | None = None,
    ) -> list[Event]:
        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500")

        if offset < 0:
            raise ValueError("Offset cannot be negative")

        async with self.uow:
            events = await self.uow.events.get_all(
                limit=limit,
                offset=offset,
                date_from=date_from,
            )

        return events
