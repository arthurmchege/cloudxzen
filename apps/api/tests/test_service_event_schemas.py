from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domains.services.models import EventType, ServiceEvent, ServiceEventStatus
from app.domains.services.schemas import ServiceEventCreate, ServiceEventResponse


def test_service_event_create_accepts_check() -> None:
    event = ServiceEventCreate(
        event_type=EventType.CHECK,
        status=ServiceEventStatus.OPERATIONAL,
        summary="Health check passed",
        occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
    )

    assert event.event_type is EventType.CHECK


def test_service_event_create_accepts_incident() -> None:
    event = ServiceEventCreate(
        event_type=EventType.INCIDENT,
        status=ServiceEventStatus.DOWN,
        summary="Payments unavailable",
        occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
    )

    assert event.status is ServiceEventStatus.DOWN


def test_service_event_create_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type=EventType.CHECK,
            status=ServiceEventStatus.OPERATIONAL,
        )


def test_service_event_create_rejects_blank_summary() -> None:
    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type=EventType.CHECK,
            status=ServiceEventStatus.OPERATIONAL,
            summary="   ",
            occurred_at=datetime(2026, 10, 29, tzinfo=UTC),
        )


def test_service_event_create_rejects_invalid_event_type_and_status() -> None:
    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type="maintenance",
            status="operational",
            summary="Maintenance",
            occurred_at=datetime(2026, 10, 29, tzinfo=UTC),
        )

    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type=EventType.CHECK,
            status="unknown",
            summary="Unknown state",
            occurred_at=datetime(2026, 10, 29, tzinfo=UTC),
        )


def test_service_event_create_rejects_operational_incident() -> None:
    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type=EventType.INCIDENT,
            status=ServiceEventStatus.OPERATIONAL,
            summary="Invalid incident",
            occurred_at=datetime(2026, 10, 29, tzinfo=UTC),
        )


def test_service_event_create_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        ServiceEventCreate(
            event_type=EventType.CHECK,
            status=ServiceEventStatus.OPERATIONAL,
            summary="Missing timezone",
            occurred_at=datetime(2026, 10, 29),
        )


def test_service_event_response_serializes_orm_model() -> None:
    occurred_at = datetime(2026, 10, 29, 18, 0, tzinfo=UTC)
    event = ServiceEvent(
        id=uuid4(),
        service_id=uuid4(),
        event_type=EventType.INCIDENT,
        status=ServiceEventStatus.DOWN,
        summary="Payments unavailable",
        details="HTTP 503 responses",
        occurred_at=occurred_at,
        resolved_at=None,
        created_at=occurred_at + timedelta(seconds=1),
    )

    response = ServiceEventResponse.model_validate(event)

    assert response.id == event.id
    assert response.event_type is EventType.INCIDENT
    assert response.created_at == event.created_at


def test_service_event_response_rejects_resolution_before_occurrence() -> None:
    occurred_at = datetime(2026, 10, 29, 18, 0, tzinfo=UTC)
    event = ServiceEvent(
        id=uuid4(),
        service_id=uuid4(),
        event_type=EventType.INCIDENT,
        status=ServiceEventStatus.DOWN,
        summary="Payments unavailable",
        occurred_at=occurred_at,
        resolved_at=occurred_at - timedelta(seconds=1),
        created_at=occurred_at,
    )

    with pytest.raises(ValidationError):
        ServiceEventResponse.model_validate(event)
