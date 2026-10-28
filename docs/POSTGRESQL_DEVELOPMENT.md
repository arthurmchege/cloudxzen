# PostgreSQL Development Strategy

## Status

**Status:** Implemented for Milestone 2. Domain models, the initial
migration, the Compose database service, and guarded PostgreSQL integration
tests are available. Actual database execution remains environment-dependent.

CloudXzen will support both:

1. native PostgreSQL 18 on the Ubuntu development host; and
2. PostgreSQL 18 in an isolated Docker Compose environment.

Both environments must use the same SQLAlchemy models, Alembic migrations, schema, persistence code, and PostgreSQL integration tests.

## Environment inspection

The current development machine was inspected without changing services or starting containers:

| Component | Observed state |
|---|---|
| PostgreSQL client | PostgreSQL 18.6 |
| Native cluster | PostgreSQL 18 `main`, online |
| Native host binding | `127.0.0.1:5432` |
| PostgreSQL 16 cluster | Present but down; not used by CloudXzen |
| Docker Engine | 29.9.1 |
| Docker Compose | v5.6.0 |
| Docker Compose projects | None running |
| Port `5433` | Not listening at inspection time |

The native PostgreSQL service is managed through systemd. The top-level `postgresql.service` reports active while the version-specific cluster state is shown by `pg_lsclusters`.

No native PostgreSQL database or role was modified. The Compose file is
available as `compose.yaml`, but no container or volume was started or created.

## Port arrangement

The observed and preferred local arrangement is:

```text
Native PostgreSQL 18: 127.0.0.1:5432
Docker PostgreSQL 18: 127.0.0.1:5433 -> container 5432
```

Port `5432` is occupied by the native PostgreSQL 18 cluster. Port `5433` was free when inspected and is therefore the proposed Docker host port.

The Docker host port must remain configurable. If `5433` becomes occupied, choose another loopback-only port and update the local environment configuration. Never bind PostgreSQL to external network interfaces for ordinary development.

## Native PostgreSQL 18

### Check service and cluster status

```bash
systemctl is-active postgresql
systemctl status postgresql --no-pager
pg_lsclusters
```

Expected project-relevant result:

```text
18 main 5432 online postgres ...
```

`postgresql.service` is a systemd umbrella service. `pg_lsclusters` is the useful command for confirming which PostgreSQL version and cluster are actually online.

### Check readiness

```bash
pg_isready -h 127.0.0.1 -p 5432
```

### Connect

Use a PostgreSQL role with access to the CloudXzen database:

```bash
psql -h 127.0.0.1 -p 5432 -U cloudxzen -d cloudxzen
```

Do not use the `postgres` superuser as the application role.

### Create the dedicated development role and database

These commands are examples for an authorized PostgreSQL administrator. They must be reviewed before execution and should be run only if the role/database do not already exist. They do not belong in automated application startup.

```sql
CREATE ROLE cloudxzen LOGIN PASSWORD 'CHOOSE_A_LOCAL_PASSWORD';
CREATE DATABASE cloudxzen OWNER cloudxzen;
```

Use a local password supplied interactively or through a protected local mechanism. Do not put the real password in Git, shell history, committed files, or application source code.

The application role should own only the dedicated CloudXzen development database and should not receive superuser, createdb, createrole, replication, or system-level privileges.

Before creating anything, inspect existing roles and databases with an authorized administrative connection:

```sql
\du
\l
```

Do not drop, alter, or reset existing roles or databases as part of normal setup.

### Native connection configuration

For local use, set `DATABASE_URL` in an ignored `.env` file:

```text
DATABASE_URL=postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@localhost:5432/cloudxzen
```

The committed `.env.example` contains no password. The actual local password must never be committed.

## Docker PostgreSQL 18

Docker and the Compose plugin are installed on the current machine, but no container or Compose project was started during this task.

The Compose configuration uses:

- an official PostgreSQL 18 image;
- a service named `db`;
- a named volume for `/var/lib/postgresql/data`;
- a health check using `pg_isready`;
- a loopback-only host binding;
- configurable host port, defaulting to `5433`;
- dedicated `cloudxzen` database and application role; and
- environment values supplied from an ignored local `.env` file.

