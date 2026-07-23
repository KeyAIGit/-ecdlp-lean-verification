# ECDLP Lean formalization (v0.1)

![Verified theorems](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json)

A **kernel-verified Lean 4 + Mathlib library** about the secp256k1 elliptic curve and
the boundary of the classical attacks on its discrete-log problem (ECDLP), grown by a
propose-and-judge engine (models propose, the Lean kernel judges, only truth survives).
It is a *verified research substrate* plus an honest no-go map of what is provable now
vs blocked — **not** a solution to any hard problem.

This file is the front door for humans and low-context agents alike. Strategy lives in
`ROADMAP.md`; live numbers live in `STATUS.md`; exact attack-route decisions live in
`repo/ECDLP_DECISION_SUBSTRATE.json`; agents start at `AGENTS.md`.

## The one invariant (never violate)

**A green build means every built theorem is fully proved.** The Lean kernel is the only
judge of correctness. Never `sorry`/`admit`, weaken/delete a proof to pass CI, or add an
axiom. Open conjecture stems live in `Ecdlp/Targets/` (one `sorry` each) and are
intentionally never built or imported, so the invariant holds.

## Where the canonical numbers are

**`STATUS.md`** — the single generated snapshot (ledger rows, distinct results, proved
modules, `sorry` = 0, custom axioms = 0, corpus coverage). It is produced by
`scripts/gen_status.py` from `data/stats.json` (which **recounts the `VERIFIED.md`
ledger table mechanically**), `data/frontier_map.json`, and the ECDLP decision substrate.
Do not quote a count from any
other doc — prose may be stale; if in doubt, cite STATUS.md. Machine-readable:
`data/stats.json` · badge endpoint `badges/theorems.json`.

**Current research decision.** `RS-2026-07-22-001` evaluated all 17 registered
routes and selected none: no audited proposal currently clears the common gate
for the exact plain single-target objective. This parks experiments and
conditional foundation work; it does not claim that no future route can work.
New evidence enters through the candidate-neutral contract in
`experiments/framework/` and explicit reconsideration triggers.

## What NOT to claim

- It does **not** solve ECDLP on secp256k1 and offers **no shortcut**. secp256k1's
  concrete hardness is an **open conjecture**, not a theorem here.
- The generic-group `Ω(√n)` lower bound constrains **black-box** algorithms only; it says
  nothing about non-generic attacks. It is **classical** — Shor breaks ECDLP quantumly.
- The protocol library is **verified protocol algebra** (algebraic identities, now also
  instantiated on the concrete curve group) — **not** proven security of any deployed
  protocol: no adversary, no hash/random oracle, no probability model.
- The autonomous engine is dispatch-only (crons removed in a security audit); external
  model-provers were attempted with **0 accepted** — real progress is the tactic ladder
  + human/assistant formalization. Never present the engine as having produced the proofs.
- Never claim more than the kernel verifies. When unsure, state the limit plainly.

## Highlights (for a Lean / formal-methods reader)

The genuinely substantive results — each kernel-checked, each disclosed at its exact scope:

- **The exact curve cardinality `#E(𝔽_p) = n` — proved without Hasse or Schoof**
  (`CurveCardinalityExact.lean`): a curve-specific certificate (`n ∣ #E`,
  `#E ≤ 2p+1 < 3n`, and `E[2] = {O}` excludes `2n`). With it the whole point group is
  `E(𝔽_p) = ⟨G⟩ ≃+ ℤ/n` (`CurveFullGroup.lean`, `PointGroupEquiv.lean`) — cofactor 1 as
  a theorem, not an assumption.
- **Pratt primality certificates for `p = 2²⁵⁶ − 2³² − 977` and the group order `n`** —
  full recursive certificates discharging `Fact p.Prime` / `Fact n.Prime`; the most
  reusable artifacts in the repo (Mathlib lacks them).
- **Generic-group DLP lower bound — the combinatorial core** (`generic_dlog_query_bound`):
  the information-theoretic heart of Shoup/Nechaev `Ω(√p)` via affine collision counting,
  with BSGS/Pollard-rho upper bounds giving generic DLP `Θ(√n)`. Not the full adaptive
  Shoup theorem (no adversary/probability model — disclosed in-file).
- **The GLV/CM endomorphism, complete**: `(x,y) ↦ (βx, y)` proved an additive
  endomorphism (`glvHom`) with full slope/branch analysis, and the eigenvalue
  `glvHom = [λ]` **unconditional on the whole point group**
  (`secp256k1_glvHom_eq_zsmul_unconditional`) via the cardinality keystone.
- **Semaev summation polynomials `S₃`/`S₄` — first formalized in Lean/Mathlib**, plus a
  division-polynomial / torsion-disjointness ladder (`Ψ₂…Ψ₇` coprimality via explicit
  Bézout certificates) and the early Weil ladder (W1–W3).
