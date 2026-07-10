# PLATFORM_STRATEGY.md — from one verified case to a verified-research platform

> Honest strategy document. It says what exists, what does **not** yet exist, and what
> each next step actually costs. It is deliberately conservative: the value is real only
> if the claims stay true. `STATUS.md` remains the canonical live snapshot of the *asset*;
> this file is the canonical statement of *direction*.

## 1. The thesis in one sentence

We are building a **machine-verifiable Research OS**: take a research domain whose claims
can be *formally proved* (or *experimentally falsified*) and run every claim through one
disciplined pipeline —

> **Corpus → Frontier → Hypotheses → Tasks → Proofs/Experiments → Truth graph → Site → Papers**

— where the truth layer is decided by a machine (the Lean kernel today), never by prose.
**secp256k1 / ECDLP is instance #1**, chosen because it is hard, high-stakes, and has a
crisp verifiable core. It is a stress-test of the method, *not* the product. The product is
the method plus the engine that runs it.

## 2. Where we actually are (be honest)

**Phase 0 — reference instance — is essentially done.** What physically exists:

- A kernel-verified Lean 4 + Mathlib library: **220 ledger rows / ~184 distinct results,
  0 `sorry`, 0 custom axioms**, machine-enforced by CI (axiom audit + no-sorry gate).
- The full 8-stage pipeline, backed by real artifacts and **three consistency gates**
  (`check_counts`, `check_status_consistency`, `check_repo_artifacts`) + an agent-bundle
  routing layer, all drift-proofed by `docs-sync`.
- A working **engine**: generator (`scripts/generator.py`, corpus → open target stems),
  autonomous prover loop (`scripts/prover_loop.py`: zero-cost tactic ladder → Featherless
  models), verifier (the Lean kernel via `lake`), and a second execution surface (a warm
  rented server) for fast verification.
- A public static site on `keyai.org` (landing + generated dashboard).

**What does NOT exist yet, stated plainly:**

- No accounts, no login, no multi-user anything. The site is read-only and static.
- No database. The "truth layer" is **git files** (JSON / MD / CSV), not a queryable store.
- No hosted verification service. Verification runs in *our* CI / *our* server, not
  on-demand for an outside user.
- No second domain. The generalization is designed-for but **unproven** — every ontology,
  generator template, and corpus schema is still ECDLP-specific.
- The AI prover is **weak**: the tactic ladder + small models close only near-trivial
  targets. Non-trivial proofs are still human/Claude-driven.

So: we have **instance #1 + the engine + a conceptual architecture that is meant to
generalize** — and a static shop window. We are *not* close to a multi-tenant SaaS. We
*are* close to being able to prove the method generalizes, cheaply, before spending on
infrastructure.

## 3. The generalization insight (what makes it a platform, not a repo)

Everything domain-specific lives in three replaceable slots:

| Slot | ECDLP instance today | Platform interface (Phase 1 target) |
|---|---|---|
| **Corpus schema** | `data/KG_CLAIM_FORMALIZATION_v1.csv` (486 ECDLP claims) | a `Domain` provides a claim corpus + provenance |
| **Ontology / generator** | `Ecdlp/Ontology.lean` + `scripts/generator.py` templates | a `Domain` provides statement templates + a target emitter |
| **Verifier** | Lean kernel (`lake env lean`) | a `Verifier` interface: `verify(candidate) -> {ok, log}` |

The rest of the system — the pipeline stages, the gates, the truth graph, the site
generator, the agent bundles — is **already domain-agnostic in principle**. The platform is
what you get when those three slots become a documented plug-in contract instead of
hard-coded ECDLP files. A new domain (another curve; a different number-theory problem; a
combinatorics corpus; anything with a machine-checkable core) becomes: *implement the
`Domain` contract, drop in a corpus, point at a verifier.*

This is why the honest near-term move is **not** auth. It is **proving the three slots
really unplug** by standing up a second domain — even a small stub — behind the same
pipeline.

## 4. Phased roadmap with honest effort

Effort bands: **S** = days, **M** = 1–3 weeks, **L** = 1–3 months, **XL** = quarter+.
Each phase is a deliberate go/no-go, not an inevitability.

### Phase 1 — Generalize the engine + multi-domain static site  *(effort: M)*
No backend, no auth, still git-backed and static. Goal: **prove the method generalizes**.
- Extract the `Domain` and `Verifier` contracts (§3) as a documented interface; refactor
  ECDLP to be *an implementation of them*, not the whole thing.
