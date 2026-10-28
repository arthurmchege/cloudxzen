# ADR-001: Modular Monolith and Zero-Cost Architecture

- **Status:** Accepted for Milestone 0
- **Date:** 2026-10-28
- **Decision owners:** CloudBench project owner and implementation agent

## Context

CloudBench is a student portfolio project with a small Service Reliability Journal domain. Its portfolio value comes primarily from engineering discipline: architecture, testing, CI/CD, Docker, deployment, observability, security, documentation, and Git workflow.

The project has a hard target cost of KSh 0. Azure for Students verification is not currently confirmed. The application therefore must not depend on Azure or any other paid provider, and it must remain portable between legitimate free-tier deployment options.

The domain does not currently require independent services, asynchronous processing, high-volume ingestion, distributed caching, or complex orchestration.

## Decision

CloudBench will start as a modular monolith with:

- a Next.js 15 frontend;
- a Python/FastAPI backend;
- a PostgreSQL database; and
- provider-specific deployment configuration isolated from application code.

The project will prioritize free/open-source software and free/student service tiers while avoiding unnecessary vendor lock-in and unapproved paid infrastructure.

The application will be designed so that local development works with local tools and PostgreSQL, including a local Docker database if useful.

## Why a modular monolith

This architecture provides:

- simple local development;
- one backend deployment unit;
- straightforward transactions;
- lower operational overhead;
- easier integration tests;
- fewer network failure modes; and
- a clear internal structure that can evolve later.

Microservices would add deployment coordination, network contracts, service discovery or configuration, duplicated operational concerns, and more difficult local testing. The current product does not justify those costs.

## Why not Redis, queues, Kafka, RabbitMQ, or Kubernetes

- **Redis:** no current caching, distributed session, or queue requirement exists.
- **Queues/Kafka/RabbitMQ:** the MVP has no long-running asynchronous workflow or high-volume event ingestion.
- **Kubernetes:** the scale and orchestration requirements do not exist, and its operational cost conflicts with the zero-budget constraint.

PostgreSQL and synchronous application operations are sufficient for the initial domain.

## Consequences

### Positive consequences

- The project can be developed and tested locally at no service cost.
- Deployment can target a free-tier provider later.
- The system is easier to explain, test, and operate.
- The application avoids premature vendor lock-in.
- Future extraction of a module remains possible if a concrete requirement appears.

### Negative consequences

- A single backend deployment cannot scale modules independently.
- Long-running asynchronous work is not available by default.
- High-traffic caching and distributed processing will require a later architectural decision.
- The team must preserve module boundaries inside the monolith as the codebase grows.

These are acceptable trade-offs for the current product scope and budget.

## Revisit criteria

Reconsider this decision only when a concrete requirement demonstrates that the modular monolith cannot satisfy the system, operational, or cost constraints. Candidate triggers include sustained traffic requiring independent scaling, a justified asynchronous workflow, or a deployment provider requirement that cannot support the current shape.
