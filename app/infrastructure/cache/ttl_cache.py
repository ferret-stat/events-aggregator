from datetime import UTC, datetime, timedelta
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int = 30) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self._data: dict[UUID, tuple[T, datetime]] = {}

    def get(self, key: UUID) -> T | None:
        item = self._data.get(key)

        if item is None:
            return None

        value, expires_at = item

        if datetime.now(UTC) >= expires_at:
            self._data.pop(key, None)
            return None

        return value

    def set(self, key: UUID, value: T) -> None:
        self._data[key] = (
            value,
            datetime.now(UTC) + self.ttl,
        )
