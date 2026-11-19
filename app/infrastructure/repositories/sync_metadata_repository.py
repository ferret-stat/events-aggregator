from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.sync_metadata import SyncMetadataModel


class PostgreSQLSyncMetadataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> SyncMetadataModel | None:
        result = await self.session.execute(
            select(SyncMetadataModel).where(SyncMetadataModel.id == 1)
        )
        return result.scalar_one_or_none()

    async def save(
        self,
        *,
        last_sync_time=None,
        last_changed_at=None,
        sync_status: str,
        last_error: str | None = None,
    ) -> SyncMetadataModel:
        metadata = await self.get()

        if metadata is None:
            metadata = SyncMetadataModel(id=1)
            self.session.add(metadata)

        metadata.last_sync_time = last_sync_time
        metadata.last_changed_at = last_changed_at
        metadata.sync_status = sync_status
        metadata.last_error = last_error

        await self.session.flush()

        return metadata
