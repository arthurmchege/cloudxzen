import asyncio
import os
from collections.abc import Iterator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.routes.services import get_db
from app.db.base import Base
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