- Add a `domains/` registry: **ECDLP live**, plus 1–2 honest **stubs** (a named future
  domain with an empty corpus and a "planned" status — exactly the "затычка" idea).
- Site gains a domain switcher: the landing shows a portfolio of domains, each linking to
  its own pipeline view; ECDLP is the only one with real numbers, the rest say "planned".
- **Exit criteria:** a second domain can be added by editing only its slot files; the site
  renders N domains; all gates stay green. This de-risks the entire platform thesis for
  the cost of a couple of weeks and **zero infrastructure**.

### Phase 2 — Backend + auth + hosted verification (MVP platform)  *(effort: L→XL)*
This is the real "platform," and it is a real engineering investment. In dependency order:
- **Persistence:** move the truth layer from git files to a database (projects, users,
  domains, claims, targets, proofs, runs). Keep git as an export/provenance mirror.
- **Auth:** user accounts via an off-the-shelf provider (Clerk / Supabase / Auth0). *This
  specific piece is **S–M*** — see §5. It is the smallest part of this phase.
- **Hosted verification worker:** the hard, expensive core — run Lean builds per submission
  in isolated, resource-capped sandboxes, queued, with caching. This is the moat *and* the
  main cost center (compute + sandbox security + queueing).
- **Web app:** a real front end (not a generated static page) where a logged-in user
  browses domains, reads the truth graph, submits a target, and gets a verdict.
- **Exit criteria:** an external user logs in, opens a domain, submits a statement, and the
  hosted verifier returns a kernel-checked verdict — with the result written to the truth
  layer under their account.

### Phase 3 — Community, multi-verifier, commercialization  *(effort: XL, ongoing)*
- More verifiers beyond Lean: Coq / Isabelle for other formal domains; **experimental /
  numerical validation harnesses** for domains that are not pure math (the "Experiment"
  half of the pipeline that is currently a placeholder).
- Collaboration, review workflows, publication export, an API, and the licensing/commercial
  track the roadmap already names (the engine as a reusable KeyAI asset).

## 5. The auth question, answered directly

**"How big a job is authentication?"** By itself, **small (S–M):** a hosted provider gives
you sign-up, login, sessions, and social auth in an afternoon-to-a-few-days of wiring.

But auth is the *tip* of the iceberg, and quoting it in isolation is misleading. Auth only
*means* something once there is (a) persistent per-user state to protect and (b) a backend
worth logging into. Those two — **a database and a hosted verification service** — are the
Phase-2 cost (**L→XL**), and they are what actually gate a real platform. So the honest
one-liner: **login is cheap; the platform behind the login is the expensive part.** Don't
let the ease of auth pull us into Phase 2 before Phase 1 has proven the thesis.

## 6. Risks and the moat

- **Moat = hosted, trustworthy verification at scale.** Anyone can render a dashboard; few
  can offer *"submit a claim, get a kernel-checked verdict, with a permanent honest record."*
  That is also the most expensive thing to build and run — the risk and the value coincide.
- **Prover quality risk.** The AI-prover is currently weak. The platform's value to
  outsiders depends on either the verified *library* growing, or the *engine* getting good
  enough that submit-and-verify is genuinely useful. Track this honestly; do not sell an
  autoprover we do not have.
- **Generalization risk.** The three slots may not unplug as cleanly as designed. **Phase 1
  exists precisely to surface this early, cheaply.** If a second domain is painful, that is
  the most valuable thing to learn before any backend spend.
- **Honesty risk.** The whole brand is "verified, and honest about scope." A single
  oversold claim on a public platform costs more than it earns. The consistency gates and
  the `native_decide` trust disclosure are the cultural template to carry into the platform.

## 7. Recommendation

**Do Phase 1 next; treat Phase 2 as a funded, deliberate decision, not a default.** Phase 1
is tractable with today's tooling (static, git-backed, no infra), directly realizes the
"our problem is one case, leave honest room for the others" vision, and de-risks the entire
platform bet for the price of a couple of weeks. When a second domain flows through the
pipeline cleanly and the site shows a portfolio with ECDLP as case #1, *then* the backend +
auth + hosted-verification investment is a decision made on evidence, not on hope.

---
*This document is direction, not a promise. Every number about the asset is owned by
`STATUS.md`; every effort band here is a considered estimate, not a commitment.*
