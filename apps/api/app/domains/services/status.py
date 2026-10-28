from collections.abc import Iterable

from app.domains.services.models import ServiceEvent, ServiceStatus


def derive_service_status(events: Iterable[ServiceEvent]) -> ServiceStatus:
    """Derive status from active incidents and the latest relevant history.

    Unresolved incidents take precedence. Once all incidents are resolved, the
    latest check is authoritative. A service with only resolved incidents is
    considered operational because resolution represents recovery. A service
    without events has unknown status.
    """

    ordered_events = sorted(
        events,
        key=lambda event: (event.occurred_at, event.created_at, event.id),
        reverse=True,
    )

    for event in ordered_events:
        if event.event_type == "incident" and event.resolved_at is None:
            return ServiceStatus(event.status)

    for event in ordered_events:
        if event.event_type == "check":
            return ServiceStatus(event.status)

    if any(event.event_type == "incident" for event in ordered_events):
        return ServiceStatus.OPERATIONAL

    return ServiceStatus.UNKNOWN
