# CloudXzen Milestone 2 Report

## Status

**Implemented:** dependency locking, PostgreSQL domain models, initial Alembic
migration, Docker Compose configuration, status derivation, and guarded
integration-test structure.

**Not verified:** applying the migration or running integration tests against a
live database. Native PostgreSQL administrator access is unavailable
non-interactively, and Docker containers were not started because the approval
requires separate authorization before starting them.

## Implemented

- Added `uv.lock` while preserving Python 3.14 and the existing dependency groups.
- Added `services` and `service_events` SQLAlchemy models with UUID keys,
  timezone-aware timestamps, foreign-key cascading, validation constraints, and
  an event history index.
- Defined status derivation: unresolved incidents take precedence, otherwise
  the latest check is authoritative; resolved-only incidents imply operational;
  no events imply unknown.
- Added the initial Alembic migration and wired Alembic to `DATABASE_URL` from
  application settings.
- Added a PostgreSQL 18 Compose service named `db`, loopback-only configurable
  port, persistent named volume, credentials from environment, and readiness
  health check.
- Added unit tests for status rules and guarded PostgreSQL integration tests
  using a separate `TEST_DATABASE_URL`.
- Updated setup, migration, testing, and dual-environment documentation.

## Verification

| Check | Result |
|---|---|
| `uv lock --check` | PASS |
| `uv sync --extra test --extra dev` | PASS |
| `uv run ruff check app tests` | PASS |
| `uv run pytest` | PASS: 5 passed, 2 skipped |
| `uv run alembic heads/history` | PASS |
| `uv run alembic upgrade head --sql` | PASS: expected PostgreSQL DDL generated |
| `docker compose config` | PASS; no service started |
| Native PostgreSQL migration | NOT VERIFIED: dedicated credentials unavailable |
| Docker PostgreSQL migration | NOT VERIFIED: container start authorization not provided |

## Schema decisions

Service names are not globally unique because ownership does not exist yet.
Check events may use operational, degraded, or down status. Incident events
must use degraded or down status and may be unresolved or resolved. Check events
cannot have a resolution timestamp, and resolutions cannot precede occurrence.

## Remaining work

1. Provision a dedicated least-privilege native `cloudxzen` role and separate
   `cloudxzen_test` database, or authorize starting the local Compose database.
2. Set `DATABASE_URL` and `TEST_DATABASE_URL` with local credentials.
3. Apply the migration and run integration tests against PostgreSQL 18.
4. Inspect the resulting schema and constraints before beginning Milestone 3.
