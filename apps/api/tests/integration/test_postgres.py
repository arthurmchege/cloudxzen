import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from app.db.base import Base
from app.domains.services.models import Service, ServiceEvent
from app.domains.services.repository import (
    create_service,
    create_service_event,
    get_service_event,
    list_service_events,
    list_services,
)
from app.domains.services.schemas import ServiceCreate, ServiceEventCreate

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_alembic_upgrade_creates_current_schema() -> None:
    if not TEST_DATABASE_URL or TEST_DATABASE_URL == DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL must be separate from DATABASE_URL")

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL.replace("%", "%%"))
    command.downgrade(config, "base")
    try:
        command.upgrade(config, "head")

        engine = create_engine(TEST_DATABASE_URL)
        with engine.connect() as connection:
            table_names = set(
                connection.exec_driver_sql(
                    "SELECT tablename FROM pg_catalog.pg_tables "
                    "WHERE schemaname = 'public'"
                ).scalars()
            )
        engine.dispose()

        assert {"services", "service_events", "alembic_version"} <= table_names
    finally:
        command.downgrade(config, "base")


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


def test_repository_creates_and_retrieves_service_event(db_session: Session) -> None:
    service = Service(name="Payments", environment="production")
    db_session.add(service)
    db_session.flush()
    data = ServiceEventCreate(
        event_type="incident",
        status="down",
        summary="Payments unavailable",
        occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
    )

    created = create_service_event(db_session, service.id, data)
    retrieved = get_service_event(db_session, service.id, created.id)

    assert retrieved is created
    assert retrieved.service_id == service.id


def test_repository_lists_service_events_newest_first(db_session: Session) -> None:
    service = Service(name="Payments", environment="production")
    db_session.add(service)
    db_session.flush()
    older = create_service_event(
        db_session,
        service.id,
        ServiceEventCreate(
            event_type="check",
            status="degraded",
            summary="High latency",
            occurred_at=datetime(2026, 10, 29, 17, 0, tzinfo=UTC),
        ),
    )
    newer = create_service_event(
        db_session,
        service.id,
        ServiceEventCreate(
            event_type="check",
            status="operational",
            summary="Latency recovered",
            occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
        ),
    )

    events = list_service_events(db_session, service.id)

    assert [event.id for event in events] == [newer.id, older.id]


def test_repository_lists_empty_history_for_service_without_events(
    db_session: Session,
) -> None:
    service = Service(name="Search", environment="production")
    db_session.add(service)
    db_session.flush()

    assert list_service_events(db_session, service.id) == []


def test_repository_scopes_event_lookup_to_service(db_session: Session) -> None:
    first_service = Service(name="Payments", environment="production")
    second_service = Service(name="Search", environment="production")
    db_session.add_all([first_service, second_service])
    db_session.flush()
    event = create_service_event(
        db_session,
        first_service.id,
        ServiceEventCreate(
            event_type="check",
            status="operational",
            summary="Healthy",
            occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
        ),
    )

    assert get_service_event(db_session, second_service.id, event.id) is None
    assert get_service_event(db_session, first_service.id, uuid4()) is None


def test_repository_rejects_event_for_missing_service(db_session: Session) -> None:
    with pytest.raises(IntegrityError):
        create_service_event(
            db_session,
            uuid4(),
            ServiceEventCreate(
                event_type="check",
                status="operational",
                summary="Orphan event",
                occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
            ),
        )

    db_session.rollback()


def test_repository_creation_does_not_commit(db_session: Session) -> None:
    service = Service(name="Payments", environment="production")
    db_session.add(service)
    db_session.flush()
    event = create_service_event(
        db_session,
        service.id,
        ServiceEventCreate(
            event_type="check",
            status="operational",
            summary="Healthy",
            occurred_at=datetime(2026, 10, 29, 18, 0, tzinfo=UTC),
        ),
    )

    db_session.rollback()

    assert db_session.get(ServiceEvent, event.id) is None
