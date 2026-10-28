# Milestone 0 Report

> **Historical report:** This report was created before the project was renamed from CloudBench to CloudXzen. References to CloudBench describe the former project identity at the time of Milestone 0.

## MILESTONE 0 COMPLETE

### Product

CloudBench — Service Reliability Journal

The planned MVP is a deliberately small journal for registering services, recording checks or incidents, reviewing current status and history, and resolving incidents.

### Completed

- Established repository hygiene and environment conventions.
- Added a root `.gitignore` for secrets, Python, Node.js, test output, local databases, IDE files, and OS files.
- Added `.env.example` with only the currently justified configuration placeholders.
- Replaced the placeholder README with a product, scope, status, stack, documentation, and cost overview.
- Added the initial provider-portable system architecture.
- Documented the modular monolith decision.
- Documented why Redis, queues, Kafka, RabbitMQ, Kubernetes, and unnecessary cloud services are not currently required.
- Added the zero-cost/free-tier policy with a target cost of KSh 0.
- Made Azure explicitly optional because Azure for Students verification is not confirmed.
- Documented that no paid service or cloud infrastructure may be activated without explicit approval.
- Added the original project roadmap and specification to the repository documentation.

### Files created or modified

- `.gitignore`
- `.env.example`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/COST_AND_FREE_TIER.md`
- `docs/CLOUDXZEN_ROADMAP.md`
- `docs/CloudXzen_Master_Project_Specification.md`
- `docs/CloudXzen.pdf`
- `docs/adr/ADR-001-modular-monolith-and-zero-cost-architecture.md`
- `docs/MILESTONE_0_REPORT.md`

### Architecture

The planned architecture is:

```text
Next.js 15 frontend
        |
        | HTTPS JSON API
        v
FastAPI modular monolith
        |
        v
PostgreSQL
```

The application core is provider-agnostic. Deployment will be selected later after verifying current free-tier rules and billing risk.

### Cost policy

- Target cost: KSh 0.
- Free and open-source tooling first.
- Free/student tiers may be used only after their current official terms are verified.
- Azure is optional.
- No paid services have been activated.
- No cloud infrastructure has been provisioned.
- No production database has been provisioned.

### Verification

The following checks were executed:

- Inspected repository status, branch, remote, and commit history before modifying files.
- Reviewed the existing roadmap and README before editing.
- Ran `git diff --check` before each documentation commit.
- Reviewed staged diffs and file statistics before each commit.
- Searched the new policy and architecture documents for cost, Azure, and unresolved placeholder language.
- Confirmed that no application source code, database schema, CI workflow, Dockerfile, or deployment configuration was created.

There are no application tests yet because application implementation has not started.

### Git

Meaningful checkpoints completed:

```text
4b35124 chore: establish repository and environment conventions
2cab96e docs: define initial system architecture
ab702c7 docs: document zero-cost deployment strategy
```

The checkpoints were created without force-pushing or rewriting history. The branch is `main`; the commits are ready to be pushed as the milestone is finalized.

### Known issues

- The application has not been implemented.
- No provider has been selected for deployment.
- Azure for Students verification remains unconfirmed.
- The exact free-tier hosting, database, monitoring, and CI/CD limits must be rechecked against official documentation at deployment time.
- No application test suite exists yet.

### Not implemented yet

- FastAPI application.
- Next.js application.
- PostgreSQL schema and migrations.
- Authentication.
- Service and incident workflows.
- Dashboard.
- Docker application images.
- GitHub Actions CI.
- Infrastructure-as-Code.
- Cloud deployment.
- Monitoring and error tracking.

### Next recommended milestone

After human approval, begin Milestone 1: bootstrap the FastAPI backend with configuration, a lightweight health endpoint, logging conventions, and its first automated API test.

## STATUS

READY FOR PROMPT 3
