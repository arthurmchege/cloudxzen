# CloudXzen API

## Status

The API foundation is implemented. Domain routes and database tables are intentionally deferred to later milestones.

## Requirements

- Python 3.14
- PostgreSQL is not required to run the health endpoint or its test.

## Setup

From `apps/api`:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test,dev]"
```

The repository root `.env.example` documents the currently supported environment variables. Copy it to `.env` only for local use; `.env` is ignored by Git.

## Configuration

| Variable | Required | Purpose |
|---|---:|---|
| `ENVIRONMENT` | No | `development`, `test`, or `production`; defaults to `development`. |
| `DATABASE_URL` | No | SQLAlchemy PostgreSQL URL used by the database foundation; defaults to a fake local development URL. |

The health endpoint does not connect to PostgreSQL yet. The default database URL is a local placeholder for the future database foundation, not a credential.

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

`/health` is intentionally outside `/api/v1` because it is an infrastructure/process health check. It does not check PostgreSQL or other external dependencies. Future product routes will use the `/api/v1` namespace.

## OpenAPI documentation

When running in development, FastAPI exposes:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Tests

From `apps/api`, with the virtual environment active:

```bash
pytest
```

The health test uses an in-process `httpx.AsyncClient` with `httpx.ASGITransport`; it does not require PostgreSQL, cloud services, or internet access.

To run the configured linter:

```bash
ruff check app tests
```

## Database foundation

SQLAlchemy session and declarative-base modules are prepared for future domain work. Alembic is initialized without a migration because no CloudXzen domain tables exist yet. Domain models and migrations belong to the next database milestone.
