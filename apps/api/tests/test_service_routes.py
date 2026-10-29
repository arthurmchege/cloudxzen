import asyncio

import httpx

from app.main import app


def test_create_service_rejects_blank_name() -> None:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/services",
                json={"name": "   ", "environment": "production"},
            )

    response = asyncio.run(request())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
