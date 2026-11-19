from dataclasses import replace

import pytest
from sqlalchemy import func, select

from app.infrastructure.models.event import EventModel
from app.infrastructure.models.place import PlaceModel
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


@pytest.mark.asyncio
async def test_upsert_does_not_create_duplicates(
    test_session_factory,
    sample_event,
):
    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        await uow.events.upsert(sample_event)

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        await uow.events.upsert(sample_event)

    async with test_session_factory() as session:
        events_count = await session.scalar(
            select(func.count()).select_from(EventModel)
        )

        places_count = await session.scalar(
            select(func.count()).select_from(PlaceModel)
        )

    assert events_count == 1
    assert places_count == 1


@pytest.mark.asyncio
async def test_upsert_updates_place(
    test_session_factory,
    sample_event,
):
    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        await uow.events.upsert(sample_event)

    updated_place = replace(
        sample_event.place,
        name="Updated Conference Hall",
    )

    updated_event = replace(
        sample_event,
        place=updated_place,
    )

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        result = await uow.events.upsert(updated_event)

    assert result.place.name == "Updated Conference Hall"

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        saved_event = await uow.events.get_by_id(sample_event.id)

    assert saved_event is not None
    assert saved_event.place.name == "Updated Conference Hall"
