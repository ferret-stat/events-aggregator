import pytest

from app.application.usecases.create_event import CreateEventUseCase
from app.domain.entities.event import Event


class FakeEventRepository:
    def __init__(self):
        self.events = {}

    async def create(self, event: Event) -> Event:
        self.events[event.id] = event
        return event

    async def get_by_id(self, event_id):
        return self.events.get(event_id)

    async def get_all(self, limit=100, offset=0):
        return list(self.events.values())[offset : offset + limit]


class FakeUnitOfWork:
    def __init__(self):
        self.events = FakeEventRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rolled_back = True
        else:
            self.committed = True


@pytest.mark.asyncio
async def test_create_event(sample_event):
    uow = FakeUnitOfWork()
    use_case = CreateEventUseCase(uow)

    result = await use_case.execute(sample_event)

    assert result.id == sample_event.id
    assert result.name == "Test Event"
    assert uow.committed is True
    assert uow.rolled_back is False
