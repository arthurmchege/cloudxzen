# CloudXzen Milestone 4 Completion

## Status

Milestone 4, **Core service-event workflow**, is implemented for the currently
defined backend scope and has been verified against the repository's PostgreSQL
test database.

This report is based on the implementation at commit `c4757c8` and the
verification commands recorded below. It distinguishes implemented behavior
from work that remains outside this milestone's completed scope.

## Objectives and scope

The roadmap defines Milestone 4 as the core service-event workflow:

- event creation;
- event history retrieval;
- status derivation;
- incident resolution;
- unit and integration tests;
- documentation updates.

The milestone remains intentionally limited to the backend service domain. It
does not add authentication, ownership, pagination, Redis, queues, background
workers, frontend functionality, cloud deployment, or a separate service.

## Implemented functionality

### Event schemas

[schemas.py](../apps/api/app/domains/services/schemas.py) defines:

- `ServiceEventCreate`
  - required `event_type`, `status`, `summary`, and `occurred_at`;
  - optional `details`;
  - excludes server-controlled `id`, `service_id`, `created_at`, and
    `resolved_at`.
- `ServiceEventResponse`
  - serializes SQLAlchemy event instances with `from_attributes=True`;
  - includes persisted identifiers, event data, occurrence time, resolution
    time, and creation time.

Validation currently enforces:

- event types are `check` or `incident`;
- event statuses are `operational`, `degraded`, or `down`;
- summaries are nonblank and no longer than 500 characters;
- occurrence timestamps include timezone information;
- incidents cannot use `operational` status;
- a response cannot represent a resolution earlier than occurrence.

### Repository operations

[repository.py](../apps/api/app/domains/services/repository.py) provides
module-level functions using the caller-provided SQLAlchemy `Session`:

- `create_service_event`;
- `list_service_events`;
- `get_service_event`;
- `resolve_service_event`.

The repository:

- does not create sessions;
- does not commit or roll back transactions;
- uses `flush()` when a generated or updated model must be available to the
  application layer;
- scopes event lookup and history to a service;
- orders event history deterministically newest-first by
  `occurred_at`, `created_at`, and `id`, all descending.

### API endpoints

The services router in
[services.py](../apps/api/app/api/routes/services.py) implements the
following event endpoints.

#### Create an event

```http
POST /services/{service_id}/events
```

The service must already exist. The request uses `ServiceEventCreate`.

- `201 Created`: returns the persisted event.
- `404 Not Found`: the service does not exist.
- `422 Unprocessable Entity`: request validation fails.
- `500 Internal Server Error`: a database failure occurs; the response uses
  the generic database-error envelope and does not expose internal details.

#### List event history

```http
GET /services/{service_id}/events
```

- `200 OK`: returns a bare JSON array of `ServiceEventResponse` objects.
- `200 OK` with `[]`: the service exists but has no events.
- `404 Not Found`: the service does not exist.

The response is ordered newest-first by occurrence timestamp, creation
timestamp, and event UUID as deterministic tie-breakers. Events belonging to
other services are not included.

#### Resolve an incident

```http
POST /services/{service_id}/events/{event_id}/resolve
```

The request has no body. The service and event must exist, and the event must
be an unresolved incident.

- `200 OK`: returns the updated event with `resolved_at`.
- `404 Not Found`: the service does not exist, or no event with that ID belongs
  to the service.
- `409 Conflict`: the event is a health check or the incident is already
  resolved.
- `500 Internal Server Error`: a database failure occurs and is represented by
  the generic database-error envelope.

The route generates `resolved_at` on the server with a timezone-aware UTC
timestamp. Clients cannot supply or override the resolution timestamp.

## Status derivation

[status.py](../apps/api/app/domains/services/status.py) contains the existing
`derive_service_status` function. This milestone did not change its algorithm.
The verified rules are:

1. no events produce `unknown`;
2. an unresolved incident takes precedence;
3. when there are no unresolved incidents, the latest check determines the
   status;
