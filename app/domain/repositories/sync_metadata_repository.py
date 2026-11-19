from datetime import datetime
from typing import Protocol


class SyncMetadataRepository(Protocol):
    async def get(self): ...

    async def save(
        self,
        *,
        last_sync_time: datetime | None = None,
        last_changed_at: datetime | None = None,
        sync_status: str,
        last_error: str | None = None,
    ): ...
