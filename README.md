# CloudXzen

CloudXzen is a small **Service Reliability Journal**: a full-stack application for recording service checks and incidents, reviewing recent service history, and resolving incidents.

The product is intentionally modest. The primary goal is to demonstrate how to design, test, document, containerize, deploy, secure, and operate a real software system without buying unnecessary complexity.

## Product scope

The planned MVP will allow a user to:

- register a service or dependency;
- record a check or incident;
- view current status and event history;
- resolve an incident; and
- review a small health/status dashboard.

The MVP does not include external polling, alerting, billing, AI/ML, multi-region infrastructure, or microservices.

## Project status

### Implemented

- Initial repository and documentation foundation.
- Product and architecture roadmap.
- Zero-cost and provider-portable project policy.
- FastAPI backend foundation with a tested `/health` endpoint.
- Service schemas, repository functions, and `POST /services` and
  `GET /services` endpoints backed by PostgreSQL.
- Next.js frontend foundation with an accessible application shell and
  verified local quality/build commands.

### Planned

- Frontend/API integration and service workflows.
- FastAPI backend.
- PostgreSQL persistence.
- Automated unit, integration, API, frontend, and selected end-to-end tests.
- Docker-based local reproducibility.
- GitHub Actions CI.
- Provider-agnostic free-tier deployment.
- Observability and production security hardening.

Nothing is deployed yet. Azure is an optional future target, not a current dependency.

## Planned technology stack

### Frontend

- Next.js 15 with App Router
- React 19
- TypeScript
- Tailwind CSS v4
- Framer Motion
- shadcn/ui
- Radix UI Primitives
- Sonner

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL

### Engineering

- Git and GitHub
- Docker
- GitHub Actions
- Infrastructure-as-Code where deployment requires it
- Automated testing
- Structured logging and error monitoring where justified

Technologies listed as planned are not claims of completed implementation.

## Local development

Local development will use free and open-source tooling. PostgreSQL may run directly on the host or through Docker. The backend setup is documented in [apps/api/README.md](./apps/api/README.md), and the frontend setup is documented in [apps/web/README.md](./apps/web/README.md).

Environment variables are documented in [.env.example](./.env.example). Never commit a real `.env` file or credentials.

## Documentation

- [Project roadmap](./docs/CLOUDXZEN_ROADMAP.md)
- [Master specification](./docs/CloudXzen_Master_Project_Specification.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Cost and free-tier policy](./docs/COST_AND_FREE_TIER.md)
- [Milestone 0 report](./docs/MILESTONE_0_REPORT.md)
- [Milestone 1 report](./docs/MILESTONE_1_REPORT.md)
- [Milestone 2 report](./docs/MILESTONE_2_REPORT.md)
- [Milestone 3 report](./docs/MILESTONE_3_REPORT.md)
- [Pre-Milestone 2 remediation report](./docs/PRE_MILESTONE_2_REMEDIATION_REPORT.md)
- [PostgreSQL development strategy](./docs/POSTGRESQL_DEVELOPMENT.md)
- [Backend README](./apps/api/README.md)
- [Frontend README](./apps/web/README.md)
- [Milestone 5 report](./docs/MILESTONE_5_REPORT.md)
- [Milestone 6 report](./docs/MILESTONE_6_REPORT.md)
- [Architecture decisions](./docs/adr/)

## Cost policy

The target software/service cost is **KSh 0**. CloudXzen will prioritize free/open-source software and free/student service tiers. Current pricing, quotas, restrictions, persistence, and billing risk must be verified against official provider documentation before deployment.

No paid service has been activated and no cloud infrastructure has been provisioned.
