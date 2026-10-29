# CloudXzen Implementation Roadmap

## Current repository assessment

The opening roadmap sections below preserve the original planning context, but
the repository has since progressed through Milestones 0–6. The current
verified state is:

- the modular-monolith backend is implemented in `apps/api` with FastAPI,
  PostgreSQL, SQLAlchemy, Alembic, tests, and documented quality checks;
- the Next.js 15 frontend foundation is implemented in `apps/web` with
  TypeScript, Tailwind CSS, tests, and production build checks;
- Milestones 0–6 are complete where their milestone sections below record
  verified evidence;
- Milestone 7, Frontend/API integration, is the next planned milestone and
  has not started;
- the current product API uses root `/services` routes while `/api/v1` remains
  an unresolved compatibility decision;
- local development continues to target KSh 0 and the modular-monolith
  architecture.

The historical planning baseline was written before implementation began. Its
recommendations remain useful context, but statements describing an empty
repository are no longer current status claims.

## 1. Recommended product/domain

### Product: CloudXzen Service Reliability Journal

CloudXzen should be a small operational journal for recording service checks and incidents.

A user can:

1. Register a service or monitored dependency.
2. Record a check result or incident against that service.
3. View the current service status and recent history.
4. Resolve an active incident.
5. Review a small dashboard showing service health over time.

This is not a large SaaS platform. It is a modest but real product that supports a real database, API, frontend, and operations story.

### Core concepts

- Service
  - name
  - description
  - environment
  - status
  - timestamps

- Service event
  - event type: check or incident
  - status: operational, degraded, or down
  - summary
  - details
  - occurred_at
  - resolved_at

### Core workflow

Create a service → record status event → view recent history → resolve incident.

This is enough to justify a real relational model, validation, frontend actions, testing, Docker, provider-portable deployment, health checks, and observability.

### Explicit non-goals for MVP

- external service polling
- alerting integrations
- SMS/email notifications
- team roles or auth-heavy workflows
- billing
- multi-region systems
- AI features
- microservice decomposition

## 2. Why this product is appropriate

This domain is a better fit than a generic task manager or large SaaS platform because it:

- has a clear domain and user workflow
- requires relational persistence without excessive complexity
- supports meaningful status transitions and validation
- creates useful API endpoints without endpoint inflation
- naturally suits a small dashboard and event history UI
- gives real backend business logic instead of simple CRUD only
- aligns with CloudXzen’s operational and engineering theme

## 3. Proposed system architecture

Use a modular monolith:

```text
Browser
   |
   | HTTPS
   v
Next.js 15 web application
   |
   | JSON over HTTPS
   v
FastAPI modular monolith
   |
   | SQLAlchemy
   v
PostgreSQL
```

Supporting concerns:

```text
FastAPI
├── structured logs
├── health endpoint
├── OpenAPI docs
└── optional Sentry integration

GitHub Actions
├── frontend lint/typecheck/test/build
├── backend lint/typecheck/test
└── container build verification

Provider-agnostic deployment
├── free-tier web app hosting
├── free-tier API hosting
├── free-tier PostgreSQL
└── monitoring/error reporting if justified
```

## 4. Proposed repository structure

```text
cloudxzen/
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── public/
│   │   ├── tests/
│   │   └── ...
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── db/
│       │   ├── domains/
│       │   ├── main.py
│       │   └── ...
│       ├── tests/
│       ├── pyproject.toml
│       └── ...
│
├── docs/
│   ├── CloudXzen_Master_Project_Specification.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── BACKEND.md
│   ├── FRONTEND.md
│   ├── TESTING.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   ├── OBSERVABILITY.md
│   ├── BUILD_LOG.md
│   └── adr/
│
├── infrastructure/
│   └── azure/
│       ├── main.bicep
│       ├── modules/
│       └── parameters/
│
├── docker/
│   ├── api.Dockerfile
│   └── web.Dockerfile
│
├── .github/
│   └── workflows/
│
├── compose.yaml
├── .env.example
├── .gitignore
├── README.md
└── docs/CloudXzen.pdf
```

