from typing import Any

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
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
        )

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        try:
            response = await self._client.get(
                endpoint,
                params=params,
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(
                f"External API returned status {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise ExternalAPIError(f"External API request failed: {exc}") from exc

        except ValueError as exc:
            raise ExternalAPIError("External API returned invalid JSON") from exc

    async def post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | list[Any]:
        try:
            response = await self._client.post(
                endpoint,
                json=payload,
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            raise ExternalAPIError(
                f"External API returned status {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise ExternalAPIError(f"External API request failed: {exc}") from exc

        except ValueError as exc:
            raise ExternalAPIError("External API returned invalid JSON") from exc

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
