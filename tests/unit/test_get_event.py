import pytest

from app.application.usecases.get_event import GetEventUseCase
from app.domain.entities.event import Event


class FakeRepository:
    def __init__(self, event: Event):
        self.event = event

    async def get_by_id(self, event_id):
        if self.event.id == event_id:
            return self.event
        return None


class FakeUnitOfWork:
    def __init__(self, event: Event):
        self.events = FakeRepository(event)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_event(sample_event):
    uow = FakeUnitOfWork(sample_event)
    use_case = GetEventUseCase(uow)

    result = await use_case.execute(sample_event.id)

    assert result is not None
    assert result.id == sample_event.id
    assert result.name == sample_event.name


@pytest.mark.asyncio
async def test_get_event_not_found(sample_event):
    uow = FakeUnitOfWork(sample_event)
    use_case = GetEventUseCase(uow)

    result = await use_case.execute(__import__("uuid").uuid4())

    assert result is None
