# CloudXzen Pre-Milestone 2 Remediation Report

**Date:** 2026-10-28
**Product:** CloudXzen — Service Reliability Journal
**Scope:** Project rename and approved Milestone 1 remediation only

## 1. Rename confirmation

CloudXzen is now the canonical human-readable project name.

The project purpose remains the Service Reliability Journal. The approved modular-monolith architecture and zero-budget policy are unchanged.

Active project references were migrated to:

- `CloudXzen` for human-readable product and application names;
- `cloudxzen` for lowercase package/distribution and local database identifiers; and
- `CLOUDXZEN` for uppercase documentation filename conventions.

The GitHub remote was intentionally preserved:

```text
git@github.com:arthurmchege/cloudbench.git
```

The repository URL is an external Git identity and was not changed.

## 2. Files changed and renamed

### Renamed documentation files

- `docs/CLOUDBENCH_ROADMAP.md` → `docs/CLOUDXZEN_ROADMAP.md`
- `docs/CloudBench_Master_Project_Specification.md` → `docs/CloudXzen_Master_Project_Specification.md`
- `docs/CloudBench.pdf` → `docs/CloudXzen.pdf`

### Updated active files

- `.env.example`
- `README.md`
- `apps/api/pyproject.toml`
- `apps/api/README.md`
- `apps/api/alembic.ini`
- `apps/api/alembic/README`
- `apps/api/app/__init__.py`
- `apps/api/app/core/config.py`
- `apps/api/app/main.py`
- `docs/ARCHITECTURE.md`
- `docs/COST_AND_FREE_TIER.md`
- `docs/adr/ADR-001-modular-monolith-and-zero-cost-architecture.md`

### Historical files retained

- `docs/MILESTONE_0_REPORT.md`
- `docs/MILESTONE_1_REPORT.md`
- `docs/PRE_MILESTONE_2_AUDIT.md`

These reports retain historical CloudBench references and now include explicit historical-report notices. Their links to renamed files were updated where appropriate.

## 3. Database URL correction

The malformed local placeholder was corrected consistently in:

- `.env.example`
- `apps/api/app/core/config.py`
- `apps/api/alembic.ini`

The local-development format is now:

```text
postgresql+psycopg://cloudxzen:cloudxzen@localhost:5432/cloudxzen
```

The username, password, and database name are deliberately fake local-development values. No real credentials were added.

The application still does not require PostgreSQL for the health endpoint test. No database server was provisioned or started by this task.

## 4. README and linting corrections

The backend README now:

- identifies CloudXzen;
- installs the `test` and `dev` extras;
- accurately documents the test’s `httpx.AsyncClient` and `httpx.ASGITransport` approach; and
- documents the reproducible Ruff command:

```bash
ruff check app tests
```

Ruff was added as a development extra without changing Python versions or migrating dependency managers.

## 5. Dependency-management options

No dependency manager migration or lockfile was introduced.

The available options remain:

### Option A — pip plus pinned constraints

Keep `pyproject.toml`, generate a committed fully pinned constraints/requirements file, and use it in local development and CI.

- Advantages: familiar Ubuntu workflow, minimal tooling change, standard pip support.
- Disadvantages: lock generation/update process must be maintained; risk of two sources of truth.

### Option B — `uv` plus `uv.lock`

Keep `pyproject.toml`, use `uv` for resolution and installation, and commit its lockfile.

- Advantages: deterministic dependency graph, fast installs, strong local/CI reproducibility.
- Disadvantages: introduces a new development tool and changes the documented workflow.

### Option C — defer locking

Keep bounded dependency ranges temporarily.

- Advantages: no migration work before the database milestone.
- Disadvantages: installations can resolve different versions over time.

### Recommendation

Retain the current pip-compatible setup for this remediation. Before CI or a larger dependency graph is introduced, the project owner should approve either `uv` with `uv.lock` or a pinned pip constraints workflow. `uv` remains the stronger long-term reproducibility option, but it was not introduced without approval.

All options are free/open-source and compatible with the KSh 0 policy.

## 6. PostgreSQL development options

### Host-installed PostgreSQL

- Lowest runtime abstraction.
- Direct access to local PostgreSQL tools.
- Requires OS-level installation and local service management.
- Can create version differences between developers and CI.

### PostgreSQL in Docker

