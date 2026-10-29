import asyncio
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes import services as services_routes
from app.api.routes.services import get_db
from app.db.base import Base
from app.domains.services.models import ServiceEvent
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


@pytest.fixture
def api_client() -> Iterator[httpx.AsyncClient]:
    if not TEST_DATABASE_URL or TEST_DATABASE_URL == DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL must be separate from DATABASE_URL")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)

    def override_get_db() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    try:
        yield client
    finally:
        asyncio.run(client.aclose())
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_create_and_list_services(api_client: httpx.AsyncClient) -> None:
    async def request() -> tuple[httpx.Response, httpx.Response]:
        created = await api_client.post(
            "/services",
            json={
                "name": "Payments",
                "description": "Payment processing",
                "environment": "production",
            },
        )
        listed = await api_client.get("/services")
        return created, listed

    created, listed = asyncio.run(request())

    assert created.status_code == 201
    assert created.json()["name"] == "Payments"
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == created.json()["id"]


def test_list_services_returns_empty_array(api_client: httpx.AsyncClient) -> None:
    async def request() -> httpx.Response:
        return await api_client.get("/services")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == []


def test_list_services_uses_deterministic_order(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        await api_client.post(
            "/services",
            json={"name": "Search", "environment": "production"},
        )
        return await api_client.get("/services")

    response = asyncio.run(request())
    services = response.json()
    ordering = [
        (datetime.fromisoformat(service["created_at"]), service["id"])
        for service in services
    ]

    assert response.status_code == 200
    assert ordering == sorted(ordering, reverse=True)


def test_create_check_event(api_client: httpx.AsyncClient) -> None:
    async def request() -> tuple[httpx.Response, str]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "check",
                "status": "operational",
                "summary": "Health check passed",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        return event_response, service_id

    response, service_id = asyncio.run(request())
    body = response.json()

    assert response.status_code == 201
    assert body["service_id"] == service_id
    assert body["event_type"] == "check"
    assert body["status"] == "operational"
    assert body["summary"] == "Health check passed"
    assert body["resolved_at"] is None


def test_create_incident_event_persists_event(api_client: httpx.AsyncClient) -> None:
    async def request() -> tuple[httpx.Response, str]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Search", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Search unavailable",
                "details": "HTTP 503 responses",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        return event_response, service_id

    response, service_id = asyncio.run(request())
    event_id = response.json()["id"]

    engine = create_engine(TEST_DATABASE_URL)
    with Session(engine) as session:
        stored = session.scalar(
            select(ServiceEvent).where(
                ServiceEvent.id == event_id,
                ServiceEvent.service_id == service_id,
            )
        )
    engine.dispose()

    assert response.status_code == 201
    assert stored is not None
    assert stored.event_type == "incident"
    assert stored.status == "down"


def test_create_event_rejects_invalid_request(api_client: httpx.AsyncClient) -> None:
    async def request() -> httpx.Response:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        return await api_client.post(
            f"/services/{service_response.json()['id']}/events",
            json={
                "event_type": "incident",
                "status": "operational",
                "summary": "Invalid incident",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )

    response = asyncio.run(request())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_create_event_returns_not_found_for_missing_service(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        return await api_client.post(
            f"/services/{uuid4()}/events",
            json={
                "event_type": "check",
                "status": "operational",
                "summary": "Health check passed",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )

    response = asyncio.run(request())

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_list_service_events_returns_empty_array_for_new_service(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        return await api_client.get(f"/services/{service_response.json()['id']}/events")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == []


def test_list_service_events_returns_newest_first_and_scoped_history(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> tuple[httpx.Response, str, str]:
        first_service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        first_service_id = first_service_response.json()["id"]
        second_service_response = await api_client.post(
            "/services",
            json={"name": "Search", "environment": "production"},
        )
        second_service_id = second_service_response.json()["id"]

        older_response = await api_client.post(
            f"/services/{first_service_id}/events",
            json={
                "event_type": "check",
                "status": "degraded",
                "summary": "High latency",
                "occurred_at": "2026-10-29T17:00:00+00:00",
            },
        )
        newer_response = await api_client.post(
            f"/services/{first_service_id}/events",
            json={
                "event_type": "check",
                "status": "operational",
                "summary": "Latency recovered",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        await api_client.post(
            f"/services/{second_service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Search unavailable",
                "occurred_at": "2026-10-29T19:00:00+00:00",
            },
        )
        history_response = await api_client.get(
            f"/services/{first_service_id}/events"
        )
        return history_response, older_response.json()["id"], newer_response.json()["id"]

    response, older_id, newer_id = asyncio.run(request())
    events = response.json()

    assert response.status_code == 200
    assert [event["id"] for event in events] == [newer_id, older_id]
    assert [event["summary"] for event in events] == [
        "Latency recovered",
        "High latency",
    ]
    assert all(event["event_type"] == "check" for event in events)


def test_list_service_events_returns_not_found_for_missing_service(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        return await api_client.get(f"/services/{uuid4()}/events")

    response = asyncio.run(request())

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_resolve_incident_sets_server_generated_timestamp(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> tuple[httpx.Response, datetime, datetime]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Payments unavailable",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        event_id = event_response.json()["id"]
        before = datetime.now(UTC)
        resolved_response = await api_client.post(
            f"/services/{service_id}/events/{event_id}/resolve"
        )
        after = datetime.now(UTC)
        return resolved_response, before, after

    response, before, after = asyncio.run(request())
    resolved_at = datetime.fromisoformat(response.json()["resolved_at"])

    assert response.status_code == 200
    assert resolved_at.tzinfo is not None
    assert before <= resolved_at <= after
    assert response.json()["event_type"] == "incident"
    assert response.json()["status"] == "down"


def test_resolve_incident_persists_timestamp(api_client: httpx.AsyncClient) -> None:
    async def request() -> tuple[httpx.Response, str, str]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Search", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "incident",
                "status": "degraded",
                "summary": "Search degraded",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        event_id = event_response.json()["id"]
        resolved_response = await api_client.post(
            f"/services/{service_id}/events/{event_id}/resolve"
        )
        return resolved_response, service_id, event_id

    response, service_id, event_id = asyncio.run(request())
    engine = create_engine(TEST_DATABASE_URL)
    with Session(engine) as session:
        stored = session.scalar(
            select(ServiceEvent).where(
                ServiceEvent.id == event_id,
                ServiceEvent.service_id == service_id,
            )
        )
    engine.dispose()

    assert response.status_code == 200
    assert stored is not None
    assert stored.resolved_at is not None
    assert stored.resolved_at.tzinfo is not None


def test_resolve_event_returns_not_found_for_missing_service(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        return await api_client.post(
            f"/services/{uuid4()}/events/{uuid4()}/resolve"
        )

    response = asyncio.run(request())

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_resolve_event_returns_not_found_for_missing_event(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> httpx.Response:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        return await api_client.post(
            f"/services/{service_response.json()['id']}/events/{uuid4()}/resolve"
        )

    response = asyncio.run(request())

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_resolve_event_is_scoped_to_service(api_client: httpx.AsyncClient) -> None:
    async def request() -> httpx.Response:
        first_service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        second_service_response = await api_client.post(
            "/services",
            json={"name": "Search", "environment": "production"},
        )
        first_service_id = first_service_response.json()["id"]
        second_service_id = second_service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{first_service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Payments unavailable",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        return await api_client.post(
            f"/services/{second_service_id}/events/"
            f"{event_response.json()['id']}/resolve"
        )

    response = asyncio.run(request())

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_resolve_check_returns_conflict(api_client: httpx.AsyncClient) -> None:
    async def request() -> httpx.Response:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "check",
                "status": "operational",
                "summary": "Health check passed",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        return await api_client.post(
            f"/services/{service_id}/events/"
            f"{event_response.json()['id']}/resolve"
        )

    response = asyncio.run(request())

    assert response.status_code == 409
    assert response.json()["detail"] == "Only incident events can be resolved"


def test_resolve_already_resolved_incident_returns_conflict(
    api_client: httpx.AsyncClient,
) -> None:
    async def request() -> tuple[httpx.Response, httpx.Response]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Payments unavailable",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        event_id = event_response.json()["id"]
        first_resolution = await api_client.post(
            f"/services/{service_id}/events/{event_id}/resolve"
        )
        second_resolution = await api_client.post(
            f"/services/{service_id}/events/{event_id}/resolve"
        )
        return first_resolution, second_resolution

    first_response, second_response = asyncio.run(request())

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Incident is already resolved"


def test_resolve_database_error_returns_generic_error_and_rolls_back(
    api_client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def request() -> tuple[httpx.Response, str]:
        service_response = await api_client.post(
            "/services",
            json={"name": "Payments", "environment": "production"},
        )
        service_id = service_response.json()["id"]
        event_response = await api_client.post(
            f"/services/{service_id}/events",
            json={
                "event_type": "incident",
                "status": "down",
                "summary": "Payments unavailable",
                "occurred_at": "2026-10-29T18:00:00+00:00",
            },
        )
        return (
            await api_client.post(
                f"/services/{service_id}/events/"
                f"{event_response.json()['id']}/resolve"
            ),
            event_response.json()["id"],
        )

    def fail_resolution(*args: object, **kwargs: object) -> None:
        raise SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(services_routes, "resolve_service_event", fail_resolution)
    response, event_id = asyncio.run(request())

    engine = create_engine(TEST_DATABASE_URL)
    with Session(engine) as session:
        stored = session.get(ServiceEvent, event_id)
    engine.dispose()

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "database_error",
            "message": "The request could not be completed.",
        }
    }
    assert stored is not None
    assert stored.resolved_at is None