## 5. Backend architecture

Milestone 1 implemented the initial Python 3.14/FastAPI foundation, environment-driven configuration, process health endpoint, logging baseline, SQLAlchemy session foundation, Alembic scaffolding, and an isolated API test. Domain models and migrations remain intentionally deferred.

Use FastAPI with a clear request flow:

```text
Route
  ↓
Request/response schema
  ↓
Application/domain service
  ↓
Repository/data-access layer
  ↓
SQLAlchemy session
  ↓
PostgreSQL
```

### Recommended modules

- API routes
- schemas/validation
- domain/application logic
- repository/data-access layer
- configuration
- infra integrations
- tests

### Technology rationale

| Technology | Problem solved | Why needed | If omitted | Complexity | Decision |
|---|---|---|---|---|---|
| Python | backend implementation language | follows project requirement | would violate the standard stack | low | use |
| FastAPI | API framework and OpenAPI generation | validation, routing, docs | more manual work | low | use |
| Pydantic | validation and serialization | explicit contracts | duplicated validation | low | use |
| SQLAlchemy | DB access and mapping | structured persistence | raw SQL increases complexity | moderate | use |
| Alembic | schema migrations | safe/schema evolution | manual changes drift | low/moderate | use |
| pytest/httpx | tests | API and integration verification | weaker validation | low | use |
| Redis | caching/session/async work | no current requirement | simple PostgreSQL-based design remains enough | operational overhead | do not use |
| Kafka/RabbitMQ | async worker processing | no current requirement | synchronous domain is simpler | high operational complexity | do not use |
| Microservices | independent deployment | not justified by current scope | modular monolith is simpler | high | do not use |
| Kubernetes | orchestration | no scale requirement | Azure managed hosting is enough | very high | do not use |

## 6. Frontend architecture

Use Next.js 15 App Router with React 19 and TypeScript.

### Server Components

Use these for:

- initial dashboard rendering
- static layout
- read-only summary pages
- metadata and page structure

### Client Components

Use these for:

- forms
- service creation
- event submission
- resolve actions
- toast notifications
- client-side interactivity

### Suggested frontend routes

- `/`
- `/services`
- `/services/new`
- `/services/[id]`
- `/services/[id]/events/new`

### Frontend principles

- responsive design
- accessible controls
- loading/error/empty states
- typed API client
- Sonner for transient notifications
- Framer Motion only for meaningful transitions
- shadcn/ui + Radix primitives for reusable UI patterns

## 7. PostgreSQL data model (high level)

### `services`

| Column | Purpose |
|---|---|
| `id` | UUID primary key |
| `name` | service name |
| `slug` | stable slug if needed |
| `description` | optional description |
| `environment` | dev/staging/prod |
| `created_at` | creation time |
| `updated_at` | last update |

### `service_events`

| Column | Purpose |
|---|---|
| `id` | UUID primary key |
| `service_id` | FK to services |
| `event_type` | check or incident |
| `status` | operational/degraded/down |
| `summary` | short summary |
| `details` | optional long detail |
| `occurred_at` | event time |
| `resolved_at` | for resolved incidents |
| `created_at` | record creation time |

### Constraints

- foreign keys enforced
- disallow empty summary
- status and event type are constrained values
- `resolved_at` only valid for relevant incidents
- timestamps stored consistently in UTC
- service names scoped with a deliberate uniqueness rule

### Indexes

Start with real queries only:

- `service_events.service_id`
- `service_events.service_id, occurred_at DESC`
- optionally `services.environment` if filtering is required

## 8. API design (high level)

### Health

```text
GET /health
```

### Services

```text
GET    /api/v1/services
POST   /api/v1/services
GET    /api/v1/services/{service_id}
```

### Service events

```text
GET  /api/v1/services/{service_id}/events
POST /api/v1/services/{service_id}/events
```

### Incident resolution

```text
POST /api/v1/services/{service_id}/events/{event_id}/resolve
```

### API conventions

- version under `/api/v1`
- consistent HTTP status codes
- response schemas
- structured error models
- input validation on all external input
- pagination only when it is justified
- OpenAPI documentation from FastAPI

