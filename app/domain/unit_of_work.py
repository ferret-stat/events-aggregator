from types import TracebackType
from typing import Protocol, Self

from app.domain.repositories.event_repository import EventRepository


class UnitOfWork(Protocol):
    events: EventRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
