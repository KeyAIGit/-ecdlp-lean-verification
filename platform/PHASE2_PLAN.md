# Phase 2 — the authenticated platform (build plan)

> Concrete, honest build plan for the platform layer of the machine-verifiable Research OS
> (`../PLATFORM_STRATEGY.md`). Phase 1 is done: two live domains (secp256k1, P-256) prove the
> engine generalizes. Phase 2 turns the static, git-backed asset into a **hosted, multi-user
> web app with authentication and a private area** — and, later, hosted verification.
>
> This directory (`platform/`) is a **staging scaffold**, not the deployed product. It is not
> built or gated by the Lean CI. When it stabilizes it should move to its own repository (the
> private material must not live in this public repo — see `../notes/PRIVATE_AREA_DESIGN.md`).

## What only you can provide (provisioning checklist)

The platform cannot be fully stood up from the build sandbox — it needs accounts and secrets
that are yours:

- [ ] A **Vercel** (or Cloudflare Pages) project to host the app.
- [ ] A **Clerk** application (auth) → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`.
- [ ] The **domain** wiring (e.g. `app.keyai.org`) once deployed.
- [ ] Later steps only: a **Postgres** database (Neon/Supabase) and a **verification worker** host.

The recommended stack is Next.js (App Router) + Clerk on Vercel — the fastest standard path.
A no-code alternative for step 1 is Cloudflare Access on a gated static deploy (no app), but
it does not grow into per-user features, so it is a dead end for the full platform.

## Increments (each is a deployable milestone, not a big-bang)

### Step 1 — Authenticated read-only platform  *(this scaffold; effort: days)*
- Public routes: domain portfolio, pipeline, ledger — reading the **existing** truth layer
  (`domains/registry.json`, `data/stats.json`, `VERIFIED.md`) at build time. No database.
- `/research` — a **login-gated** area (Clerk) for private/speculative work. The private zone
  the strategy calls for, now behind real auth (unlike Pages, which cannot gate).
- **Exit:** an external user signs in and sees a gated page the public cannot.

### Step 2 — Persistence + accounts  *(weeks; data layer now scaffolded)*
- Add Postgres (users, domains, claims, submissions). Keep git as the export mirror.
- Move the private research content into the DB / private repo (also closes SECURITY task #36).
- **Exit:** per-user state persists; the truth layer is queryable, not just static JSON.

**Already scaffolded (no DB required to read the code):**
- `lib/db/schema.ts` (Drizzle) + `db/schema.sql` (plain-SQL equivalent) — the data model above.
- `lib/data.ts` is now a `DataSource` **interface** with two backends chosen by env:
  `lib/data.static.ts` (Step 1, reads the site) and `lib/data.db.ts` (Step 2, reads Postgres).
  Connecting a DB is a **config change** (`DATABASE_URL`), not a rewrite — pages/API call
  `getDataSource()` and never know which backend answered. The Lean counts stay authoritative
  from the repo in both backends.
- `scripts/seed.ts` (`npm run db:seed`) seeds domains from `domains/registry.json` and claims
  from the per-domain corpus, so the DB starts as a faithful copy of the git truth layer.
- Typed API routes `GET /api/stats`, `GET /api/domains`, `GET /api/domains?id=<domain>`.

To turn it on: provision Postgres (Neon/Supabase), set `DATABASE_URL`, `npm run db:push`
(or `psql -f db/schema.sql`), `npm run db:seed`. The app then serves domains/claims from the DB.

### Step 3 — Hosted verification (the moat)  *(1–3 months)*
- A sandboxed worker that runs `lake build` on a submitted target, resource-capped and queued,
  with the warm-server pattern (`../.github/workflows/server-run.yml`) as the seed.
- A logged-in user submits a statement and gets a kernel-checked verdict written to their
  account. This is the expensive core and the real product differentiator.
- **Exit:** submit-and-verify works end to end for an outside user.

### Step 4 — Community / commercialization  *(ongoing)*
- Collaboration, other verifiers (Coq/Isabelle/experiments), publication export, API, licensing.

## Data model (Step 2 target)

```
User      (id, clerk_id, email, role)
Domain    (id, slug, title, status, corpus_ref, ontology_ref, verifier)
Claim     (id, domain_id, statement, status[verified|planned], evidence_ref)
Submission(id, user_id, domain_id, statement, lean_source, verdict, log, created_at)
```

Step 1 needs none of this — it reads the git-backed JSON. The model is here so Step 1's
`lib/data.ts` shapes match what the DB will later serve.

## Honest scope

- Step 1 (this scaffold) is **auth + a gated read-only surface**. It does not verify anything;
  it re-presents the already-verified asset behind login. That is a real, shippable increment,
  not the whole platform.
- The valuable/expensive part is Step 3 (hosted verification). Do not sell submit-and-verify
  before it exists.
- Nothing here weakens the Lean invariant: the kernel is still the only judge; the platform is
  a presentation + workflow layer on top of the verified truth.
