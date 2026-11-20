from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends

from app.application.usecases.get_event import GetEventUseCase
from app.application.usecases.get_event_seats import GetEventSeatsUseCase
from app.application.usecases.get_events import GetEventsUseCase
from app.application.usecases.register_ticket import RegisterTicketUseCase
from app.core.config import settings
from app.infrastructure.cache.ttl_cache import TTLCache
from app.infrastructure.clients.external_api_client import ExternalAPIClient
from app.infrastructure.database import async_session_factory
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork

seats_cache = TTLCache[list[str]](
    ttl_seconds=settings.seats_cache_ttl_seconds,
)


async def get_uow() -> AsyncIterator[SQLAlchemyUnitOfWork]:
    yield SQLAlchemyUnitOfWork(async_session_factory)


async def get_external_api_client() -> AsyncIterator[ExternalAPIClient]:
    client = ExternalAPIClient(
        base_url=settings.external_api_url,
        api_key=settings.external_api_key,
    )
    try:
        yield client
    finally:
        await client.close()


def get_event_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
) -> GetEventUseCase:
    return GetEventUseCase(uow)


def get_events_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
) -> GetEventsUseCase:
    return GetEventsUseCase(uow)


def get_event_seats_use_case(
    event_use_case: Annotated[
        GetEventUseCase,
        Depends(get_event_use_case),
    ],
    api_client: Annotated[
        ExternalAPIClient,
        Depends(get_external_api_client),
    ],
) -> GetEventSeatsUseCase:
    return GetEventSeatsUseCase(
        event_use_case=event_use_case,
        api_client=api_client,
        cache=seats_cache,
    )

def get_register_ticket_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    api_client: Annotated[ExternalAPIClient, Depends(get_external_api_client)],
) -> RegisterTicketUseCase:
    return RegisterTicketUseCase(
        uow=uow,
        api_client=api_client,
        cache=seats_cache,
    )