The intended application-to-database URL when the API runs on the host is:

```text
postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@localhost:5433/cloudxzen
```

If the API later runs inside the same Compose project, `localhost` must not be used. The database service name should be used instead:

```text
postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@db:5432/cloudxzen
```

### Docker workflow

```bash
docker compose up -d db
docker compose ps
docker compose logs db
docker compose stop db
docker compose start db
docker compose down
```

`docker compose down` stops and removes containers and the project network but does not remove named volumes by default.

The following is destructive and must not be run casually:

```bash
docker compose down -v
```

It removes the Compose project’s named volumes and can permanently delete the database data stored there. Back up data before any destructive volume operation.

Do not use `docker volume prune` for CloudXzen database maintenance.

### Future Docker diagnostics

```bash
docker compose ps
docker compose logs --tail=100 db
docker volume ls
docker inspect <container-name>
pg_isready -h 127.0.0.1 -p 5433
```

Common causes of failure include:

- port `5433` already being occupied;
- Docker daemon not running;
- invalid environment variables;
- a container health check still reporting `starting`;
- a stale or incompatible volume;
- insufficient Docker permissions; and
- the API using `localhost:5432` while the intended database is Docker on `5433`.

Do not delete a volume to solve a startup problem until its data has been inspected and backed up.

## Switching between native and Docker PostgreSQL

The application uses one `DATABASE_URL` setting. Switching environments means changing only the ignored local configuration:

### Native

```text
DATABASE_URL=postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@localhost:5432/cloudxzen
```

### Docker while API runs on the host

```text
DATABASE_URL=postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@localhost:5433/cloudxzen
```

### Docker while API runs in Compose

```text
DATABASE_URL=postgresql+psycopg://cloudxzen:YOUR_LOCAL_PASSWORD@db:5432/cloudxzen
```

The database schema and migration history must remain identical in all three cases.

## Migrations and tests

The same Alembic migration applies to either environment:

```bash
cd apps/api
uv run alembic upgrade head
```

Integration tests use a dedicated test database, not the ordinary development
database. Configure `TEST_DATABASE_URL` explicitly, for example:

```text
postgresql+psycopg://cloudxzen_test:YOUR_TEST_PASSWORD@localhost:5432/cloudxzen_test
```

The test database must be created separately and must never contain ordinary development data. CI should use an isolated PostgreSQL 18 service. SQLite is not an acceptable replacement for tests that verify PostgreSQL-specific behavior.

From `apps/api`, run unit tests without PostgreSQL:

```bash
uv run pytest
```

Run PostgreSQL integration tests separately:

```bash
uv run pytest tests/integration
```

The integration suite refuses to run when `TEST_DATABASE_URL` is absent or
matches `DATABASE_URL`.

## Backup and restore guidance

Before destructive database or volume operations, create a logical backup:

```bash
pg_dump -h 127.0.0.1 -p <port> -U cloudxzen -d cloudxzen > cloudxzen-backup.sql
```

Restore into an explicitly selected empty or disposable database:

```bash
psql -h 127.0.0.1 -p <port> -U cloudxzen -d cloudxzen < cloudxzen-backup.sql
```

Do not commit backup files. Add any local backup filename or directory to the appropriate ignored local storage if backups are created.

These commands are examples only. Confirm the target host, port, database, role, and backup contents before executing them.

## Prerequisites and safety boundary

Before the database milestone begins:

1. Confirm whether the native `cloudxzen` role and database already exist.
2. Confirm whether the developer is authorized to create them.
3. Decide whether native or Docker is the primary documented path.
4. Implement the Compose file only after reviewing the host-port mapping.
5. Create a dedicated test database or isolated test container.
6. Keep all passwords in ignored local configuration.
7. Do not stop or reconfigure the existing PostgreSQL 18 cluster.
8. Do not delete databases, data directories, Docker volumes, or containers without explicit approval.

No hosted database, paid service, or cloud infrastructure is required.
