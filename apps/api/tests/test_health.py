import asyncio

import httpx

from app.core.config import Settings
from app.main import app, create_app


def test_health_returns_ok() -> None:
    async def request_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/health")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_request_id() -> None:
    async def request_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/health", headers={"X-Request-ID": "test-request"})

    response = asyncio.run(request_health())

    assert response.headers["X-Request-ID"] == "test-request"


def test_openapi_is_available_outside_production() -> None:
    async def request_openapi() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/openapi.json")

    response = asyncio.run(request_openapi())

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "CloudXzen API"


def test_production_disables_documentation_endpoints() -> None:
    production_app = create_app(
        Settings(
            environment="production",
            database_url="postgresql+psycopg://unused:unused@localhost/unused",
        )
    )

    async def request_documentation() -> tuple[httpx.Response, httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=production_app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return (
                await client.get("/docs"),
                await client.get("/redoc"),
                await client.get("/openapi.json"),
            )

    docs_response, redoc_response, openapi_response = asyncio.run(request_documentation())

    assert docs_response.status_code == 404
    assert redoc_response.status_code == 404
    assert openapi_response.status_code == 404
