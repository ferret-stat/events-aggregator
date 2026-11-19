from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.domain.entities.event import Event
from app.infrastructure.repositories.event_repository import (
    PostgreSQLEventRepository,
)


def test_event_model_to_entity():
    now = datetime.now(UTC)

    place_id = uuid4()
    event_id = uuid4()

    place_model = SimpleNamespace(
        id=place_id,
        name="Test Place",
        city="Tomsk",
        address="Test Street, 1",
        seats_pattern="standard",
        changed_at=now,
        created_at=now,
    )

    event_model = SimpleNamespace(
        id=event_id,
        name="Test Event",
        place=place_model,
        event_time=now,
        registration_deadline=now,
        status="active",
        number_of_visitors=100,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )

    result = PostgreSQLEventRepository._to_entity(event_model)

    assert isinstance(result, Event)
    assert result.id == event_id
    assert result.name == "Test Event"
    assert result.place.id == place_id
    assert result.place.name == "Test Place"
    assert result.number_of_visitors == 100
