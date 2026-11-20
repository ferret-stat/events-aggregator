from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_cancel_ticket_use_case,
    get_register_ticket_use_case,
)
from app.api.schemas.ticket import TicketCreateRequest, TicketResponse
from app.application.usecases.cancel_ticket import (
    CancelTicketUseCase,
    EventAlreadyStartedError,
    EventNotFoundError,
    TicketAlreadyCancelledError,
    TicketNotFoundError,
)
from app.application.usecases.register_ticket import (
    EventNotFoundError as RegistrationEventNotFoundError,
)
from app.application.usecases.register_ticket import (
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
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
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
    except RegistrationEventNotFoundError as exc:
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


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
)
async def cancel_ticket(
    ticket_id: UUID,
    use_case: Annotated[
        CancelTicketUseCase,
        Depends(get_cancel_ticket_use_case),
    ],
) -> dict[str, bool]:
    try:
        await use_case.execute(ticket_id)
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EventNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TicketAlreadyCancelledError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except EventAlreadyStartedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail="External events provider is unavailable",
        ) from exc

    return {"success": True}
