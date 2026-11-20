from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TicketCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: UUID
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    seat: str = Field(min_length=1, max_length=50)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("seat")
    @classmethod
    def validate_seat(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Seat cannot be empty")
        return value


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: UUID

