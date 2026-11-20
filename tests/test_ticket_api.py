from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_cancel_ticket_use_case,
    get_register_ticket_use_case,
)
from app.application.usecases.cancel_ticket import (
    EventAlreadyStartedError,
    TicketAlreadyCancelledError,
    TicketNotFoundError,
)
from app.application.usecases.cancel_ticket import (
    EventNotFoundError as CancelEventNotFoundError,
)
from app.application.usecases.register_ticket import (
    EventNotFoundError as RegistrationEventNotFoundError,
)
from app.application.usecases.register_ticket import (
    EventNotPublishedError,
    RegistrationDeadlinePassedError,
    SeatUnavailableError,
)
from app.infrastructure.clients.external_api_client import ExternalAPIError
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def register_mock():
    use_case = AsyncMock()
    app.dependency_overrides[get_register_ticket_use_case] = lambda: use_case
    return use_case


@pytest.fixture
def cancel_mock():
    use_case = AsyncMock()
    app.dependency_overrides[get_cancel_ticket_use_case] = lambda: use_case
    return use_case


@pytest.fixture
def ticket_payload():
    return {
        "event_id": str(uuid4()),
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivan@example.com",
        "seat": "A1",
    }


# Registration API


def test_register_ticket_success(client, register_mock, ticket_payload):
    ticket_id = uuid4()
    register_mock.execute.return_value = ticket_id

    response = client.post("/api/tickets", json=ticket_payload)

    assert response.status_code == 201
    assert response.json() == {"ticket_id": str(ticket_id)}
    register_mock.execute.assert_awaited_once()


def test_register_ticket_invalid_email(
    client,
    register_mock,
    ticket_payload,
):
    ticket_payload["email"] = "invalid-email"

    response = client.post("/api/tickets", json=ticket_payload)

    assert response.status_code == 400
    register_mock.execute.assert_not_awaited()


def test_register_ticket_empty_name(
    client,
    register_mock,
    ticket_payload,
):
    ticket_payload["first_name"] = ""

    response = client.post("/api/tickets", json=ticket_payload)

    assert response.status_code == 400
    register_mock.execute.assert_not_awaited()


def test_register_ticket_invalid_event_id(
    client,
    register_mock,
    ticket_payload,
):
    ticket_payload["event_id"] = "not-a-uuid"

    response = client.post("/api/tickets", json=ticket_payload)

    assert response.status_code == 400
    register_mock.execute.assert_not_awaited()


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (RegistrationEventNotFoundError("Event not found"), 404),
        (EventNotPublishedError("Event is not published"), 409),
        (
            RegistrationDeadlinePassedError("Deadline passed"),
            409,
        ),
        (SeatUnavailableError("Seat unavailable"), 409),
        (ExternalAPIError("Provider error"), 502),
    ],
)
def test_register_ticket_errors(
    client,
    register_mock,
    ticket_payload,
    exception,
    expected_status,
):
    register_mock.execute.side_effect = exception

    response = client.post("/api/tickets", json=ticket_payload)

    assert response.status_code == expected_status


# Cancellation API


def test_cancel_ticket_success(client, cancel_mock):
    ticket_id = uuid4()

    response = client.delete(f"/api/tickets/{ticket_id}")

    assert response.status_code == 200
    assert response.json() == {"success": True}
    cancel_mock.execute.assert_awaited_once_with(ticket_id)


def test_cancel_ticket_invalid_id(client, cancel_mock):
    response = client.delete("/api/tickets/not-a-uuid")

    assert response.status_code == 422
    cancel_mock.execute.assert_not_awaited()


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (TicketNotFoundError("Ticket not found"), 404),
        (CancelEventNotFoundError("Event not found"), 404),
        (
            TicketAlreadyCancelledError("Already cancelled"),
            409,
        ),
        (
            EventAlreadyStartedError("Event already started"),
            409,
        ),
        (ExternalAPIError("Provider error"), 502),
    ],
)
def test_cancel_ticket_errors(
    client,
    cancel_mock,
    exception,
    expected_status,
):
    cancel_mock.execute.side_effect = exception
    ticket_id = uuid4()

    response = client.delete(f"/api/tickets/{ticket_id}")

    assert response.status_code == expected_status
