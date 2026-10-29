import os
from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.domains.services.models import Service, ServiceEvent
from app.domains.services.repository import create_service, list_services
from app.domains.services.schemas import ServiceCreate

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


@pytest.fixture
def db_session() -> Iterator[Session]:
    if not TEST_DATABASE_URL or TEST_DATABASE_URL == DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL must be separate from DATABASE_URL")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_service_and_event_persist_with_relationship(db_session: Session) -> None:
    service = Service(name="Payments", environment="production")
    service.events.append(
        ServiceEvent(
            event_type="check",
            status="operational",
            summary="Healthy",
            occurred_at=datetime.now(UTC),
        )
    )
    db_session.add(service)
    db_session.commit()

    stored = db_session.scalar(select(Service).where(Service.id == service.id))

    assert stored is not None
    assert len(stored.events) == 1
    assert stored.events[0].service_id == service.id


def test_foreign_key_rejects_missing_service(db_session: Session) -> None:
    event = ServiceEvent(
        id=uuid4(),
        service_id=uuid4(),
        event_type="check",
        status="operational",
        summary="Orphan",
        occurred_at=datetime.now(UTC),
    )
    db_session.add(event)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_repository_creates_and_lists_services(db_session: Session) -> None:
    created = create_service(
        db_session,
        ServiceCreate(name="Payments", environment="production"),
    )
    db_session.commit()

    services = list_services(db_session)

    assert services == [created]
    assert services[0].name == "Payments"
