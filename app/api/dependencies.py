from collections.abc import AsyncIterator

from app.infrastructure.database import async_session_factory
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


async def get_uow() -> AsyncIterator[SQLAlchemyUnitOfWork]:
    yield SQLAlchemyUnitOfWork(async_session_factory)
