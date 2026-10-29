# CloudXzen Milestone 7 Report

## Milestone Overview

Milestone 7, **Frontend/API Integration**, connects the Next.js frontend to
the existing FastAPI service-reliability API. The milestone begins as
**In Progress**.

The objective is to replace the foundation-only frontend experience with
honest, typed workflows for viewing services, registering a service, viewing
service events, recording supported events, and resolving incidents where the
backend supports those operations.

## Verified Repository Checkpoint

The repository was inspected before application changes:

- repository root: `/home/arthur/Projects/CloudBench`;
- branch: `main`;
- `HEAD`: `88c1f5b` (`docs: reconcile Milestone 6 verification`);
- working tree: clean, with no untracked files;
- remote: `origin` points to `arthurmchege/cloudxzen`;
- local `main` and `origin/main`: synchronized with divergence `0 0`.

Milestones 0–6 are documented as complete in the roadmap. The existing
frontend is the Next.js 15 foundation in `apps/web`; it currently has no live
API client or production service data. The backend is the modular-monolith
FastAPI application in `apps/api`, backed by PostgreSQL, SQLAlchemy, and
Alembic.

## Scope and Acceptance Criteria

This milestone is expected to:

- establish a typed, centralized frontend API client;
- retrieve and display real services with loading, empty, retry, and error
  states;
- register services using the actual backend request schema;
- display service details and event history;
- create supported service events;
- resolve incidents only through the existing backend operation;
- preserve accessible, responsive UI behavior and the existing visual
  foundation;
- test API parsing/failure behavior and user-visible service workflows;
- preserve the backend regression suite and the KSh 0 cost target.

This milestone will not add authentication, new infrastructure, Redis,
queues, microservices, database schema changes, fabricated metrics, or
unsupported backend capabilities.

## Actual Backend API Contracts

The backend currently exposes these product routes:

```text
POST /services
GET /services
POST /services/{service_id}/events
GET /services/{service_id}/events
POST /services/{service_id}/events/{event_id}/resolve
```

`GET /health` remains an infrastructure health route outside the product
namespace.

Services use UUID identifiers and return:

- `id`, `name`, `description`, `environment`;
- derived `status`: `unknown`, `operational`, `degraded`, or `down`;
- `created_at` and `updated_at`.

Service registration accepts only `name`, `description`, and `environment`.
Names and environments must be non-blank and fit their length limits.

Events use:

- `event_type`: `check` or `incident`;
- `status`: `operational`, `degraded`, or `down`;
- non-blank `summary`;
- optional `details`;
- timezone-aware `occurred_at`;
- response fields `id`, `service_id`, `resolved_at`, and `created_at`.

Incident events cannot use `operational` status. Incident resolution has no
request body and returns `409` for check events or already-resolved incidents.
Unknown services and events return `404`.

Successful collection responses are bare JSON arrays. Errors use the
structured envelope:

```json
{
  "error": {
    "code": "validation_error | not_found | conflict | database_error",
    "message": "A user-readable message.",
    "details": []
  }
}
```

The `details` field is present for validation errors and may be absent for
other failures. The API also returns `X-Request-ID`; the existing frontend
integration must not change that policy.

## API Namespace Decision

The written project specification and architecture planning text refer to a
versioned `/api/v1` API. The implemented backend, backend README, Milestone 5
report, tests, and current consumers use root `/services` routes. The backend
router is explicitly declared with `prefix="/services"` and no application
level `/api/v1` prefix or alias exists.

The repository therefore does not contain an authoritative decision that
resolves the discrepancy. Changing the namespace during integration would
affect every existing backend test, API README example, generated OpenAPI
path, and any future consumer. Adding aliases would expand the public
contract and create duplicate routes without a demonstrated compatibility
requirement.

Options:

1. **Integrate with the existing `/services` routes (recommended).**
   - Smallest change and matches the implemented, tested contract.
   - Avoids backend route changes and duplicate aliases.
   - The frontend client can isolate the path constants so a future versioned
     migration remains contained.
   - The specification and architecture documentation would need a later
     compatibility update.

2. **Introduce `/api/v1` as the canonical namespace.**
   - Aligns future API evolution with the high-level specification.
   - Requires changing routes, tests, documentation, OpenAPI paths, and the
     frontend base-path contract.
   - A compatibility period would require aliases or a coordinated consumer
     migration, increasing scope and maintenance.

3. **Add `/api/v1` aliases while retaining `/services`.**
   - Allows both old and new consumers to operate.
   - Duplicates the public surface, complicates documentation and testing, and
     does not establish which contract is canonical.
   - Not justified without an explicit backward-compatibility requirement.

Recommended decision: approve option 1 for Milestone 7, preserving the
existing `/services` contract and recording `/api/v1` as a later compatibility
decision. No dependent frontend integration code will be implemented until
this decision is confirmed.

## Proposed Implementation Plan

After the namespace decision is confirmed:

1. Add a typed API client with configurable browser-safe base URL, structured
   error parsing, malformed-response guards, and network-failure handling.
2. Add service list and registration workflows using the existing routes.
3. Add service details, event history, event creation, and incident resolution
   workflows supported by the backend.
4. Add loading, empty, validation, success, retry, and failure states without
   fabricated service data.
5. Add focused network-boundary and user-visible workflow tests.
6. Run frontend and backend quality gates, update the roadmap/report, then
   create a reviewed Git checkpoint.

## Testing Strategy

Frontend tests will cover:

- successful API parsing;
- structured non-success responses;
- backend validation details;
- network failures;
- malformed response handling;
- service list loading, success, empty, and error states;
- registration validation, submission, success, and failure;
- service details and event-history success/error states;
- event creation and incident resolution where implemented.

Verification will include `npm ci`, lint, TypeScript checking, Vitest,
production build, the existing backend test suite, Ruff, Python compilation,
lock validation, and Git diff checks. Tests will use safe network-boundary
mocks or a dedicated test configuration and will not contact production data.

## Known Limitations and Risks

- The `/api/v1` versus `/services` discrepancy is unresolved and blocks
  dependent integration work until approved.
- The backend has no pagination, authentication, ownership, or uptime
  percentage calculation; the frontend must not present those as available.
- The backend database routes require PostgreSQL, so browser development
  requires the API and a configured database.
- Cross-origin development configuration may be needed once the client is
  implemented; no production origin or secret will be hard-coded.

## Initial Status

**In Progress — contract discovery and namespace decision pending.**

No frontend/API integration functionality has been implemented in this
milestone yet. Completion will require verified tests, quality checks, a
roadmap update, and a final Git checkpoint.

## Next Action

Confirm whether Milestone 7 should preserve and consume the implemented root
`/services` contract (recommended), or whether the project should first adopt
`/api/v1` through a separately scoped backend compatibility change.
