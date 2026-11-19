from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.entities.event import Event


class EventRepository(Protocol):
    async def get_by_id(self, event_id: UUID) -> Event | None: ...

    async def create(self, event: Event) -> Event: ...

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from: date | None = None,
    ) -> list[Event]: ...

    async def upsert(self, event: Event) -> Event: ...
