from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.repositories.event_repository import (
    PostgreSQLEventRepository,
)
from app.infrastructure.repositories.sync_metadata_repository import (
    PostgreSQLSyncMetadataRepository,
)


class SQLAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        await self.session.begin()

        self.events = PostgreSQLEventRepository(self.session)
        self.sync_metadata = PostgreSQLSyncMetadataRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
