# CloudXzen Milestone 2 Report

## Status

**Milestone 2 status:** verified successfully for the native PostgreSQL 18
development path. Docker Compose support is implemented and its configuration
was validated, but the Docker database runtime was not started during this
verification.

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
| `uv run --locked ruff check .` | PASS |
| `uv run --locked python -m compileall -q app tests` | PASS |
| `uv run --locked pytest` with both local database URLs exported | PASS: 7 passed |
| `uv run --locked alembic heads` | PASS: `20260301_0001` |
| `uv run --locked alembic upgrade head` | PASS against native PostgreSQL 18 |
| Repeated `uv run --locked alembic upgrade head` | PASS; database remained at head |
| `uv run --locked alembic current` | PASS: `20260301_0001 (head)` |
| Native PostgreSQL readiness | PASS: `127.0.0.1:5432` accepting connections |
| Native PostgreSQL migration | PASS against dedicated `cloudxzen` database |
| PostgreSQL integration tests | PASS: 2 passed against separate `cloudxzen_test` database |
| Live schema inspection | PASS: both tables, one foreign key, six checks, and the event index present |
| `docker compose config --quiet` | PASS; no service started |
| Docker PostgreSQL migration | NOT VERIFIED: Docker database runtime was not started |

The local `.env` file contains the configured development and test URLs, is
ignored by Git, and was restricted to mode `600`. No credential values are
recorded in this report.

## Schema decisions

Service names are not globally unique because ownership does not exist yet.
Check events may use operational, degraded, or down status. Incident events
must use degraded or down status and may be unresolved or resolved. Check events
cannot have a resolution timestamp, and resolutions cannot precede occurrence.

## Remaining work

1. Optionally verify the same migration and integration tests against the Docker
   PostgreSQL 18 service on loopback port `5433`.
2. Review and approve the Milestone 2 checkpoint before beginning Milestone 3.

Milestone 3 remains out of scope for this report. No service API endpoints,
frontend work, authentication, cloud infrastructure, or deployment was added.