Authentication should be deferred unless there is a real need for user-level control.

## 9. Testing strategy

### Backend unit tests

- validation behavior
- transformations
- domain rules
- calculations
- edge cases

### Backend integration tests

- SQLAlchemy persistence
- foreign key behavior
- migration correctness
- service/event-related queries
- transaction behavior

### API tests

- valid requests
- invalid requests
- validation failures
- correct status codes
- error contracts
- health endpoint

### Frontend tests

- service list rendering
- forms and validation
- empty/error states
- user interaction and success feedback
- result pages

### E2E tests

Use selectively for the critical path:

1. create service
2. record incident
3. confirm status changes
4. resolve incident
5. confirm final state

## 10. Docker strategy

Use containers for local reproducibility and CI consistency.

### Docker approach

- API image
- Web image
- PostgreSQL via Docker Compose
- production images built without secrets
- environment variables for configuration

### Decision rule

Do not add Docker Compose unless it meaningfully improves local development. A single local PostgreSQL container plus direct local app startup may be enough early on.

## 11. GitHub Actions CI strategy

### Standard pipeline

1. dependency install
2. lint
3. typecheck
4. tests
5. build
6. container build verification

### Backend checks

- lint
- type checking
- integration tests
- API tests

### Frontend checks

- lint
- typecheck
- tests
- production build

This must protect the main branch from broken code.

## 12. Provider-agnostic deployment strategy

The initial deployment target should be deliberately simple and provider-agnostic:

```text
Free-tier web and API hosting
├── Next.js web app
├── FastAPI API
└── free-tier PostgreSQL
```

### Decision factors

- target cost of KSh 0
- simplicity
- reliability
- deployment workflow
- portfolio value
- operational overhead
- persistence, sleep behavior, quotas, and billing risk

Azure is an optional future target because Azure for Students verification is not currently confirmed. Do not provision Azure resources until current eligibility, pricing, and billing risk are verified and explicitly approved. Avoid Kubernetes and unnecessary cloud services at the MVP stage.

## 13. Infrastructure-as-Code strategy

Use Bicep if Azure is selected later. Infrastructure-as-Code should remain provider-specific and isolated from application code.

### Goals

- version-controlled infrastructure
- repeatable provision
- environment parameters
- clear dependencies
- safe upgrades

### Minimal starting point

- resource group
- hosting resources
- PostgreSQL resource
- app config
- monitoring hooks
- secure secret configuration

Terraform should not be introduced unless there is a clear reason.

## 14. Observability strategy

### Minimum requirements

- health endpoint
- structured logs
- request IDs / correlation IDs
- safe error context
- basic production verification

### Logging contract

Log:

- timestamp
- severity
- route
- method
- status code
- duration
- safe application context

Do not log:

- API keys
- passwords
- database credentials
- secrets
- unsafe personal data

### Error monitoring

Use Sentry or a similar service only when the value is justified. It should capture failures without exposing sensitive data.

## 15. Security strategy

- validate all backend inputs
- use schema validation and parameterized DB queries
- avoid stack traces in API responses
- configure CORS deliberately
- use secure headers where appropriate
- never commit `.env` files
- store secrets in environment-protected mechanisms
- use least privilege wherever possible
- run dependency checks in CI
- do not deploy secrets in source control

Authentication should be added only when the product actually needs multi-user control or protected writes.

## 16. Documentation structure

