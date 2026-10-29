# CloudXzen Milestone 5 Report

## Milestone Overview

Milestone 5, **Backend API Hardening and Documentation**, strengthens the
FastAPI backend's contracts, production configuration, migration verification,
and failure-path documentation without expanding the product architecture.

The milestone objectives were to:

- standardize structured HTTP error responses;
- document success and failure responses in OpenAPI;
- restrict interactive API documentation in production;
- verify request correlation and database failure behavior;
- verify Alembic migrations against the dedicated PostgreSQL test database;
- document compatibility decisions for the current unversioned API routes.

## Scope and Requirements

In scope:

- structured validation, not-found, conflict, and database-error responses;
- generated OpenAPI response schemas;
- production documentation endpoint restrictions;
- focused failure-path and configuration tests;
- migration upgrade verification;
- API README, roadmap, and milestone reporting.

Out of scope:

- authentication, authorization, ownership, or multi-user behavior;
- pagination or filtering;
- Redis, queues, background workers, or cloud resources;
- paid services;
- frontend implementation;
- changing the current root `/services` routes to `/api/v1`;
- enforcing a new request-ID format without a defined compatibility
  requirement.

The modular-monolith Python/FastAPI/PostgreSQL architecture and KSh 0 cost
target are preserved.

## Implementation

### Structured API errors

- Added centralized `HTTPException` handling.
- `404` responses use `not_found`.
- `409` responses use `conflict`.
- Validation failures continue to use `validation_error`.
- SQLAlchemy failures use `database_error` with a generic client message.
- Added the reusable `ErrorResponse` Pydantic schema.

### Production documentation restrictions

- Added `create_app(settings)` to make runtime configuration explicit and
  directly testable.
- `/docs`, `/redoc`, and `/openapi.json` remain available outside production.
- All three documentation endpoints are disabled when
  `ENVIRONMENT=production`.

### Migration verification

- Added a PostgreSQL integration test that runs Alembic from `base` to `head`
  against `TEST_DATABASE_URL`.
- The test verifies `services`, `service_events`, and `alembic_version`.
- The test downgrades the dedicated test database back to `base` during
  cleanup.
- The test refuses to use `DATABASE_URL` for destructive setup.

### Files changed

- `apps/api/app/core/errors.py`
- `apps/api/app/main.py`
- `apps/api/app/api/routes/services.py`
- `apps/api/app/alembic/env.py`
- `apps/api/alembic.ini`
- `apps/api/tests/test_health.py`
- `apps/api/tests/integration/test_postgres.py`
- `apps/api/tests/integration/test_services_api.py`
- `apps/api/README.md`
- `docs/CLOUDXZEN_ROADMAP.md`
- `docs/MILESTONE_5_REPORT.md`

The first hardening checkpoint is recorded in commit `b859ebf`; the migration,
production-configuration, and final verification checkpoint is recorded in
commit `3e70216`.

## Architecture and Technical Decisions

### Centralized error handling

Route handlers continue to raise normal FastAPI `HTTPException` instances.
The application-level handler converts them to the same structured envelope
used by validation and database failures. This avoids duplicating response
construction in each route while preserving existing status codes.

### Application factory

The application factory accepts a `Settings` instance for deterministic
configuration tests. The production restriction is applied when the
application is constructed, rather than at request time. This keeps runtime
behavior simple and makes the security-sensitive configuration directly
testable.

### Migration test isolation

The migration test uses the existing guarded `TEST_DATABASE_URL` convention.
It does not add a separate database service, test framework, or dependency.
The test performs destructive setup only on the explicitly dedicated test
database and restores it to the base revision after verification.

### Deferred API versioning

The roadmap and specification describe `/api/v1`, while the implemented
Milestone 4 and 5 contract uses root `/services` paths. Introducing aliases or
moving routes now would create an undocumented compatibility surface before a
frontend client requires it. `/api/v1` remains an explicit decision for a
future API contract checkpoint.

### Deferred request-ID validation

