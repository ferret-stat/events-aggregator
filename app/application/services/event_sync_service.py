import logging
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from app.application.services.event_mapper import map_event
from app.infrastructure.clients.external_api_client import ExternalAPIClient

logger = logging.getLogger(__name__)

INITIAL_CHANGED_AT = "2000-01-01"


def normalize_pagination_url(url: str) -> str:
    parsed = urlsplit(url)

    if parsed.scheme == "http":
        parsed = parsed._replace(scheme="https")

    return urlunsplit(parsed)


class EventSyncService:
    def __init__(
        self,
        api_client: ExternalAPIClient,
        uow_factory: Any,
    ) -> None:
        self.api_client = api_client
        self.uow_factory = uow_factory

    async def _get_checkpoint(self) -> datetime | None:
        async with self.uow_factory() as uow:
            metadata = await uow.sync_metadata.get()

            if metadata is None:
                return None

            return metadata.last_changed_at

    async def _save_failure(self, error: Exception) -> None:
        async with self.uow_factory() as uow:
            metadata = await uow.sync_metadata.get()

            await uow.sync_metadata.save(
                last_sync_time=metadata.last_sync_time if metadata else None,
                last_changed_at=metadata.last_changed_at if metadata else None,
                sync_status="failed",
                last_error=str(error)[:2000],
            )

    async def sync_events(self) -> int:
        logger.info("Starting events synchronization")

        try:
            checkpoint = await self._get_checkpoint()

            changed_at = (
                checkpoint.date().isoformat()
                if checkpoint is not None
                else INITIAL_CHANGED_AT
            )

            events = []
            next_url = None

            # Получаем все страницы внешнего API.
            while True:
                if next_url:
                    response = await self.api_client.get(
                        normalize_pagination_url(next_url)
                    )
                else:
                    response = await self.api_client.get(
                        "/api/events/",
                        params={"changed_at": changed_at},
                    )

                if not isinstance(response, dict):
                    raise ValueError("Expected an object from external API")

                results = response.get("results")

                if not isinstance(results, list):
                    raise ValueError(
                        "External API response does not contain a valid results list"
                    )

                events.extend(map_event(item) for item in results)

                next_url = response.get("next")

                if not next_url:
                    break

                if not isinstance(next_url, str):
                    raise ValueError("Invalid pagination URL")

            latest_changed_at = max(
                (event.changed_at for event in events),
                default=checkpoint,
            )

            # Сохраняем события и checkpoint атомарно.
            async with self.uow_factory() as uow:
                for event in events:
                    await uow.events.upsert(event)

                await uow.sync_metadata.save(
                    last_sync_time=datetime.now(UTC),
                    last_changed_at=latest_changed_at,
                    sync_status="success",
                    last_error=None,
                )

            logger.info(
                "Events synchronization completed. Processed: %s",
                len(events),
            )

            return len(events)

        except Exception as exc:
            logger.exception("Events synchronization failed")

            try:
                await self._save_failure(exc)
            except Exception:
                logger.exception("Failed to save synchronization error status")

            raise
