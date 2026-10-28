from datetime import UTC, datetime
from uuid import uuid4

from app.domains.services.models import ServiceEvent
from app.domains.services.status import derive_service_status


def event(event_type: str, status: str, *, resolved: bool = False) -> ServiceEvent:
    occurred_at = datetime(2026, 1, 1, tzinfo=UTC)
    return ServiceEvent(
        id=uuid4(),
        service_id=uuid4(),
        event_type=event_type,
        status=status,
        summary="status update",
        occurred_at=occurred_at,
        resolved_at=occurred_at if resolved else None,
    )


def test_service_without_events_is_unknown() -> None:
    assert derive_service_status([]).value == "unknown"


def test_unresolved_incident_takes_precedence_over_latest_check() -> None:
    assert derive_service_status(
        [event("check", "operational"), event("incident", "down")]
    ).value == "down"


def test_latest_check_is_used_when_incidents_are_resolved() -> None:
    assert derive_service_status(
        [event("incident", "down", resolved=True), event("check", "degraded")]
    ).value == "degraded"


def test_only_resolved_incidents_mean_operational() -> None:
    assert derive_service_status([event("incident", "down", resolved=True)]).value == (
        "operational"
    )
