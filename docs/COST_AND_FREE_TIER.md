# Cost and Free-Tier Policy

## Status

**Status:** Policy established. No paid service has been activated and no cloud infrastructure has been provisioned.

## Current budget

```text
Target cost: KSh 0
```

The zero-cost target is a hard project constraint. CloudXzen must remain useful and developable without purchasing software, domains, cloud credits, monitoring plans, or hosted databases.

## Software

The planned application stack is based on free or open-source software:

- Next.js, React, TypeScript, Tailwind CSS, Framer Motion, shadcn/ui, Radix UI, and Sonner.
- Python, FastAPI, Pydantic, SQLAlchemy, Alembic, pytest, and httpx.
- PostgreSQL.
- Git, GitHub, Node.js, Python, and Docker where appropriate.

Individual dependencies will still be reviewed for licensing, maintenance, security, and build requirements before they are added.

## Local development

Local development must not require a paid service:

- PostgreSQL can run locally or in a local Docker container.
- The frontend and backend can run with local development tools.
- Environment variables will be supplied through local, ignored files.
- Tests must use local or CI-managed isolated dependencies.

No hosted database is required for application development.

## GitHub

The project may use:

- a GitHub repository;
- GitHub pull requests and reviews;
- GitHub Actions for CI; and
- GitHub Student benefits where the account is eligible.

Current quotas and terms must not be assumed. The project will verify the official GitHub documentation and account-specific availability before depending on a capability. This document intentionally does not claim a specific quota.

## Cloud

Azure is currently optional:

- Azure for Students verification is not confirmed for this project.
- No Azure resource will be provisioned during Milestone 0.
- Azure must not be required for local development or application correctness.
- Azure may be evaluated later if current eligibility and free/student terms are verified.

The application must remain deployable to a legitimate free-tier alternative. Possible providers may include Render, Cloudflare, Vercel, Neon, Supabase, or another provider, but no provider is selected by this document.

## Future deployment evaluation

Before using any cloud provider, verify its current official pricing and terms. The evaluation must cover:

- free-tier availability and eligibility;
- quotas and rate limits;
- sleep/cold-start behavior;
- database persistence and retention;
- bandwidth and build limits;
- geographic availability;
- HTTPS;
- environment variables and secrets;
- logs and monitoring;
- CI/CD compatibility;
- commercial-use and student-program restrictions; and
- behavior when the free allowance is exceeded.

Free-tier availability, quotas, restrictions, sleep behavior, database retention, bandwidth, build minutes, and commercial-use restrictions must be verified against the provider's current official documentation before deployment.

## Unapproved paid services

Do not:

- subscribe to a paid service;
- enable paid cloud resources;
- purchase a domain;
- purchase a software license;
- upgrade a plan;
- activate paid monitoring; or
- provision infrastructure that may incur charges

without explicit approval.

If a service could incur charges, stop and report:

1. the service;
2. why it is needed;
3. its free-tier limitations;
4. what happens when the allowance is exceeded;
5. whether a credit card is required;
6. the possible billing risk;
7. a free alternative; and
8. whether the feature can be implemented without it.

## Cost-aware architecture

The project will not add Redis, Kafka, RabbitMQ, Kubernetes, microservices, paid monitoring, or a paid authentication provider merely to make the architecture appear more sophisticated. Each addition must solve a concrete requirement and pass a cost and operational-complexity review.
