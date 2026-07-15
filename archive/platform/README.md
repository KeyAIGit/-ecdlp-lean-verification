# platform/ — Phase-2 authenticated app (Step 1 scaffold)

The first deployable increment of the platform (`PHASE2_PLAN.md`): a Next.js + Clerk web app
with a **public overview** (re-presents the verified truth layer) and a **login-gated private
research area**. No database and no verification service yet — those are Steps 2–3.

> This is a **staging scaffold** inside the Lean repo. It is **not** built or gated by the Lean
> CI. When it stabilizes, move it to its own (ideally private-capable) repository — the private
> material must not live in this public repo (`../notes/PRIVATE_AREA_DESIGN.md`).

## What it does

- `/` — public: headline counts + domain portfolio, fetched from `NEXT_PUBLIC_DATA_BASE`
  (default `https://keyai.org`): `data/stats.json` and `domains/registry.json`. Always in sync
  with the repo, because it reads the repo's own published artifacts.
- `/research` — **requires sign-in** (Clerk). The private zone; placeholder content until Step 2.

## Run it (needs your accounts)

```bash
cd platform
cp .env.example .env.local        # then paste your Clerk keys
npm install
npm run dev                       # http://localhost:3000
```

1. Create a **Clerk** application → copy the publishable + secret keys into `.env.local`.
2. `npm run dev`, open the site, click **Sign in**, then visit **/research** — the public can't.

## Deploy (Vercel)

1. Push this repo; on **Vercel**, create a project with **Root Directory = `platform`**.
2. Add env vars `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` (and optionally
   `NEXT_PUBLIC_DATA_BASE`).
3. Deploy; wire a subdomain (e.g. `app.keyai.org`). `/research` is gated at the edge by
   `middleware.ts`.

Alternative gating with no app code (dead-ends before Step 2): Cloudflare Access on a static
deploy — see `PHASE2_PLAN.md`.

## Files

| File | Role |
|---|---|
| `middleware.ts` | Clerk edge auth; protects `/research(.*)`, everything else public |
| `app/layout.tsx` | shell + header with Sign in / UserButton (Clerk) |
| `app/page.tsx` | public overview (server component, reads the truth layer) |
| `app/research/page.tsx` | gated private area (placeholder) |
| `lib/data.ts` | `DataSource` interface + `getDataSource()` env-based factory |
| `lib/data.static.ts` | Step-1 backend: reads the published truth layer (no DB) |
| `lib/data.db.ts` · `lib/db/*` | Step-2 backend: Drizzle over Postgres (used when `DATABASE_URL` is set) |
| `db/schema.sql` · `scripts/seed.ts` | SQL schema + seeder (`npm run db:push` / `db:seed`) |
| `app/api/*` | typed JSON API: `/api/stats`, `/api/domains`, `/api/domains?id=` |

## Turning on the database (Step 2)

Optional — the app runs without it (Step 1). To back it with Postgres:

```bash
# provision Neon/Supabase, then in .env.local:  DATABASE_URL=postgres://...
npm run db:push      # apply lib/db/schema.ts   (or: psql "$DATABASE_URL" -f db/schema.sql)
npm run db:seed      # copy domains + claims from the repo truth layer into the DB
```

With `DATABASE_URL` set, `getDataSource()` serves domains/claims from Postgres; unset, it
reads the static site. The Lean counts stay authoritative from the repo either way.

## Honest scope

Step 1 is **auth + a gated read-only surface** over the already-verified asset. It verifies
nothing itself. The valuable/expensive part (hosted `lake` verification) is Step 3. The Lean
kernel remains the only judge of truth.
