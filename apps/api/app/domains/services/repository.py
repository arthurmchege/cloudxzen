from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.services.models import Service
from app.domains.services.schemas import ServiceCreate


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
    statement = select(Service).order_by(Service.created_at.desc(), Service.id.desc())
    return list(session.scalars(statement))
