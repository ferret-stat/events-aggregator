import pytest

from app.infrastructure.models.place import PlaceModel
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@pytest.fixture
async def prepared_place(test_session_factory, sample_place):
    async with test_session_factory() as session:
        place = PlaceModel(
            id=sample_place.id,
            name=sample_place.name,
            city=sample_place.city,
            address=sample_place.address,
            seats_pattern=sample_place.seats_pattern,
            changed_at=sample_place.changed_at,
            created_at=sample_place.created_at,
        )

        session.add(place)
        await session.commit()

    return sample_place


@pytest.mark.asyncio
async def test_create_event_in_database(
    test_session_factory,
    prepared_place,
    sample_event,
):
    uow = SQLAlchemyUnitOfWork(test_session_factory)

    result = await uow.events.create(sample_event) if False else None

    async with uow:
        result = await uow.events.create(sample_event)

    assert result.id == sample_event.id
    assert result.name == sample_event.name

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        saved_event = await uow.events.get_by_id(sample_event.id)

    assert saved_event is not None
    assert saved_event.id == sample_event.id
    assert saved_event.place.id == prepared_place.id


@pytest.mark.asyncio
async def test_rollback_event_creation(
    test_session_factory,
    prepared_place,
    sample_event,
):
    uow = SQLAlchemyUnitOfWork(test_session_factory)

    with pytest.raises(RuntimeError):
        async with uow:
            await uow.events.create(sample_event)
            raise RuntimeError("Force rollback")

    async with SQLAlchemyUnitOfWork(test_session_factory) as uow:
        result = await uow.events.get_by_id(sample_event.id)

    assert result is None
