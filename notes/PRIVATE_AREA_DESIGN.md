# PRIVATE_AREA_DESIGN — a gated research area (public/private split)

> Direction doc, not private content. It describes *how* to stand up a login-gated private
> area and *what* belongs behind it. It contains no secrets. Decision on file: the private
> area is for **private research / drafts** (your + collaborators' speculative work), not an
> interactive verification platform (that was Phase 2 of the archived `archive/docs/PLATFORM_STRATEGY.md`; the scaffold lives in `archive/platform/`).

## The constraint that shapes everything

This repository is **public** and the site is served by **GitHub Pages** from it. Therefore
**everything here — every file, every page on `keyai.org` — is public.** A login button on
`keyai.org` would not make anything private; Pages cannot gate content. Real privacy needs
**two** things Pages does not provide:

1. a **private store** (a separate private repository or a database), and
2. a **host that enforces auth** (Cloudflare Access / Netlify / Vercel), on a separate
   subdomain — not Pages.

So "private area" = a **second, separate deployment**, not an edit to this site.

## Architecture (recommended)

```
  PUBLIC                                   PRIVATE (new)
  ───────────────────────────────         ───────────────────────────────
  repo: -ecdlp-lean-verification          repo: keyai-research-private   (NEW, private)
  host: GitHub Pages → keyai.org          host: Cloudflare Pages → research.keyai.org
  content: verified asset, honest         gate: Cloudflare Access (email allow-list)
           scope, barriers, pipeline,     content: speculative attacks, "lottery
           domain portfolio, papers                ticket", drafts, sensitive ops notes
```

- **Keep the public repo exactly as it is** — it is the brand: *verified and honest*.
- **New private repo** holds anything not ready for public honesty scrutiny.
- **Gate with Cloudflare Access** (recommended): no application code — you attach an access
  policy (an email allow-list, or Google/GitHub SSO) to `research.keyai.org`. Free tier
  covers a small team. Alternative: Vercel + Clerk if you later want real user accounts and
  app logic (that trends toward Phase 2).

## What goes where (the boundary rule)

| Public (`keyai.org`) | Private (`research.keyai.org`) |
|---|---|
| Kernel-verified ledger (`VERIFIED.md`) | Speculative attack ideas, the "lottery ticket" |
| Honest scope, barriers, coverage | Work-in-progress not yet honest-reviewed |
| Pipeline + domain portfolio | Unpublished drafts before a venue decision |
| Publishable units (final) | Sensitive ops notes (server IPs, infra) — see task #36 |

Rule of thumb: **if a claim is not yet true-and-honest enough to defend in public, it lives
private until it is.** Promotion private→public is a deliberate act, mirroring the existing
Targets→Proved promotion discipline.

## Migration steps (you run these — they need your accounts)

1. Create a **private** GitHub repo `keyai-research-private`.
2. Move speculative/WIP material there (do **not** copy secrets into the public repo). This
   is also the right moment to address task #36 — sensitive ops notes belong on the private
   side.
3. Connect the private repo to **Cloudflare Pages**; add a **Cloudflare Access** policy on
   `research.keyai.org` with an email allow-list (you + collaborators).
4. Add a small "Private research (login)" link from the public dashboard footer pointing at
   `research.keyai.org` — visitors see the link, but content requires auth.
5. (Optional, later) mirror the same `build_dashboard.py` generator into the private repo so
   the private area gets its own pipeline view over private domains.

## Effort & honest scope

- **~1–2 weeks**, mostly account setup + content migration; **no backend, no verification
  service**. This is *content gating*, not the interactive submit-and-verify platform.
- It does **not** move us toward Phase 2 by itself; it is orthogonal. It protects the public
  brand and gives sensitive/immature work a home — worth doing once there is real private
  material to justify it (don't build an empty vault).
- The Lean kernel, CI gates, and the "green = proved" invariant are **unchanged** — the
  private area is a *publishing boundary*, not a second source of truth.
