import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.services.repository import create_service, list_services
from app.domains.services.schemas import ServiceCreate, ServiceResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
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

    return service


@router.get("", response_model=list[ServiceResponse])
def list_services_endpoint(db: Session = Depends(get_db)) -> list[ServiceResponse]:
    return list_services(db)
