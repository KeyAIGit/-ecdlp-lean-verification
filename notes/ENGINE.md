# The autonomous engine

How this repository proves theorems **without a human in the loop** — and, honestly, where
that stops and human/orchestrated work is still needed.

## The loop

`​.github/workflows/autonomous-engine.yml` runs on manual dispatch (`workflow_dispatch`;
the weekly cron was removed in the 2026-07 security audit, so the whole autonomous layer
is dispatch-only). One run is three stages:

```
DISCOVER ──▶ PROVE ──▶ SURFACE
```

1. **Discover** — `scripts/autonomous_discover.py`.
   The deterministic corpus generator (`scripts/generator.py`) is **exhausted**: it emits 0
   templated stems now, and the remaining corpus claims are barrier-blocked (Weil pairing,
   lattice reduction, Semaev) or need genuine mathematics. So discovery is LLM-driven: the
   model is shown the current verified base (every proved theorem name) and the barrier map,
   and asked for the next batch of **new, closeable-now, non-barrier-blocked** targets — the
   same judgment the interactive landability audit used to surface ECDSA / Shamir / scalar-
   group / `#E[2]≤4`, none of which were corpus targets. Output → `targets/queue.json`.

2. **Prove** — `scripts/agent_day.py` (reusing `agent_prove.py`'s audited primitives).
   For each queued target: the model proposes a complete Lean file, the **warm server**
   verifies it with `lake env lean` (the Lean kernel is the only judge), and rejections are
   fed back for repair — budget- and wall-clock-bounded. Every kernel-clean node is kept.

   **Fable-in-CI (`scripts/certify.py`).** When a target rests on a nontrivial algebraic
   identity (a polynomial identity, an exact `linear_combination` cofactor, a resultant),
   discovery attaches a `certify` claim. Before proving, a model designs a **self-contained
   sympy script** that verifies that identity by exact symbolic computation; the engine
   *runs* it and only a script printing `CERT_OK` counts. The verified certificate (explicit
   polynomials/cofactors) is then prepended to the prover prompt, so the prover transcribes a
   machine-checked identity instead of guessing one — the same division of labour (Fable
   designs → build agent transcribes) that made the deep torsion results tractable
   interactively. sympy only proposes; the Lean kernel still judges.

3. **Surface** — the accepted nodes are opened as **one draft PR**. `main` is never touched;
   CI's own `lake build` + no-sorry + axiom-audit gates **re-verify each node independently**
   on the PR before a delegated maintainer decides whether to merge.

## Safety (why this can run unattended)

- **Draft PRs only.** The engine never edits `main`. A human reviews and merges.
- **The kernel is the judge, twice.** The server's `lake env lean` gates acceptance; CI's
  `lake build` + no-sorry gate re-verify on the PR. `agent_prove.py` also refuses any
  candidate containing `sorry`/`admit`/`axiom`.
- **Hard budget caps.** Per-run USD and wall-clock caps (`budget_usd`, `time_budget_min`),
  backstopped by the Anthropic Console spend limit (set this — see below).
- **Fails safe.** With no `ANTHROPIC_API_KEY` the run is a green no-op (zero spend).

## One-time human setup (then it is automatic)

Set three repository secrets (Settings → Secrets and variables → Actions), once:

| Secret | Role |
|---|---|
| `ANTHROPIC_API_KEY` | the "brain" — the model that proposes Lean and discovers targets |
| `SSH_PRIVATE_KEY` | key to the warm Lean server (the "verifier") |
| `SERVER_HOST` | the server host (`SERVER_USER` optional, defaults to `root`) |

Then, as an independent backstop, set a **spend limit in the Anthropic Console**. After that
each dispatched run works on its own: you only ever see draft PRs to review — no prompting.
(Re-enabling a cron is a one-line change, deliberately not made after the security audit.)

## Honest scope — what it does and does not do

**Does, unattended:** discovers and closes the *reachable* tail — group/field-algebra
identities, abstract DL-crypto protocol facts (ECDSA/Schnorr/SSS-style), secp256k1-concrete
corollaries, and self-gaps (things asserted in prose but not fully proved). Each is
kernel-verified before it reaches a PR.

**Does not, fully:** match orchestrated depth. The `certify.py` Fable-in-CI step closes part
of the gap — the unattended loop can now get a sympy-verified certificate for a hard algebraic
identity before proving, which is exactly what unlocked the deep torsion results. What it
still lacks versus the interactive campaigns is the *adaptive* orchestration around that step:
a multi-angle audit fanning out, several parallel build agents per target, independent
`#print axioms` review, and a human's judgment of which direction is worth the spend. So the
engine is best understood as the **autonomous tail** of the pipeline: it harvests the
reachable frontier (now including certificate-backed algebra) between the deeper, human-
directed campaigns — a strong complement to them, not yet a full replacement.

The maximal "literally the interactive pipeline on a schedule" is a further step: run Claude
Code itself headless in CI (with the Workflow/Agent tools + direct SSH verify), rather than
the raw-API `agent_day` loop. That is more faithful but harder to bound on cost and auth; it
is deliberately left as a follow-up on top of this controllable base.

**And never:** breaks secp256k1. That is a lottery ticket against a proven **generic** (and
**classical**-only) lower bound — a real theorem about black-box algorithms, not an
unconditional one against all algorithms, and provably false against quantum ones (Shor).
Breaking the curve is not a goal (see `BARRIERS.md`, `notes/SECURITY_SCOPE.md`).

## Pieces

| File | Role |
|---|---|
| `.github/workflows/autonomous-engine.yml` | the orchestrator, dispatch-only (discover → prove → draft PR) |
| `scripts/autonomous_discover.py` | LLM discovery → `targets/queue.json` (has `--dry-run`) |
| `scripts/certify.py` | Fable-in-CI: model designs a sympy certificate, we run it (has `--self-test`) |
| `scripts/agent_day.py` | budget-bounded prove loop over the queue (runs the certify step) |
| `scripts/agent_prove.py` | single-target propose → server-verify primitives (reused) |
| `scripts/generator.py` | deterministic corpus → stems (Layer 3; now exhausted) |
| `.github/workflows/prove.yml` | the older tier-0 tactic-ladder loop (Featherless models) |
| `targets/queue.json` | the current target batch (regenerated each run) |
