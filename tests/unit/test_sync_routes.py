from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_event_sync_service
from app.main import app


@pytest.fixture
def sync_service():
    service = MagicMock()
    service.sync_events = AsyncMock()
    return service


@pytest.fixture
async def client(sync_service):
    app.dependency_overrides[get_event_sync_service] = lambda: sync_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_trigger_sync_success(client, sync_service):
    sync_service.sync_events.return_value = 150

    response = await client.post("/api/sync/trigger")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "processed": 150,
    }

    sync_service.sync_events.assert_awaited_once()


@pytest.mark.asyncio
async def test_trigger_sync_failure(client, sync_service):
    sync_service.sync_events.side_effect = RuntimeError("External API unavailable")

    response = await client.post("/api/sync/trigger")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Events synchronization failed",
    }

    sync_service.sync_events.assert_awaited_once()


@pytest.mark.asyncio
async def test_trigger_sync_empty_result(client, sync_service):
    sync_service.sync_events.return_value = 0

    response = await client.post("/api/sync/trigger")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "processed": 0,
    }