4. a history containing only resolved incidents produces `operational`.

Events are sorted using occurrence time, creation time, and event ID before
derivation. The status function is covered by unit tests, but Milestone 4 does
not expose a dedicated service-status API endpoint or include derived status in
the current service response.

## Database behavior and constraints

The existing PostgreSQL migration
[20260301_0001_create_service_tables.py](../apps/api/alembic/versions/20260301_0001_create_service_tables.py)
already supports the workflow. No Milestone 4 migration was required.

The `service_events` table provides:

- UUID primary keys;
- a foreign key to `services` with cascade delete;
- timezone-aware `occurred_at` and nullable `resolved_at`;
- database checks for valid event types and statuses;
- a check preventing operational incidents;
- a check preventing blank summaries;
- a check preventing resolved checks;
- a check preventing resolution before occurrence;
- an index on `(service_id, occurred_at)`.

Application validation provides client-facing errors before database writes.
PostgreSQL constraints remain the final integrity boundary.

Route-level transaction handling follows the established convention:

- the route calls the repository;
- the route commits and refreshes successful writes;
- SQLAlchemy failures trigger rollback;
- the centralized exception handler logs the failure and returns a generic
  `500` response without exposing SQL, credentials, or internal details.

Integration tests use `TEST_DATABASE_URL` and fail if it is the same as
`DATABASE_URL`. Test fixtures create and drop schema only on the dedicated
test database.

## Tests and verified results

The following verification was run from `apps/api` against the configured
PostgreSQL test database:

```bash
set -a && . ../../.env && set +a
.venv/bin/uv run --locked pytest
```

Result:

```text
46 passed
```

The suite includes:

- event schema validation and ORM serialization;
- status derivation unit tests;
- PostgreSQL repository persistence, ordering, scoping, foreign-key, and
  transaction-boundary tests;
- event creation API tests;
- event history API tests;
- incident resolution API tests;
- missing-resource and invalid-state responses;
- server-generated timezone-aware resolution timestamps;
- simulated database failure, generic error handling, and rollback behavior.

Additional checks completed successfully:

```bash
.venv/bin/uv run --locked ruff check app tests
.venv/bin/uv run --locked python -m compileall -q app tests
.venv/bin/uv lock --check
git diff --check
```

The reported results were:

- Ruff: all checks passed;
- Python compilation: passed;
- `uv lock --check`: passed;
- `git diff --check`: passed.

## Git checkpoints

Milestone 4 was implemented in small, reviewable checkpoints:

| Commit | Checkpoint |
|---|---|
| `2dbd3da` | Add service-event schemas and repository operations |
| `802afac` | Add the service-event creation endpoint |
| `5ca8f1b` | Add the service-event history endpoint |
| `c4757c8` | Add the incident-resolution endpoint |

At the time of this report, `main` and `origin/main` both point to
`c4757c8`.

## Known limitations and remaining work

The following items are not claimed as completed by this report:

- There is no dedicated endpoint for returning a derived service status.
- The current service response does not include derived status or a status
  summary.
- Multiple unresolved incidents are allowed; the current derivation function
  returns the newest unresolved incident according to its deterministic
  ordering. A product decision may be needed if only one active incident
  should be permitted.
- There is no pagination or filtering for event history.
- Authentication, authorization, ownership, and multi-user behavior are not
  implemented.
- Frontend event workflows are not implemented.
- Docker database runtime verification remains separate from the native
  PostgreSQL verification recorded by earlier milestones.
- CI, observability expansion, infrastructure-as-code, and Azure deployment
  remain later roadmap work.

These limitations do not invalidate the implemented event workflow, but they
should be addressed or explicitly deferred before broader production use.

## Conclusion

The documented Milestone 4 backend workflow is implemented and verified:
events can be validated, persisted, listed, and resolved through the API, with
PostgreSQL constraints, transaction boundaries, structured error handling, and
automated tests supporting the behavior. The remaining items above are
explicitly outside the verified completion claims of this checkpoint.
