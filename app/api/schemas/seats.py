from pydantic import BaseModel


class EventSeatsResponse(BaseModel):
    seats: list[str]
