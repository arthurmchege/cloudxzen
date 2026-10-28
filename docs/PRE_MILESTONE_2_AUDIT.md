# CloudBench Pre-Milestone 2 Repository Audit

> **Historical report:** This audit records the repository state before the project was renamed from CloudBench to CloudXzen. It is retained for audit history; the current remediation and rename status is documented separately.

**Audit date:** 2026-10-28
**Scope:** Read-only audit before PostgreSQL domain models and migrations
**Product:** CloudBench — Service Reliability Journal

## 1. Executive summary

Milestone 1 is substantially implemented and reproducible for the health-only backend foundation:

- the FastAPI application imports and starts;
- `GET /health` returns the expected response;
- request IDs are generated and propagated;
- request logging is visible;
- Pydantic Settings loads and validates environment configuration;
- the test suite passes;
- Python compilation passes; and
- the Git branch is clean and synchronized with `origin/main`.

However, the repository is **not ready for Milestone 2 without a configuration correction**. The default PostgreSQL URL is malformed in three tracked locations:

```text
******localhost:5432/cloudbench
```

It is present in:

- `.env.example`
- `apps/api/app/core/config.py`
- `apps/api/alembic.ini`

The health endpoint does not expose this because it does not connect to PostgreSQL, and SQLAlchemy creates its engine lazily. Database implementation should not begin until the project owner approves replacing this placeholder with a valid, clearly fake local PostgreSQL URL.

## 2. Classification summary

| Area | Classification | Finding |
|---|---|---|
| Repository state | PASS | Working tree was clean before this audit report; branch is `main`. |
| FastAPI import/startup | PASS | `app.main` imported and Uvicorn started successfully. |
| Health endpoint | PASS | Live request returned HTTP 200 and `{"status":"ok"}`. |
| Request IDs | PASS | IDs are generated when absent and propagated when supplied. |
| Request logging | PASS | Startup and request completion logs were observed. |
| Pydantic Settings | PASS | Defaults, environment overrides, and invalid values behaved as expected. |
| SQLAlchemy foundation | WARNING | Engine/session scaffolding exists, but the configured database URL is malformed. |
| Alembic scaffolding | WARNING | Metadata is referenced and no domain revisions exist, but Alembic uses the same malformed URL. |
| Automated tests | PASS | One test passed with the documented command. |
| Python compilation | PASS | `compileall` completed successfully. |
| Linting | NOT VERIFIED | Ruff is configured in `pyproject.toml` but is not installed or declared as a dependency. |
| Dependency reproducibility | WARNING | Version ranges exist, but no lockfile exists. |
| Documentation consistency | WARNING | Backend README says the test uses `TestClient`; the actual test uses `httpx.ASGITransport`. |
| Milestone 2 readiness | BLOCKER | Correct the local PostgreSQL URL before database implementation. |
| Git synchronization | PASS | Local `HEAD` equals `origin/main`; `git ls-remote` verified the remote ref. |
| Zero-budget compliance | PASS | No cloud services or paid infrastructure were activated. |

## 3. Actual repository state

The repository contains:

- root README and Git hygiene files;
- root `.env.example`;
- `apps/api/pyproject.toml`;
- FastAPI application modules under `apps/api/app`;
- SQLAlchemy session and declarative-base scaffolding;
- Alembic configuration and environment;
- one health test;
- backend README;
- architecture, cost, roadmap, milestone, and ADR documentation.

The repository does **not** contain:

- domain SQLAlchemy models;
- domain database tables;
- Alembic migration revisions;
- frontend code;
- Docker configuration;
- GitHub Actions workflows;
- cloud infrastructure;
- cloud deployment configuration.

That absence is consistent with the requested milestone boundary.

## 4. Verification results

### 4.1 FastAPI import and startup — PASS

Command:

```bash
cd apps/api
.venv/bin/python -c 'from app.main import app; print(app.title, app.version)'
```

Observed:

```text
CloudBench API 0.1.0
```

Uvicorn was also started successfully on a local port.

### 4.2 Health endpoint — PASS

Command:

```bash
curl http://127.0.0.1:8001/health
```

Observed:

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

### 4.3 Request IDs — PASS

Without a request header, the response included a generated UUID in `X-Request-ID`.

With:

```http
X-Request-ID: audit-request-123
```

the response returned:

```http
X-Request-ID: audit-request-123
```

### 4.4 Request logging — PASS

Observed logs included:

- application startup;
- request ID;
- HTTP method;
- path;
- status code; and
- request duration.

Example observed shape:

```text
request_complete request_id=... method=GET path=/health status_code=200 duration_ms=...
```

### 4.5 Configuration — PASS with database URL blocker

Pydantic Settings behavior was verified:

- default environment: `development`;
- explicit `ENVIRONMENT=test`: `test`;
- invalid `ENVIRONMENT=staging`: `ValidationError`.

