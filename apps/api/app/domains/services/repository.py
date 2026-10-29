from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domains.services.models import Service, ServiceEvent
from app.domains.services.schemas import ServiceCreate, ServiceEventCreate


def create_service(session: Session, data: ServiceCreate) -> Service:
    service = Service(
        name=data.name,
        description=data.description,
        environment=data.environment,
    )
    session.add(service)
    session.flush()
    return service


def list_services(session: Session) -> list[Service]:
    statement = (
        select(Service)
        .options(selectinload(Service.events))
        .order_by(Service.created_at.desc(), Service.id.desc())
    )
    return list(session.scalars(statement))


def get_service(session: Session, service_id: UUID) -> Service | None:
    return session.get(Service, service_id)


def create_service_event(
    session: Session,
    service_id: UUID,
    data: ServiceEventCreate,
) -> ServiceEvent:
    event = ServiceEvent(
        service_id=service_id,
        event_type=data.event_type,
        status=data.status,
        summary=data.summary,
        details=data.details,
        occurred_at=data.occurred_at,
    )
    session.add(event)
    session.flush()
    return event


def list_service_events(session: Session, service_id: UUID) -> list[ServiceEvent]:
    statement = (
        select(ServiceEvent)
        .where(ServiceEvent.service_id == service_id)
        .order_by(
            ServiceEvent.occurred_at.desc(),
            ServiceEvent.created_at.desc(),
            ServiceEvent.id.desc(),
        )
    )
    return list(session.scalars(statement))


def get_service_event(
    session: Session,
    service_id: UUID,
    event_id: UUID,
) -> ServiceEvent | None:
    statement = select(ServiceEvent).where(
        ServiceEvent.service_id == service_id,
        ServiceEvent.id == event_id,
    )
    return session.scalar(statement)


def resolve_service_event(
    session: Session,
    event: ServiceEvent,
    resolved_at: datetime,
) -> ServiceEvent:
    event.resolved_at = resolved_at
    session.flush()
    return event
