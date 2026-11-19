from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends

from app.application.usecases.get_event import GetEventUseCase
from app.application.usecases.get_events import GetEventsUseCase
from app.infrastructure.database import async_session_factory
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


async def get_uow() -> AsyncIterator[SQLAlchemyUnitOfWork]:
    yield SQLAlchemyUnitOfWork(async_session_factory)


def get_event_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
) -> GetEventUseCase:
    return GetEventUseCase(uow)


def get_events_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
) -> GetEventsUseCase:
    return GetEventsUseCase(uow)
