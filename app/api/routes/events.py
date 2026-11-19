from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_event_use_case,
    get_events_use_case,
)
from app.api.schemas.event import EventListResponse, EventResponse
from app.application.usecases.get_event import GetEventUseCase
from app.application.usecases.get_events import GetEventsUseCase

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get(
    "/",
    response_model=EventListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_events(
    use_case: Annotated[
        GetEventsUseCase,
        Depends(get_events_use_case),
    ],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EventListResponse:
    events = await use_case.execute(
        limit=limit,
        offset=offset,
    )

    return EventListResponse(
        items=[EventResponse.model_validate(event) for event in events],
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
)
async def get_event(
    event_id: UUID,
    use_case: Annotated[
        GetEventUseCase,
        Depends(get_event_use_case),
    ],
) -> EventResponse:
    event = await use_case.execute(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventResponse.model_validate(event)
