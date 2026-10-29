import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import ErrorResponse
from app.db.session import get_db
from app.domains.services.models import EventType
from app.domains.services.repository import (
    create_service,
    create_service_event,
    get_service,
    get_service_event,
    list_service_events,
    list_services,
    resolve_service_event,
)
from app.domains.services.schemas import (
    ServiceCreate,
    ServiceEventCreate,
    ServiceEventResponse,
    ServiceResponse,
)
from app.domains.services.status import derive_service_status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/services", tags=["services"])


def _service_response(service) -> ServiceResponse:
    response = ServiceResponse.model_validate(service)
    return response.model_copy(update={"status": derive_service_status(service.events)})


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
)
def create_service_endpoint(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    try:
        service = create_service(db, payload)
        db.commit()
        db.refresh(service)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("service_creation_failed")
        raise

    return _service_response(service)


@router.get("", response_model=list[ServiceResponse], responses={422: {"model": ErrorResponse}})
def list_services_endpoint(db: Session = Depends(get_db)) -> list[ServiceResponse]:
    return [_service_response(service) for service in list_services(db)]


@router.post(
    "/{service_id}/events",
    response_model=ServiceEventResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_service_event_endpoint(
    service_id: UUID,
    payload: ServiceEventCreate,
    db: Session = Depends(get_db),
) -> ServiceEventResponse:
    if get_service(db, service_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    try:
        event = create_service_event(db, service_id, payload)
        db.commit()
        db.refresh(event)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("service_event_creation_failed")
        raise

    return event


@router.get(
    "/{service_id}/events",
    response_model=list[ServiceEventResponse],
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def list_service_events_endpoint(
    service_id: UUID,
    db: Session = Depends(get_db),
) -> list[ServiceEventResponse]:
    if get_service(db, service_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    return list_service_events(db, service_id)


@router.post(
    "/{service_id}/events/{event_id}/resolve",
    response_model=ServiceEventResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def resolve_service_event_endpoint(
    service_id: UUID,
    event_id: UUID,
    db: Session = Depends(get_db),
) -> ServiceEventResponse:
    if get_service(db, service_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    event = get_service_event(db, service_id, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.event_type != EventType.INCIDENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only incident events can be resolved",
        )
    if event.resolved_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incident is already resolved",
        )

    try:
        event = resolve_service_event(db, event, datetime.now(UTC))
        db.commit()
        db.refresh(event)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("service_event_resolution_failed")
        raise

    return event