The configuration mechanism is correctly environment-driven. However, the actual default database URL was verified as:

```text
'******localhost:5432/cloudbench'
```

This is not a valid SQLAlchemy PostgreSQL URL. It is not a real credential, but it is also not a usable local connection string.

### 4.6 SQLAlchemy — WARNING

The following foundation exists:

- `create_engine`;
- `sessionmaker`;
- `get_db` generator;
- declarative `Base`.

The engine can be instantiated because SQLAlchemy defers the database connection. No PostgreSQL connection was attempted during this audit. A real database connection cannot be considered verified.

### 4.7 Alembic — WARNING

The Alembic environment imports:

```python
from app.db.base import Base
```

and assigns:

```python
target_metadata = Base.metadata
```

This is the intended metadata reference. `alembic heads` and `alembic history` completed with no revisions, which is correct for the current no-domain-table state.

Alembic has not been used against PostgreSQL because no database server was required or available for this health-only milestone, and its configured URL is malformed.

### 4.8 Tests — PASS

Command:

```bash
cd apps/api
.venv/bin/python -m pytest
```

Result:

```text
1 passed in 0.75s
```

The test uses `httpx.ASGITransport` and does not require PostgreSQL, cloud services, internet access, or a deployed server.

### 4.9 Python compilation — PASS

Command:

```bash
python3 -m compileall -q app tests
```

Result: completed successfully.

### 4.10 Linting — NOT VERIFIED

The project contains Ruff configuration:

```toml
[tool.ruff]
...
```

but Ruff is not declared in the project dependencies and is not installed in the backend virtual environment. Running the module form produced:

```text
No module named ruff
```

No lint result is claimed.

## 5. Confirmed problems

### BLOCKER — malformed PostgreSQL URL configuration

Locations:

- `.env.example`
- `apps/api/app/core/config.py`
- `apps/api/alembic.ini`

Current value:

```text
******localhost:5432/cloudbench
```

Impact:

- SQLAlchemy cannot connect to a local PostgreSQL server with this value.
- Alembic cannot connect to apply or inspect migrations with this value.
- The database milestone cannot be verified reliably.

Recommended correction, subject to project-owner approval:

```text
postgresql+psycopg://cloudbench:cloudbench@localhost:5432/cloudbench
```

This is a local-only example with fake credentials, not a production secret. The same configuration convention should be used consistently by Pydantic Settings and Alembic.

### WARNING — test documentation mismatch

`apps/api/README.md` says:

> The health test uses FastAPI's in-process `TestClient`.

The actual test uses `httpx.AsyncClient` with `httpx.ASGITransport`.

This does not affect runtime correctness, but it reduces documentation accuracy.

### WARNING — lint command is not reproducible

Ruff is configured but not declared or installed. A future contributor cannot reproduce the configured lint check using only the documented project dependencies.

## 6. Dependency reproducibility assessment

### Current approach

Dependencies are declared in `apps/api/pyproject.toml` using bounded ranges, for example:

```toml
fastapi>=0.115,<1.0
sqlalchemy>=2.0,<3.0
```

This establishes compatibility boundaries but does not pin a complete dependency graph. There is no `requirements.txt`, `uv.lock`, Poetry lockfile, or other lockfile.

### Current reproducibility

**Classification: WARNING.**

The setup is installable in the current environment, but two installations at different times can receive different compatible versions. Transitive dependencies can also change. The Milestone 1 environment was installed successfully, but that is not equivalent to deterministic reproduction.

Python compatibility is currently coherent:

- available Python: 3.14.4;
- declared Python: `>=3.14,<3.15`;
- installed package wheels were available for the current environment.

This does not prove that every future platform or provider will have identical wheel availability.

### Option A — add a committed pip constraints/requirements file

Example approach:

- keep `pyproject.toml` as the project metadata and dependency source;
- generate a fully pinned `requirements.lock` or constraints file;
- install the pinned file in local development and CI.

Advantages:

- familiar to Ubuntu and GitHub Actions users;
- minimal tooling change;
- easy to inspect;
- works with standard `pip`.

Disadvantages:

- lock generation and update policy must be maintained manually;
- extras and platform-specific dependencies require care;
- the project can accidentally maintain two sources of truth.

### Option B — use `uv` with a committed `uv.lock`

Example approach:

- keep `pyproject.toml`;
- use `uv` to resolve and install;
- commit `uv.lock`;
- use the same commands locally and in GitHub Actions.

Advantages:

- fast and deterministic resolution;
- lockfile includes the complete dependency graph;
- good fit for a modern Python application;
- can create/manage virtual environments.

Disadvantages:

- adds a dependency-management tool that contributors must install;
- requires documenting `uv` for Ubuntu and CI;
- platform-specific resolution still needs review;
- changes the current setup, which currently works with standard `venv` and `pip`.

### Recommendation

