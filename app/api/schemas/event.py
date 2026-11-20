from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.schemas.place import PlaceResponse
from app.domain.enums import EventStatus


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    place: PlaceResponse
    event_time: datetime
    registration_deadline: datetime
    status: EventStatus
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime | None = None


class EventListResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventResponse]
