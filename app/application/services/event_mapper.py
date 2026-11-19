from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.entities.event import Event
from app.domain.entities.place import Place


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_event(data: dict[str, Any]) -> Event:
    place_data = data["place"]

    place = Place(
        id=UUID(place_data["id"]),
        name=place_data["name"],
        city=place_data["city"],
        address=place_data["address"],
        seats_pattern=place_data["seats_pattern"],
        changed_at=parse_datetime(place_data["changed_at"]),
        created_at=parse_datetime(place_data["created_at"]),
    )

    return Event(
        id=UUID(data["id"]),
        name=data["name"],
        place=place,
        event_time=parse_datetime(data["event_time"]),
        registration_deadline=parse_datetime(data["registration_deadline"]),
        status=data["status"],
        number_of_visitors=data["number_of_visitors"],
        changed_at=parse_datetime(data["changed_at"]),
        created_at=parse_datetime(data["created_at"]),
        status_changed_at=(
            parse_datetime(data["status_changed_at"])
            if data.get("status_changed_at")
            else None
        ),
    )
