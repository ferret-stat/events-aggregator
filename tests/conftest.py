from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities.event import Event
from app.domain.entities.place import Place


@pytest.fixture
def sample_place() -> Place:
    now = datetime.now(UTC)

    return Place(
        id=uuid4(),
        name="Test Place",
        city="Tomsk",
        address="Test Street, 1",
        seats_pattern="standard",
        changed_at=now,
        created_at=now,
    )


@pytest.fixture
def sample_event(sample_place: Place) -> Event:
    now = datetime.now(UTC)

    return Event(
        id=uuid4(),
        name="Test Event",
        place=sample_place,
        event_time=now,
        registration_deadline=now,
        status="active",
        number_of_visitors=100,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )
