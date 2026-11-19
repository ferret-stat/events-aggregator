from uuid import uuid4

from app.application.services.event_mapper import map_event


def test_map_event():
    event_id = uuid4()
    place_id = uuid4()

    data = {
        "id": str(event_id),
        "name": "Python Conference",
        "event_time": "2026-12-01T10:00:00+00:00",
        "registration_deadline": "2026-11-30T20:00:00+00:00",
        "status": "active",
        "number_of_visitors": 100,
        "changed_at": "2026-11-19T10:00:00+00:00",
        "created_at": "2026-11-18T10:00:00+00:00",
        "status_changed_at": "2026-11-19T10:00:00+00:00",
        "place": {
            "id": str(place_id),
            "name": "Conference Hall",
            "city": "Tomsk",
            "address": "Lenina Street, 1",
            "seats_pattern": "standard",
            "changed_at": "2026-11-19T10:00:00+00:00",
            "created_at": "2026-11-18T10:00:00+00:00",
        },
    }

    event = map_event(data)

    assert event.id == event_id
    assert event.name == "Python Conference"
    assert event.place.id == place_id
    assert event.place.city == "Tomsk"
    assert event.number_of_visitors == 100
