from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.entities.event import Event
from app.domain.entities.place import Place
from app.domain.entities.ticket import Ticket
from app.domain.enums import EventStatus


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
        status=EventStatus.PUBLISHED,
        number_of_visitors=100,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )


@pytest.fixture
def published_event(sample_event):
    now = datetime.now(UTC)

    return replace(
        sample_event,
        status="published",
        event_time=now + timedelta(days=7),
        registration_deadline=datetime.now(timezone.utc) + timedelta(days=1),
    )


@pytest.fixture
def sample_ticket(published_event):
    return Ticket(
        id=uuid4(),
        event_id=published_event.id,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A1",
        created_at=datetime.now(UTC),
        cancelled_at=None,
    )
