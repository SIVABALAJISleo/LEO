# LEO AI Frontend — Deployment Guide

Production-ready deployment for the LEO AI frontend (TanStack Start + Vite,
targeting Cloudflare Workers by default).

## 1. Environment variables

All `VITE_*` variables are baked in at build time — you must rebuild whenever
you change them.

| Variable                | Required | Default                 | Description                                                                    |
| ----------------------- | -------- | ----------------------- | ------------------------------------------------------------------------------ |
| `VITE_LEO_API_BASE_URL` | ✅       | `http://localhost:8000` | Base URL of your Python LEO backend. Must be reachable from end-user browsers. |
| `NODE_ENV`              | –        | `production`            | Node environment.                                                              |
| `PORT`                  | –        | `3000`                  | Port for the self-hosted SSR server (Node target only).                        |

Copy `.env.example` → `.env` for local dev. In production, set these in your
host's dashboard (Cloudflare, Vercel, Netlify, etc.).

### Runtime API base override

End users can also point the app at a different backend from the in-app
**Settings → API base URL** page. That value is stored in `localStorage`
under `leo.api_base` and takes precedence over `VITE_LEO_API_BASE_URL`.

## 2. Scripts

```bash
bun install          # install dependencies
bun run dev          # local dev server
bun run build        # production build (SSR bundle + client assets)
bun run preview      # preview the production build locally
bun run lint         # eslint
bun run format       # prettier
```

## 3. Backend requirements

The frontend expects the LEO backend to expose:

- `POST /api/v1/auth/login`, `POST /api/v1/auth/signup` — JWT bearer flow
- `POST /v1/chat/completions` — OpenAI-compatible (streaming supported)
- `POST /v1/embeddings` — 384-dim vectors
- `POST /api/v1/leo/orchestrate` — router pipeline
- `GET /api/v1/leo/metrics` — Prometheus-style JSON metrics
- `GET/POST /api/v1/memory` — semantic memory CRUD
- `POST /api/v1/kg/query` — knowledge-graph 2-hop query

**CORS**: the backend must send `Access-Control-Allow-Origin` for your
deployed frontend domain, and allow the `Authorization` header.

## 4. Deployment targets

### Cloudflare Workers (default)

The project builds to a Worker bundle out of the box via
`@lovable.dev/vite-tanstack-config`. Deploy with `wrangler deploy` after
running `bun run build`. Set `VITE_LEO_API_BASE_URL` as a build-time secret.

### Static + Node SSR

```bash
bun run build
node .output/server/index.mjs
```

Put nginx or Caddy in front for TLS and gzip.

### Docker

```dockerfile
FROM oven/bun:1 AS build
WORKDIR /app
COPY . .
ARG VITE_LEO_API_BASE_URL
ENV VITE_LEO_API_BASE_URL=$VITE_LEO_API_BASE_URL
RUN bun install --frozen-lockfile && bun run build

FROM oven/bun:1-slim
WORKDIR /app
COPY --from=build /app/.output .output
COPY --from=build /app/package.json .
EXPOSE 3000
CMD ["bun", ".output/server/index.mjs"]
```

Build with:

```bash
docker build --build-arg VITE_LEO_API_BASE_URL=https://api.your-domain.com -t leo-frontend .
docker run -p 3000:3000 leo-frontend
```

## 5. Production checklist

- [ ] `VITE_LEO_API_BASE_URL` points at your production LEO backend (https).
- [ ] Backend CORS allows your frontend origin.
- [ ] JWT auth endpoints (`/api/v1/auth/login`, `/api/v1/auth/signup`) are live.
- [ ] TLS certificate installed on both frontend and backend.
- [ ] Rate limits configured on the backend (frontend surfaces 429s as toasts).
- [ ] `bun run build` completes without errors.
- [ ] Visit `/app/settings` after deploy to verify the API base URL.

## E2E, Smoke Tests & Observability

- `bun run test` — Vitest unit tests
- `bun run test:e2e` — Playwright end-to-end tests against a local production build with a fully mocked LEO backend (auth login, protected `/app`, streamed chat)
- `SMOKE_BASE_URL=https://your-host bun run smoke` — Deployment smoke test against a running artifact (home renders, `/app` gates auth, marketing routes respond 200)
- CI (`.github/workflows/ci.yml`) runs typecheck → lint → unit → build → Playwright e2e → deployment smoke on every push, and uploads the built artifact plus Playwright HTML report

### Streaming chat

`POST /v1/chat/completions` with `stream: true` must emit OpenAI-style SSE
(`data: {json}\n\n` ending with `data: [DONE]`). The chat UI streams tokens
incrementally, exposes a red **Stop** button while in flight, and falls back
to non-streaming JSON if the backend does not support SSE.

### Web Vitals & error reporting

The client collects CLS, INP, LCP, FCP, and TTFB via `web-vitals` and forwards
them (plus uncaught `window.error` / `unhandledrejection`) to `/api/telemetry`
using `navigator.sendBeacon`. Implement that endpoint on the backend (or a
proxy) to persist regressions and crashes. In dev, metrics also log to the
console under `[LEO vitals]`.

### Cache freshness

`benchmarks` and `memory` pages use stale-while-revalidate (React Query
`staleTime` + `placeholderData: (prev) => prev`), so navigating back to a
page renders the last known data instantly while a fresh fetch runs in
the background.
