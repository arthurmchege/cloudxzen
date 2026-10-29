# CloudXzen Web

The CloudXzen web application is the Next.js 15 App Router frontend. It uses
the existing root `/services` FastAPI contract to display services and event
history and to register services.

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

The browser uses a same-origin `/api-backend` proxy by default. Set
`API_BASE_URL` when starting Next.js to point the proxy at the backend, for
example:

```bash
API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

`NEXT_PUBLIC_API_BASE_URL` may be set when a browser-accessible API origin is
explicitly configured, but it is not required for local development. Never
put credentials in browser-exposed environment variables.

The current frontend consumes `/services` rather than `/api/v1` because the
implemented and tested backend contract is root-level. See
`docs/MILESTONE_7_REPORT.md` for the compatibility decision.
