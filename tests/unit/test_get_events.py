import pytest

from app.application.usecases.get_events import GetEventsUseCase
from app.domain.entities.event import Event


class FakeRepository:
    def __init__(self, events: list[Event]):
        self.events = events

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from=None,
    ):
        return self.events[offset : offset + limit]


class FakeUnitOfWork:
    def __init__(self, events: list[Event]):
        self.events = FakeRepository(events)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_events(sample_event):
    uow = FakeUnitOfWork([sample_event])
    use_case = GetEventsUseCase(uow)

    result = await use_case.execute()

    assert len(result) == 1
    assert result[0].id == sample_event.id


@pytest.mark.asyncio
async def test_get_events_with_pagination(sample_event):
    uow = FakeUnitOfWork([sample_event])
    use_case = GetEventsUseCase(uow)

    result = await use_case.execute(
        limit=10,
        offset=1,
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_events_invalid_limit(sample_event):
    uow = FakeUnitOfWork([sample_event])
    use_case = GetEventsUseCase(uow)

    with pytest.raises(ValueError):
        await use_case.execute(limit=0)


@pytest.mark.asyncio
async def test_get_events_invalid_offset(sample_event):
    uow = FakeUnitOfWork([sample_event])
    use_case = GetEventsUseCase(uow)

    with pytest.raises(ValueError):
        await use_case.execute(offset=-1)
