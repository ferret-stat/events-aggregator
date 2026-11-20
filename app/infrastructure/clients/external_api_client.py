from typing import Any
from uuid import UUID

import httpx


class ExternalAPIError(Exception):
    """Base exception for external API errors."""


class ExternalAPIClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        api_key: str | None = None,
    ) -> None:
        headers = {}

        if api_key:
            headers["x-api-key"] = api_key

        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            headers=headers,
        )

    @property
    def base_url(self) -> str:
        return str(self._client.base_url)

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any]:
        try:
            response = await self._client.request(
                method,
                endpoint,
                **kwargs,
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(
                f"External API returned status "
                f"{exc.response.status_code}: {exc.response.text}"
            ) from exc

        except httpx.RequestError as exc:
            raise ExternalAPIError(
                f"External API request failed: {type(exc).__name__}: {exc!r}"
            ) from exc

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        return await self._request(
            "GET",
            endpoint,
            params=params,
        )

    async def post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | list[Any]:
        return await self._request(
            "POST",
            endpoint,
            json=payload,
        )

    async def delete(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | list[Any]:
        return await self._request(
            "DELETE",
            endpoint,
            json=payload,
        )

    async def get_events(
        self,
        changed_at: str,
    ) -> dict[str, Any]:
        response = await self.get(
            "/api/events/",
            params={"changed_at": changed_at},
        )

        if not isinstance(response, dict):
            raise ExternalAPIError("Expected an object when fetching events")

        return response

    async def get_seats(
        self,
        event_id: UUID,
    ) -> list[str]:
        response = await self.get(f"/api/events/{event_id}/seats/")

        if not isinstance(response, dict):
            raise ExternalAPIError("Expected an object when fetching seats")

        seats = response.get("seats")

        if not isinstance(seats, list):
            raise ExternalAPIError("Invalid seats response")

        return seats

    async def register(
        self,
        event_id: UUID,
        payload: dict[str, str],
    ) -> dict[str, Any]:
        response = await self.post(
            f"/api/events/{event_id}/register/",
            payload,
        )

        if not isinstance(response, dict):
            raise ExternalAPIError("Expected an object when registering")

        return response

    async def unregister(
        self,
        event_id: UUID,
        ticket_id: UUID,
    ) -> dict[str, Any]:
        response = await self.delete(
            f"/api/events/{event_id}/unregister/",
            {"ticket_id": str(ticket_id)},
        )

        if not isinstance(response, dict):
            raise ExternalAPIError("Expected an object when unregistering")

        return response

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "ExternalAPIClient":
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> None:
        await self.close()
