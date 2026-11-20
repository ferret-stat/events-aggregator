from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_event_seats_use_case,
    get_event_use_case,
    get_events_use_case,
)
from app.api.schemas.event import EventListResponse, EventResponse
from app.api.schemas.seats import EventSeatsResponse
from app.application.usecases.get_event import GetEventUseCase
from app.application.usecases.get_event_seats import (
    EventNotFoundError,
    EventNotPublishedError,
    GetEventSeatsUseCase,
)
from app.application.usecases.get_events import GetEventsUseCase
from app.infrastructure.clients.external_api_client import ExternalAPIError

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
    date_from: Annotated[date | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 100,
) -> EventListResponse:
    offset = (page - 1) * page_size

    events = await use_case.execute(
        limit=page_size,
        offset=offset,
        date_from=date_from,
    )

    return EventListResponse(
        items=[EventResponse.model_validate(event) for event in events],
        page=page,
        page_size=page_size,
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


@router.get(
    "/{event_id}/seats/",
    response_model=EventSeatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_event_seats(
    event_id: UUID,
    use_case: Annotated[
        GetEventSeatsUseCase,
        Depends(get_event_seats_use_case),
    ],
) -> EventSeatsResponse:
    try:
        seats = await use_case.execute(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EventNotPublishedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="External events provider is unavailable",
        ) from exc

    return EventSeatsResponse(seats=seats)