The repository should gradually gain:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/DATABASE.md`
- `docs/BACKEND.md`
- `docs/FRONTEND.md`
- `docs/TESTING.md`
- `docs/SECURITY.md`
- `docs/DEPLOYMENT.md`
- `docs/OBSERVABILITY.md`
- `docs/BUILD_LOG.md`
- `docs/adr/`

This documentation is part of the product’s value.

## 17. Major implementation milestones

### Milestone 0 — Product and repository foundation

Achievements:

- confirm product scope and MVP boundaries
- decide repository layout
- add `.gitignore`
- add `.env.example`
- expand README
- decide architecture direction
- document product contract

Git checkpoint:

```text
docs: define CloudXzen product and engineering roadmap
```

### Milestone 1 — Backend foundation

Achievements:

- FastAPI bootstrap
- configuration management
- `/health` endpoint
- logging baseline
- lint/test tooling
- health API tests

Git checkpoint:

```text
feat: bootstrap FastAPI service
```

### Milestone 2 — Database foundation

**Status:** Verified successfully against native PostgreSQL 18. Docker Compose
configuration is implemented and validated, but the Docker database runtime
has not been verified.

Achievements:

- PostgreSQL local setup
- SQLAlchemy session management
- initial domain models
- Alembic setup
- first migration
- DB integration setup

Git checkpoints:

```text
feat: add PostgreSQL persistence foundation
feat: add initial service event migration
```

### Milestone 3 — First working product endpoint

Achievements:

- service schemas
- repository layer
- service creation endpoint
- service listing endpoint
- validation and errors
- API tests

Git checkpoints:

```text
feat: implement service creation API
feat: add service listing and validation
```

### Milestone 4 — Core service-event workflow

Achievements:

- event creation
- event history API
- status derivation
- derived status in service API responses
- incident resolution
- unit/integration tests
- documentation updates

Git checkpoints:

```text
feat: add service event workflow
feat: add incident resolution rules
```

### Milestone 5 — Backend API hardening and documentation

**Status: Complete and verified.**

Objectives:

- standardize HTTP error envelopes and generated error responses;
- make production documentation exposure an explicit configuration decision;
- verify request correlation headers and meaningful database failure behavior;
- document the current unversioned API contract and the deferred `/api/v1`
  compatibility decision;
- add focused failure-path and OpenAPI contract tests.

This milestone does not add authentication, pagination, Redis, queues, cloud
resources, or paid services. It preserves the modular monolith and the KSh 0
cost target.

Planned checkpoints:

1. **Complete:** normalize route errors and validation responses;
2. **Complete:** harden production configuration and documentation exposure;
3. **Complete:** verify OpenAPI response contracts and database failure paths;
4. **Complete:** run the complete backend verification suite and update API
   documentation.

Verified results:

- structured validation, not-found, conflict, and database-error envelopes;
- OpenAPI declarations for relevant success and failure responses;
- production `/docs`, `/redoc`, and `/openapi.json` restrictions;
- automated production configuration tests;
- guarded Alembic `base` to `head` migration verification;
- 54 backend tests passing, with Ruff, compilation, lock, and diff checks
  passing.

The complete handoff report is
[`docs/MILESTONE_5_REPORT.md`](MILESTONE_5_REPORT.md). `/api/v1` routing and
request-ID validation remain explicitly deferred compatibility decisions.

Git checkpoint:

```text
test(api): verify production docs and migrations
```

### Milestone 6 — Frontend foundation

**Status: Complete and verified.**

Achievements:

- Next.js 15.5 App Router bootstrap in `apps/web`
- React 19 and strict TypeScript setup
- Tailwind CSS v4 integration
- responsive accessible application shell and entry page
- loading, error, and not-found boundaries
- focused Vitest/Testing Library test foundation
- lint, type-check, npm audit, and production build commands
- local frontend setup documentation

Verified results:

- clean `npm ci` installation with zero npm audit vulnerabilities;
- frontend lint passed;
- frontend type-check passed;
- frontend tests passed: 1 test;
- frontend production build passed;
- backend regression suite passed: 54 tests;
- backend Ruff, compilation, lock, and diff checks passed.

The complete handoff report is
[`docs/MILESTONE_6_REPORT.md`](MILESTONE_6_REPORT.md). Frontend/API
integration remains deferred to Milestone 7.

Git checkpoint:

```text
feat(frontend): establish Next.js foundation
```

### Milestone 7 — Frontend/API integration

Achievements:

- service list page
- create service form
- service detail page
- event creation flow
- resolve action
- loading/error/success handling
- frontend tests

Git checkpoints:

```text
feat: integrate service dashboard with API
feat: add service event interactions
```

### Milestone 8 — Quality gates and meaningful tests

Achievements:

- backend unit coverage
- integration tests
- API validation tests
- frontend behavior tests
- E2E smoke flow
- CI verification strategy

Git checkpoint:

```text
test: establish CloudXzen quality suite
```

### Milestone 9 — Docker and local reproducibility

Achievements:

- API Dockerfile
- web Dockerfile
- PostgreSQL Compose config
- build verification
- environment setup docs

Git checkpoint:

```text
build: containerize CloudXzen applications
```

### Milestone 10 — GitHub Actions CI

Achievements:

- PR workflow
- backend checks
- frontend checks
- container build
- dependency scanning
- required branch protection

Git checkpoint:

```text
ci: add automated quality pipeline
```

### Milestone 11 — Provider-agnostic IaC and deployment

Achievements:

- selected provider deployment files
- free-tier managed PostgreSQL
- application hosting
- production configuration
- HTTPS
- migration deployment
- smoke verification

Git checkpoints:

```text
infra: provision selected CloudXzen environment
feat: deploy CloudXzen to selected provider
```

### Milestone 12 — Observability and production readiness

Achievements:

- health verification
- structured logs
- Azure monitoring integration
- error monitoring
- secure deployment review
- incident runbook

Git checkpoint:

```text
feat: add production observability
```

### Milestone 13 — Documentation and portfolio polish

Achievements:

- final README
- architecture docs
- API docs
- database docs
- deployment docs
- ADRs
- build log

Git checkpoint:

```text
docs: complete CloudXzen engineering documentation
```

## 18. Smaller achievements inside each milestone

Each milestone should contain several independent, meaningful job-level achievements, not just large phases.

Examples:

- repository foundation
- backend bootstrapping
- database connection
- migration success
- first working endpoint
- validation
- test setup
- frontend API integration
- Docker running locally
- CI green
- deployment resources provisioned
- deployment working
- observability verified
- documentation polish

These are the natural places for Git checkpoints.

## 19. Git commit/push checkpoints

The intended pattern is:

```text
Achievement
→ verify
→ git status
→ inspect diff
→ git add
→ git commit
→ git push
→ continue
```

Do not wait until the whole phase is done. Prefer meaningful checkpoints after stable increments.

## 20. Major technical risks and unknowns

### Product risks

- status semantics can become ambiguous without clear rules
- event-driven workflows may need more structure than a small product should require
- authentication may expand scope before the MVP is stable

### Backend risks

- status derivation could drift if it is stored in multiple places
- transactions may be misapplied around event creation
- error contracts may drift without strong API tests

### Database risks

- timestamp/timezone ambiguity
- migration drift across environments
- shallow test isolation

### Frontend risks

- UI abstraction can become over-engineered
- component boundaries may be wrong between server and client
- forms may not handle API errors cleanly

### CI/CD risks

- backend and frontend dependency setup may become slow
- PostgreSQL in CI may not match local behavior
- databases and deployments may be mixed across environments

### Deployment-provider risks

- pricing and platform availability can change
- provider free-tier limitations need careful comparison
- deployment secrets must be managed correctly

### Scope risk

The biggest technical risk is unnecessary infrastructure: Redis, Kafka, Kubernetes, microservices, queues, and caching should not be introduced before there is a concrete requirement.

## Recommended first actual implementation milestone

The first actual implementation step should be:

### Milestone 0 — repository foundation and product contract

This should be limited to:

1. final product/domain confirmation
2. MVP and non-goals
3. repository conventions
4. `.gitignore`
5. `.env.example`
6. README update
7. architecture doc skeleton
8. ADR explaining modular monolith and why the project does not need Redis, Kafka, microservices, or Kubernetes yet

This milestone should be approved before any real app code begins.

## Final note

The project is intentionally modest in product scope while producing a high-value engineering portfolio. The engineering rigor is the main output: architecture, testing, CI/CD, Docker, provider-portable IaC, deployment, observability, security, documentation, and disciplined Git workflow.

This roadmap is the correct planning baseline before implementation begins.
