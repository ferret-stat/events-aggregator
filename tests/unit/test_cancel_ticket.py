from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.usecases.cancel_ticket import (
    CancelTicketUseCase,
    EventAlreadyStartedError,
    EventNotFoundError,
    TicketAlreadyCancelledError,
    TicketNotFoundError,
)
from app.infrastructure.clients.external_api_client import ExternalAPIError


@pytest.fixture
def cancel_dependencies():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.tickets.get_by_id = AsyncMock()
    uow.tickets.update = AsyncMock()
    uow.events.get_by_id = AsyncMock()

    api_client = MagicMock()
    api_client.base_url = "https://provider.example"
    api_client.unregister = AsyncMock(return_value={"success": True})

    cache = MagicMock()

    use_case = CancelTicketUseCase(
        uow=uow,
        api_client=api_client,
        cache=cache,
    )

    return use_case, uow, api_client, cache


@pytest.mark.asyncio
async def test_cancel_ticket_success(
    sample_ticket,
    published_event,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    uow.tickets.get_by_id.return_value = sample_ticket
    uow.events.get_by_id.return_value = published_event

    await use_case.execute(sample_ticket.id)

    api_client.unregister.assert_awaited_once_with(
        sample_ticket.event_id,
        sample_ticket.id,
    )
    uow.tickets.update.assert_awaited_once_with(sample_ticket)

    assert sample_ticket.cancelled_at is not None
    cache.delete.assert_called_once_with(sample_ticket.event_id)


@pytest.mark.asyncio
async def test_cancel_ticket_not_found(cancel_dependencies):
    use_case, uow, api_client, cache = cancel_dependencies
    uow.tickets.get_by_id.return_value = None

    with pytest.raises(TicketNotFoundError):
        await use_case.execute(sample_ticket_id())

    api_client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_ticket_already_cancelled(
    sample_ticket,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    from datetime import UTC, datetime

    sample_ticket.cancelled_at = datetime.now(UTC)
    uow.tickets.get_by_id.return_value = sample_ticket

    with pytest.raises(TicketAlreadyCancelledError):
        await use_case.execute(sample_ticket.id)

    api_client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_ticket_event_not_found(
    sample_ticket,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    uow.tickets.get_by_id.return_value = sample_ticket
    uow.events.get_by_id.return_value = None

    with pytest.raises(EventNotFoundError):
        await use_case.execute(sample_ticket.id)

    api_client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_ticket_event_already_started(
    sample_ticket,
    sample_event,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    uow.tickets.get_by_id.return_value = sample_ticket
    uow.events.get_by_id.return_value = sample_event

    with pytest.raises(EventAlreadyStartedError):
        await use_case.execute(sample_ticket.id)

    api_client.unregister.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_ticket_provider_error(
    sample_ticket,
    published_event,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    uow.tickets.get_by_id.return_value = sample_ticket
    uow.events.get_by_id.return_value = published_event
    api_client.unregister.side_effect = ExternalAPIError("Provider error")

    with pytest.raises(ExternalAPIError):
        await use_case.execute(sample_ticket.id)

    uow.tickets.update.assert_not_awaited()
    cache.delete.assert_not_called()


@pytest.mark.asyncio
async def test_cancel_ticket_provider_rejected(
    sample_ticket,
    published_event,
    cancel_dependencies,
):
    use_case, uow, api_client, cache = cancel_dependencies

    uow.tickets.get_by_id.return_value = sample_ticket
    uow.events.get_by_id.return_value = published_event
    api_client.unregister.return_value = {"success": False}

    with pytest.raises(ExternalAPIError):
        await use_case.execute(sample_ticket.id)

    uow.tickets.update.assert_not_awaited()


def sample_ticket_id():
    from uuid import uuid4

    return uuid4()
