from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.usecases.register_ticket import (
    EventNotFoundError,
    EventNotPublishedError,
    RegisterTicketUseCase,
    RegistrationDeadlinePassedError,
    SeatUnavailableError,
)
from app.infrastructure.clients.external_api_client import ExternalAPIError


@pytest.fixture
def register_dependencies():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.events.get_by_id = AsyncMock()
    uow.tickets.create = AsyncMock()

    api_client = MagicMock()
    api_client.get_seats = AsyncMock(return_value=["A1", "A2"])
    api_client.register = AsyncMock()

    cache = MagicMock()

    use_case = RegisterTicketUseCase(
        uow=uow,
        api_client=api_client,
        cache=cache,
    )

    return use_case, uow, api_client, cache


@pytest.mark.asyncio
async def test_register_ticket_success(
    published_event,
    register_dependencies,
):
    use_case, uow, api_client, cache = register_dependencies
    ticket_id = uuid4()

    uow.events.get_by_id.return_value = published_event
    api_client.register.return_value = {"ticket_id": str(ticket_id)}

    result = await use_case.execute(
        event_id=published_event.id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
    )

    assert result == ticket_id
    api_client.get_seats.assert_awaited_once_with(published_event.id)
    api_client.register.assert_awaited_once()
    uow.tickets.create.assert_awaited_once()
    cache.delete.assert_called_once_with(published_event.id)


@pytest.mark.asyncio
async def test_register_ticket_event_not_found(register_dependencies):
    use_case, uow, api_client, cache = register_dependencies
    uow.events.get_by_id.return_value = None

    with pytest.raises(EventNotFoundError):
        await use_case.execute(uuid4(), "Ivan", "Ivanov", "ivan@example.com", "A1")

    api_client.get_seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_ticket_event_not_published(
    sample_event,
    register_dependencies,
):
    use_case, uow, api_client, cache = register_dependencies
    uow.events.get_by_id.return_value = sample_event

    with pytest.raises(EventNotPublishedError):
        await use_case.execute(
            sample_event.id, "Ivan", "Ivanov", "ivan@example.com", "A1"
        )

    api_client.get_seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_ticket_deadline_passed(
    published_event,
    register_dependencies,
):
    use_case, uow, api_client, cache = register_dependencies

    published_event.registration_deadline = datetime.now(UTC) - timedelta(days=1)
    uow.events.get_by_id.return_value = published_event

    with pytest.raises(RegistrationDeadlinePassedError):
        await use_case.execute(
            published_event.id, "Ivan", "Ivanov", "ivan@example.com", "A1"
        )

    api_client.get_seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_ticket_seat_unavailable(
    published_event,
    register_dependencies,
):
    use_case, uow, api_client, cache = register_dependencies
    uow.events.get_by_id.return_value = published_event

    with pytest.raises(SeatUnavailableError):
        await use_case.execute(
            published_event.id, "Ivan", "Ivanov", "ivan@example.com", "A9"
        )

    api_client.register.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_ticket_invalid_provider_response(
    published_event,
    register_dependencies,
):
    use_case, uow, api_client, cache = register_dependencies

    uow.events.get_by_id.return_value = published_event
    api_client.register.return_value = {"unexpected": "response"}

    with pytest.raises(ExternalAPIError):
        await use_case.execute(
            published_event.id, "Ivan", "Ivanov", "ivan@example.com", "A1"
        )

    uow.tickets.create.assert_not_awaited()
