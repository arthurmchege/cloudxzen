# CloudXzen API

## Status

The API foundation, initial service database schema, and first service HTTP
routes are implemented.

## Requirements

- Python 3.14
- PostgreSQL is not required to run the health endpoint or its test.

## Setup

From `apps/api`:

```bash
uv venv
uv sync --extra test --extra dev
```

The repository root `.env.example` documents the currently supported environment variables. Copy it to `.env` only for local use; `.env` is ignored by Git.

## Configuration

| Variable | Required | Purpose |
|---|---:|---|
| `ENVIRONMENT` | No | `development`, `test`, or `production`; defaults to `development`. |
| `DATABASE_URL` | No | SQLAlchemy PostgreSQL URL for the selected development database. |
| `TEST_DATABASE_URL` | No | Explicit PostgreSQL URL for destructive integration-test setup. Tests refuse to use `DATABASE_URL`. |

The health endpoint does not connect to PostgreSQL. Service routes use the
configured PostgreSQL database and require a working `DATABASE_URL`.

Validation failures use a structured `validation_error` response. Requests receive an `X-Request-ID` response header, and request completion/failure is logged with method, path, status, duration, and the request ID.

## Run locally

From `apps/api`, with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

## Health endpoint

```http
GET /health
```

Example response:

```json
{"status":"ok"}
```

`/health` is an infrastructure/process health check. It does not check
PostgreSQL or other external dependencies. The initial product routes use the
root `/services` paths defined below; introducing a versioned API namespace is
deferred until it is justified by the API contract.

## Service endpoints

The first product endpoints are available at the root service paths:

```http
POST /services
GET /services
```

Create a service:

```json
{
  "name": "Payments",
  "description": "Payment processing",
  "environment": "production"
}
```

`POST /services` returns `201 Created` with the created service. `GET
/services` returns a bare JSON array ordered by newest creation timestamp, with
the service ID as a deterministic tie-breaker. Authentication, ownership,
pagination, and service-event endpoints are outside this milestone.

## OpenAPI documentation

When running in development, FastAPI exposes:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Tests

From `apps/api`, with the virtual environment active:

```bash
uv run pytest
```

The health test uses an in-process `httpx.AsyncClient` with `httpx.ASGITransport`; it does not require PostgreSQL, cloud services, or internet access.

PostgreSQL integration tests are kept separate and require `TEST_DATABASE_URL`:

```bash
uv run pytest tests/integration
```

They refuse to run if `TEST_DATABASE_URL` is absent or matches `DATABASE_URL`.

To run the configured linter:

```bash
uv run ruff check app tests
```

## Database foundation

The initial `services` and `service_events` schema is represented by
`app.domains.services.models` and migration
`alembic/versions/20260301_0001_create_service_tables.py`. Both native
PostgreSQL and Docker PostgreSQL use the same models and migration:

```bash
uv run alembic upgrade head
```

Use the native or Docker URLs documented in
[`docs/POSTGRESQL_DEVELOPMENT.md`](../../docs/POSTGRESQL_DEVELOPMENT.md).
