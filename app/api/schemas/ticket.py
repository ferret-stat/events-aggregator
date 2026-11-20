from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TicketCreateRequest(BaseModel):
    event_id: UUID
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    seat: str = Field(min_length=1, max_length=50)


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: UUID
