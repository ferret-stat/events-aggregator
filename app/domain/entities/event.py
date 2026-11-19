from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Event:
    id: UUID
    provider_id: int
    title: str
    description: str | None
    status: str
    starts_at: datetime
    ends_at: datetime | None
    changed_at: datetime
