from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_register_ticket_use_case
from app.api.schemas.ticket import TicketCreateRequest, TicketResponse
from app.application.usecases.register_ticket import (
    EventNotFoundError,
    EventNotPublishedError,
    RegisterTicketUseCase,
    RegistrationDeadlinePassedError,
    SeatUnavailableError,
)
from app.infrastructure.clients.external_api_client import ExternalAPIError

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_ticket(
    payload: TicketCreateRequest,
    use_case: Annotated[
        RegisterTicketUseCase,
        Depends(get_register_ticket_use_case),
    ],
) -> TicketResponse:
    try:
        ticket_id = await use_case.execute(
            event_id=payload.event_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            seat=payload.seat,
        )
    except EventNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except EventNotPublishedError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except RegistrationDeadlinePassedError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except SeatUnavailableError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except ExternalAPIError as exc:
        raise HTTPException(
            502,
            detail="External events provider is unavailable",
        ) from exc

    return TicketResponse(ticket_id=ticket_id)
