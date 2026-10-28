# CloudBench

CloudBench is a small **Service Reliability Journal**: a full-stack application for recording service checks and incidents, reviewing recent service history, and resolving incidents.

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

### Planned

- Next.js web application.
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

Local development will use free and open-source tooling. PostgreSQL may run directly on the host or through Docker. Application-specific setup instructions will be added when the frontend and backend are bootstrapped.

Environment variables are documented in [.env.example](./.env.example). Never commit a real `.env` file or credentials.

## Documentation

- [Project roadmap](./docs/CLOUDBENCH_ROADMAP.md)
- [Master specification](./docs/CloudBench_Master_Project_Specification.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Cost and free-tier policy](./docs/COST_AND_FREE_TIER.md)
- [Milestone 0 report](./docs/MILESTONE_0_REPORT.md)
- [Architecture decisions](./docs/adr/)

## Cost policy

The target software/service cost is **KSh 0**. CloudBench will prioritize free/open-source software and free/student service tiers. Current pricing, quotas, restrictions, persistence, and billing risk must be verified against official provider documentation before deployment.

No paid service has been activated and no cloud infrastructure has been provisioned.