- Reproducible PostgreSQL version and configuration.
- Easy isolation and cleanup.
- Requires Docker to be installed and running.
- Docker resource usage may be inconvenient on some Ubuntu systems.

### Support both with one primary path

This maximizes contributor flexibility but increases setup documentation and the number of environments to verify.

### Recommendation

Use Docker PostgreSQL as the primary documented path if Docker is already available, while allowing host-installed PostgreSQL as an alternative. Before implementation, check whether Docker is installed rather than assuming it. The database test suite must remain PostgreSQL-based and must not silently substitute SQLite.

No hosted database is required.

## 7. Remaining Milestone 2 design decisions

### Status representation

Recommendation: derive current service status from the latest relevant service event for the initial product.

- Avoids duplicated state and transactional synchronization problems.
- Keeps the event history authoritative.
- May require a query or projection for dashboard reads.

Storing status on `services` could simplify reads, but every event mutation would need to update the service status transactionally and consistently.

### Service-name uniqueness

Recommendation: do not make display names globally unique before authentication and ownership exist.

A display name such as `Payments API` may reasonably be reused by different users or environments in a future version. If the first milestone needs a constraint, scope uniqueness deliberately, for example by an environment or a future owner boundary. This decision should not prematurely prevent future multi-user use.

### Timestamps

Recommendation:

- store timestamps in PostgreSQL using timezone-aware UTC columns;
- create and compare timestamps in UTC;
- serialize API timestamps with an explicit UTC offset, preferably `Z`;
- avoid naive datetime values at API/database boundaries.

The chosen approach should be documented in the database design before models are created.

### Test database strategy

Use an isolated PostgreSQL database for integration tests:

- a dedicated local test database or disposable Docker PostgreSQL instance;
- a separate `TEST_DATABASE_URL`;
- no fallback to the ordinary developer database;
- an explicit test setup/teardown process;
- CI later using a service container or equivalent isolated PostgreSQL service.

The test suite should fail clearly when PostgreSQL integration prerequisites are unavailable. SQLite should not replace PostgreSQL integration tests where PostgreSQL behavior matters.

### Milestone 2 scope

Recommendation: keep Milestone 2 narrow and verifiable:

1. local PostgreSQL setup documentation;
2. SQLAlchemy `services` and `service_events` models;
3. constraints and relationships;
4. initial Alembic migration;
5. database session/configuration improvements;
6. isolated PostgreSQL integration tests; and
7. setup documentation.

Do not add a persisted API endpoint in the remediation task. A first persistence endpoint should be a separate checkpoint after the schema is verified.

## 8. Validation performed

The following checks were executed after the changes:

- searched the repository for active old-name references;
- reviewed remaining old-name references as historical reports or the preserved GitHub remote;
- inspected renamed documentation links;
- installed the new development extra from the existing pip-compatible setup;
- ran backend tests;
- ran Python compilation;
- ran Ruff;
- loaded Pydantic Settings without displaying credentials;
- parsed the corrected SQLAlchemy URL without displaying credentials;
- validated Alembic configuration without connecting to PostgreSQL;
- reviewed the final diff for secrets, generated files, and unrelated changes.

No PostgreSQL server was provisioned or started, so database connectivity is not claimed.

## 9. Git status

The changes were grouped into a coherent rename/remediation checkpoint.

Commit:

```text
de6b240 chore: rename project to CloudXzen
```

Push result:

- pushed successfully to the existing `origin/main`;
- local `HEAD` and `origin/main` are synchronized after the push;
- no history rewrite or force-push was used.

GitHub returned this informational repository-moved notice:

```text
This repository moved. Please use the new location:
git@github.com:arthurmchege/cloudxzen.git
```

The configured remote URL was intentionally not changed because the task explicitly required preserving it. The existing remote remains:

```text
git@github.com:arthurmchege/cloudbench.git
```

## 10. Remaining blockers

- The project owner must approve the dependency-locking direction before introducing `uv`, a lockfile, or a pinned constraints workflow.
- The project owner should confirm the primary local PostgreSQL path.
- The project owner should approve the status, uniqueness, timestamp, and test-database decisions above.
- Milestone 2 database implementation has not started.

**STATUS: RENAME AND REMEDIATION COMPLETE — AWAITING MILESTONE 2 APPROVAL**
