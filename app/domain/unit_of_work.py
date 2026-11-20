from types import TracebackType
from typing import Protocol, Self

from app.domain.repositories.event_repository import EventRepository
from app.domain.repositories.sync_metadata_repository import (
    SyncMetadataRepository,
)
from app.domain.repositories.ticket_repository import TicketRepository


class UnitOfWork(Protocol):
    events: EventRepository
    sync_metadata: SyncMetadataRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        tickets: TicketRepository,
    ) -> None: ...
