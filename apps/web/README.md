# CloudXzen Web

The CloudXzen web application is the Next.js 15 App Router frontend. Milestone
6 establishes the accessible application shell only; service and event API
integration is deferred to Milestone 7.

## Requirements

- Node.js 22 or a compatible Node.js 20+ release
- npm

## Setup

From `apps/web`:

```bash
npm ci
```

## Commands

```bash
npm run dev
npm run lint
npm run typecheck
npm test
npm run build
```

The page intentionally uses no live API data or credentials. The backend
continues to run separately from `apps/api`.