- **Audited attack boundaries**: Pohlig–Hellman, anti-MOV/Frey–Rück (embedding degree
  > 100), anti-Smart/SSSA (non-anomalous, ordinary trace), quadratic-twist security —
  verified structural exclusions at their exact scopes. The detailed attack evidence,
  target applicability, and unresolved routes are separated in the attack registry and
  decision substrate; this is not a proof against every classical algorithm.

The rest of the ledger is verified engineering (Mathlib wrappers, protocol-algebra
identities, instantiations) — honestly ~10–15% substantive, ~85% routine; the split is
audited in `COVERAGE.md`.

**Trust base (precise).** No result depends on any *custom* axiom or `sorryAx` —
machine-enforced by the axiom-audit gate (`Ecdlp/AxiomAudit.lean` +
`scripts/check_axioms.py`). "0 axioms" means none beyond Lean/Mathlib's standard
`{propext, Classical.choice, Quot.sound}`. Results proved by `native_decide` (the
concrete 256-bit facts) **additionally trust the Lean compiler** via `Lean.ofReduceBool`
— a real extension of the trusted base, catalogued per-theorem in `TRUST_REPORT.md`.

## Layout

| Where | What |
|---|---|
| `Ecdlp/Proved/*.lean`, `Ecdlp/Secp256k1Verified.lean`, … | the built, gated proof base (see `VERIFIED.md` for the row-per-theorem ledger) |
| `Ecdlp/Targets/` + `targets/*.json` | open conjecture stems + the prover-loop registry (never imported/built) |
| `ResearchOS/` | second lake target: the non-ECC portability instance (elementary number theory) |
| `STATUS.md` · `data/` | generated truth layer: stats, frontier map, knowledge graph, registries |
| `BARRIERS.md` · `TRUST_REPORT.md` · `ABSTRACT_SCOPE.md` | the no-go map and the exact trust/scope boundaries |
| `ROADMAP.md` | the one strategy document (position, north star, program) |
| `AGENTS.md` · `CLAUDE.md` · `tasks/NEXT.md` | agent orientation, conventions, active queue |
| `REPOSITORY_ARCHITECTURE.md` + `repo/ARTIFACTS.yaml` | exhaustive whole-repo ownership map |
| `repo/FORMAL_SUBSTRATE.json` | machine-readable result families, critical path, blockers, and release boundary |
| `repo/ECDLP_DECISION_SUBSTRATE.json` | exact target, threat models, route dispositions, evidence gates, and foundation priority |
| `experiments/framework/` | candidate-neutral run contract and independent toy-curve output validator; no hypothesis authorization |
| `experiments/` · `domains/` · `notes/` (`notes/INDEX.md`) | validated experiments, domain registry, curated research memory |
| `archive/` | frozen history: superseded docs, raw traces, the undeployed platform scaffold |

## Build

Core verified file (no Mathlib): `lean Ecdlp/Secp256k1Verified.lean`.
Full project: `lake exe cache get && lake build`.
Toolchain pinned in `lean-toolchain` (Lean v4.31.0); Mathlib rev pinned in `lakefile.toml`.
CI is the verifier of record: build + no-sorry gate + axiom audit + consistency gates
(counts are recounted from the ledger table, so prose cannot silently drift). See `SETUP.md`.

## The engine (honest)

The scaffolded loop — discover → attempt → draft PR — is
`.github/workflows/autonomous-engine.yml`, **dispatch-only**. The zero-cost tactic ladder
plus human-in-loop promotion is what has landed every proof; the free Featherless prover
tier is dead from CI (Cloudflare bot-block of GitHub runners, verified 2026-07-15) and
external model-provers stand at 0 accepted. `notes/ENGINE.md` documents how the loop
works, its safety model (draft-only, kernel-judged twice, budget-capped), and exactly
what it does vs does not do autonomously. The prover-tier protocol and promotion rules
live in `AGENTS.md`.

## Authorship & AI disclosure

The human maintainer is the author and bears intellectual responsibility for every claim
of novelty and significance; correctness of each listed theorem is guaranteed by the Lean
kernel. AI tooling (assistant models for formalization, code, and proof search) was used
as an aid — it is disclosed here and is not an author. CI-bot commits are git metadata,
not authorship. License and the final author list are set by the maintainer.

## Where to go deeper

`STATUS.md` (canonical snapshot) · `repo/ECDLP_DECISION_SUBSTRATE.json` (route decisions) ·
`ROADMAP.md` (strategy & program) · `VERIFIED.md`
(the ledger) · `BARRIERS.md` (the no-go map) · `TRUST_REPORT.md` (what "verified" rests
on) · `PUBLISHABLE_UNITS.md` (the 3 standalone results) · `notes/INDEX.md` (research
memory) · `SETUP.md` (build + CI + regen) · `tasks/NEXT.md` (active queue).
