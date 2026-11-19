from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.event_sync_service import EventSyncService


@pytest.fixture
def setup_sync_service():
    api_client = MagicMock()
    api_client.get = AsyncMock()

    uow = MagicMock()
    uow.events.upsert = AsyncMock()
    uow.sync_metadata.get = AsyncMock(return_value=None)
    uow.sync_metadata.save = AsyncMock()

    uow_context = MagicMock()
    uow_context.__aenter__ = AsyncMock(return_value=uow)
    uow_context.__aexit__ = AsyncMock(return_value=None)

    uow_factory = MagicMock(return_value=uow_context)

    service = EventSyncService(
        api_client=api_client,
        uow_factory=uow_factory,
    )

    return service, api_client, uow, uow_factory


@pytest.mark.asyncio
async def test_first_sync_uses_initial_date(setup_sync_service):
    service, api_client, uow, _ = setup_sync_service

    api_client.get.return_value = {
        "results": [],
        "next": None,
    }

    result = await service.sync_events()

    assert result == 0

    api_client.get.assert_awaited_once_with(
        "/api/events/",
        params={"changed_at": "2000-01-01"},
    )

    uow.sync_metadata.save.assert_awaited_once()

    saved_data = uow.sync_metadata.save.await_args.kwargs

    assert saved_data["sync_status"] == "success"
    assert saved_data["last_changed_at"] is None


@pytest.mark.asyncio
async def test_sync_uses_existing_checkpoint(setup_sync_service):
    service, api_client, uow, _ = setup_sync_service

    checkpoint = datetime(2026, 11, 18, 15, 30, tzinfo=UTC)

    uow.sync_metadata.get.return_value = SimpleNamespace(
        last_changed_at=checkpoint,
        last_sync_time=None,
    )

    api_client.get.return_value = {
        "results": [],
        "next": None,
    }

    await service.sync_events()

    api_client.get.assert_awaited_once_with(
        "/api/events/",
        params={"changed_at": "2026-11-18"},
    )


@pytest.mark.asyncio
async def test_sync_processes_all_pages(setup_sync_service):
    service, api_client, _, _ = setup_sync_service

    api_client.get.side_effect = [
        {
            "results": [],
            "next": "https://provider.example/api/events/?cursor=next",
        },
        {
            "results": [],
            "next": None,
        },
    ]

    result = await service.sync_events()

    assert result == 0
    assert api_client.get.await_count == 2

    api_client.get.assert_any_await(
        "/api/events/",
        params={"changed_at": "2000-01-01"},
    )

    api_client.get.assert_any_await(
        "https://provider.example/api/events/?cursor=next",
    )


@pytest.mark.asyncio
async def test_empty_sync_does_not_reset_checkpoint(setup_sync_service):
    service, api_client, uow, _ = setup_sync_service

    checkpoint = datetime(2026, 11, 18, 15, 30, tzinfo=UTC)

    uow.sync_metadata.get.return_value = SimpleNamespace(
        last_changed_at=checkpoint,
        last_sync_time=None,
    )

    api_client.get.return_value = {
        "results": [],
        "next": None,
    }

    await service.sync_events()

    saved_data = uow.sync_metadata.save.await_args.kwargs

    assert saved_data["last_changed_at"] == checkpoint


@pytest.mark.asyncio
async def test_api_error_does_not_advance_checkpoint(setup_sync_service):
    service, api_client, uow, _ = setup_sync_service

    checkpoint = datetime(2026, 11, 18, 15, 30, tzinfo=UTC)

    uow.sync_metadata.get.return_value = SimpleNamespace(
        last_changed_at=checkpoint,
        last_sync_time=None,
    )

    api_client.get.side_effect = RuntimeError("API unavailable")

    with pytest.raises(RuntimeError, match="API unavailable"):
        await service.sync_events()

    # Первый вызов save — фиксация статуса failed.
    uow.sync_metadata.save.assert_awaited_once()

    saved_data = uow.sync_metadata.save.await_args.kwargs

    assert saved_data["sync_status"] == "failed"
    assert saved_data["last_changed_at"] == checkpoint