Do not change dependency management during this audit. Before Milestone 2 grows the dependency graph, adopt **Option B (`uv` plus a committed `uv.lock`)** if the project owner accepts adding one small development tool.

Reasoning:

- it preserves `pyproject.toml`;
- it provides the strongest practical reproducibility for local Ubuntu development and GitHub Actions;
- it is free and open source;
- it does not introduce a runtime service or cloud cost; and
- it avoids manually maintaining a second pip constraints workflow.

If minimizing tooling is more important than deterministic resolution, Option A is a valid lower-change alternative.

Approval is required before changing dependency tooling or adding a lockfile.

## 7. Git and remote synchronization

### Local state — PASS

Before creating this audit report:

```text
## main...origin/main
```

The worktree was clean, with no staged or unstaged source changes.

### Recent history

The latest milestone commits are present:

```text
6fae9f5 docs: record Milestone 1 completion
884052a feat(api): add FastAPI health application
98ee7bf feat(api): establish Python backend foundation
```

### Remote synchronization — PASS

The configured remote is:

```text
origin git@github.com:arthurmchege/cloudbench.git
```

The following hashes matched:

- local `HEAD`: `6fae9f561726cee3f4fca748db333f7197485c4d`
- local `origin/main`: `6fae9f561726cee3f4fca748db333f7197485c4d`
- remote `refs/heads/main`: `6fae9f561726cee3f4fca748db333f7197485c4d`

No credentials or private key content was displayed.

This audit made no commits, pushes, pulls, resets, rebases, amendments, or history rewrites.

## 8. Zero-budget compliance

**Classification: PASS.**

Verified:

- no cloud services were provisioned;
- no Azure resource was provisioned;
- no paid dependency was introduced;
- the health test runs locally without PostgreSQL or internet access;
- the current backend can be developed with Python, local files, and free/open-source packages.

Potential future cost decisions:

- hosted PostgreSQL;
- free-tier application hosting;
- monitoring/error reporting;
- any provider-required build or registry service.

None should be activated without current official pricing/terms verification and explicit approval. Milestone 2 can remain local and zero-cost.

## 9. Milestone 2 readiness assessment

### Overall status: BLOCKED pending database URL correction

The architecture is otherwise ready for a focused database milestone:

- SQLAlchemy engine/session structure exists.
- Declarative base exists.
- Alembic metadata wiring exists.
- Domain tables have not been created prematurely.
- Health tests do not depend on PostgreSQL.
- Local development is provider-independent.

Before implementing models and migrations, the project needs:

1. approval to correct the local PostgreSQL URL in configuration and examples;
2. a reproducible local PostgreSQL strategy, either a host installation or Docker, without requiring a hosted service;
3. a clear test database strategy;
4. a migration execution strategy;
5. a decision on whether service status is stored or derived from events;
6. a decision on service name uniqueness scope;
7. a decision on timestamp conventions and UTC handling; and
8. a decision on whether the first database milestone includes only schema/integration tests or also the first API persistence endpoint.

## 10. Decisions requiring project-owner approval

### Decision 1 — Correct the database URL

Approve replacing the malformed value with a valid fake local URL:

```text
postgresql+psycopg://cloudbench:cloudbench@localhost:5432/cloudbench
```

### Decision 2 — Dependency locking

Choose one:

1. adopt `uv` and commit `uv.lock` (recommended); or
2. retain pip and add a committed pinned constraints/requirements file; or
3. defer locking until CI is introduced, accepting reduced reproducibility temporarily.

### Decision 3 — Local PostgreSQL runtime

Choose one:

1. host-installed PostgreSQL;
2. Docker PostgreSQL;
3. support both, with one documented primary path.

No hosted database is required for Milestone 2.

### Decision 4 — Status representation

Choose one:

1. derive current service status from the latest event; or
2. store a current status on `services` and update it transactionally with events.

Derivation reduces duplicated state. A stored status can make reads simpler but creates consistency responsibilities.

### Decision 5 — Scope of the next milestone

Choose one:

1. database foundation, models, migration, and persistence tests only; or
2. all of the above plus the first persisted API endpoint.

The narrower option better preserves incremental milestone boundaries.

## 11. Recommended next steps

Ordered by priority:

1. Approve correction of the malformed local PostgreSQL URL.
2. Decide whether to adopt `uv`/`uv.lock` or a pip constraints file.
3. Decide the primary local PostgreSQL setup path.
4. Correct the backend README’s test-client description when the next approved change window opens.
5. Add a reproducible database test strategy before creating domain models.
6. Resolve the status representation and uniqueness/timestamp decisions.
7. Begin Milestone 2 only after these decisions are approved.

## 12. Audit boundary and stop condition

This audit did not modify application source code, configuration, dependencies, migrations, tests, or existing documentation. The only requested deliverable created by this audit is this report.

No Milestone 2 implementation was started.

**STATUS: AUDIT COMPLETE — WAITING FOR PROJECT-OWNER APPROVAL**
