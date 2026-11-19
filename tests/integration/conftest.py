import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.infrastructure.database import Base


@pytest.fixture
async def test_session_factory():
    database_url = settings.test_database_url

    if not database_url:
        pytest.fail("TEST_DATABASE_URL is not configured")

    engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    yield session_factory

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()
