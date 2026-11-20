from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def normalize_pagination_url(url: str, base_url: str) -> str:
    parsed_url = urlsplit(url)
    parsed_base = urlsplit(base_url)

    return urlunsplit(
        (
            parsed_base.scheme,
            parsed_base.netloc,
            parsed_url.path,
            parsed_url.query,
            parsed_url.fragment,
        )
    )


class EventsPaginator:
    def __init__(
        self,
        api_client: Any,
        changed_at: str,
    ) -> None:
        self.api_client = api_client
        self.changed_at = changed_at

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        next_url: str | None = None

        while True:
            if next_url is None:
                response = await self.api_client.get(
                    "/api/events/",
                    params={"changed_at": self.changed_at},
                )
            else:
                response = await self.api_client.get(next_url)

            if not isinstance(response, dict):
                raise ValueError("Expected an object from external API")

            results = response.get("results")

            if not isinstance(results, list):
                raise ValueError(
                    "External API response does not contain a valid results list"
                )

            for item in results:
                if not isinstance(item, dict):
                    raise ValueError("Invalid event in external API response")
                yield item

            next_url = response.get("next")

            if not next_url:
                break

            if not isinstance(next_url, str):
                raise ValueError("Invalid pagination URL")

            next_url = normalize_pagination_url(
                next_url,
                self.api_client.base_url,
            )
