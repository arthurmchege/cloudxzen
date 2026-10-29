import asyncio

import httpx

from app.main import app


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