The existing behavior accepts and returns a caller-provided `X-Request-ID` or
generates a UUID when absent. No maximum length, character policy, or
downstream tracing requirement has been established. Enforcing a new format
now would be a compatibility change without evidence of a current defect.

## API and Documentation Changes

The API README now documents:

- structured `validation_error`, `not_found`, `conflict`, and
  `database_error` responses;
- production disabling of Swagger UI, ReDoc, and OpenAPI JSON;
- migration verification against the dedicated test database.

Service route OpenAPI metadata now declares relevant `404`, `409`, `422`, and
`500` responses using `ErrorResponse`. Successful response schemas and status
codes remain unchanged.

The current product routes remain:

```text
POST /services
GET /services
POST /services/{service_id}/events
GET /services/{service_id}/events
POST /services/{service_id}/events/{event_id}/resolve
```

`GET /health` remains outside any product API namespace as an infrastructure
health check.

## Testing and Verification

The final verified backend suite was run from `apps/api` with the documented
environment loading and locked dependencies:

```bash
set -a && . ../../.env && set +a
.venv/bin/uv run --locked pytest
```

Result: **54 passed**.

Additional verified checks:

```text
Focused production documentation tests: 4 passed
Focused Alembic migration test: 1 passed
Ruff: passed
Python compilation: passed
uv lock --check: passed
git diff --check: passed
OpenAPI database-error schema inspection: passed
```

The suite includes API failure contracts, simulated database failure and
rollback behavior, production documentation restrictions, PostgreSQL
persistence, and Alembic upgrade verification.

## Git Checkpoints

| Commit | Description | Remote status |
|---|---|---|
| `b859ebf` | Harden error contracts and documentation | Pushed to `origin/main` |
| `3e70216` | Verify production docs and migrations | Pushed to `origin/main` |

The current verified branch is `main`. At report creation time, local `HEAD`
and `origin/main` both point to `3e70216f5d3fbffa1a9454a7fa1ebcc8d121fecf`.

## Outstanding Issues

- `/api/v1` compatibility strategy is deferred. The current root route
  contract must not be changed implicitly.
- Request-ID format and length validation are deferred until an operational or
  client contract requires them.
- Frontend implementation has not started.
- CI, Docker reproducibility, deployment, infrastructure-as-code, expanded
  observability, and production readiness remain later roadmap work.
- Authentication and ownership remain intentionally out of scope.

## Completion Assessment

**Status: Complete for the defined Milestone 5 scope.**

Evidence:

- structured API errors are implemented and covered;
- relevant success and failure responses are present in OpenAPI;
- production documentation restrictions are implemented and tested;
- Alembic migration execution is verified against the dedicated PostgreSQL
  test database;
- the complete backend suite reports 54 passing tests;
- lint, compilation, lock, and diff checks pass;
- commits `b859ebf` and `3e70216` are present and pushed;
- no required Milestone 5 item remains unverified.

The deferred `/api/v1` and request-ID decisions are explicitly outside the
acceptance criteria for this milestone.

## Next Milestone

The roadmap identifies Milestone 6 as **Frontend foundation**.

Expected outcomes:

- bootstrap the Next.js application;
- establish TypeScript and Tailwind configuration;
- add the initial application shell and justified accessible UI primitives;
- establish frontend lint, type-check, and test commands;
- preserve the existing backend API contract while the frontend is built.

Prerequisites:

- the verified backend API and documented root routes;
- the existing environment-variable and local development documentation;
- a frontend dependency and toolchain decision consistent with the project
  specification and KSh 0 cost target.

Acceptance criteria should include a booting Next.js app, passing frontend
lint/type-check/test commands, documented local setup, and no regression in
the backend verification suite.

Proposed stages:

1. create the frontend workspace and dependency manifest;
2. configure TypeScript, Next.js App Router, and Tailwind;
3. add the accessible app shell and minimal UI primitives;
4. add frontend quality commands and focused tests;
5. update frontend setup documentation and create a milestone checkpoint.

The next milestone is not implemented by this report.
