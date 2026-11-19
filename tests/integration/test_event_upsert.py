from dataclasses import replace

import pytest

from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_upsert_creates_event(
    test_session_factory,
    sample_event,
):
    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        result = await uow.events.upsert(sample_event)

    assert result.id == sample_event.id
    assert result.name == sample_event.name
    assert result.place.id == sample_event.place.id

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        saved_event = await uow.events.get_by_id(sample_event.id)

    assert saved_event is not None
    assert saved_event.name == sample_event.name


@pytest.mark.asyncio
async def test_upsert_updates_existing_event(
    test_session_factory,
    sample_event,
):
    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        await uow.events.upsert(sample_event)

    updated_event = replace(
        sample_event,
        name="Updated Event",
    )

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        result = await uow.events.upsert(updated_event)

    assert result.name == "Updated Event"

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        saved_event = await uow.events.get_by_id(sample_event.id)

    assert saved_event is not None
    assert saved_event.name == "Updated Event"
