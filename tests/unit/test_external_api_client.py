import httpx
import pytest

from app.core.config import settings
from app.infrastructure.clients.external_api_client import (
    ExternalAPIClient,
    ExternalAPIError,
)


@pytest.mark.asyncio
async def test_get_request():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"id": 1, "name": "Test Event"},
        )

    client = ExternalAPIClient(settings.external_api_url)
    await client._client.aclose()

    client._client = httpx.AsyncClient(
        base_url=settings.external_api_url,
        transport=httpx.MockTransport(handler),
    )

    result = await client.get("/events/1")

    assert result["id"] == 1
    assert result["name"] == "Test Event"

    await client.close()


@pytest.mark.asyncio
async def test_get_request_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = ExternalAPIClient(settings.external_api_url)
    await client._client.aclose()

    client._client = httpx.AsyncClient(
        base_url=settings.external_api_url,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ExternalAPIError):
        await client.get("/events/999")

    await client.close()


@pytest.mark.asyncio
async def test_post_request():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={"id": 10, "status": "created"},
        )

    client = ExternalAPIClient(settings.external_api_url)
    await client._client.aclose()

    client._client = httpx.AsyncClient(
        base_url=settings.external_api_url,
        transport=httpx.MockTransport(handler),
    )

    result = await client.post(
        "/events",
        {"name": "New Event"},
    )

    assert result["id"] == 10
    assert result["status"] == "created"

    await client.close()
