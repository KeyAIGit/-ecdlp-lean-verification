# The autonomous engine

How this repository proves theorems **without a human in the loop** — and, honestly, where
that stops and human/orchestrated work is still needed.

## The loop

`​.github/workflows/autonomous-engine.yml` runs on a weekly schedule (and on manual
dispatch). One run is three stages:

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

3. **Surface** — the accepted nodes are opened as **one draft PR**. `main` is never touched;
   CI's own `lake build` + no-sorry + axiom-audit gates **re-verify each node independently**
   on the PR before a human merges.

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
the weekly schedule runs on its own: you only ever see draft PRs to review — no prompting.

## Honest scope — what it does and does not do

**Does, unattended:** discovers and closes the *reachable* tail — group/field-algebra
identities, abstract DL-crypto protocol facts (ECDSA/Schnorr/SSS-style), secp256k1-concrete
corollaries, and self-gaps (things asserted in prose but not fully proved). Each is
kernel-verified before it reaches a PR.

**Does not, yet:** reliably produce the *hardest* novel results. The multi-week landmarks in
this repo (the `n=3,5,7` torsion bridges, the `#E[n]≤n²` point count) needed **orchestration**
— an audit fanning out, Fable designing sympy-verified certificates, parallel build agents,
independent axiom review. `agent_day.py`'s single propose→verify→repair loop is weaker than
that. So the engine is best understood as the **autonomous tail** of the pipeline: it keeps
the reachable frontier harvested between the deeper, human-directed campaigns — not a
replacement for them.

**And never:** breaks secp256k1. That is a lottery ticket against a proven **generic** (and
**classical**-only) lower bound — a real theorem about black-box algorithms, not an
unconditional one against all algorithms, and provably false against quantum ones (Shor).
Breaking the curve is not a goal (see `BARRIERS.md`).

## Pieces

| File | Role |
|---|---|
| `.github/workflows/autonomous-engine.yml` | the scheduled orchestrator (discover → prove → draft PR) |
| `scripts/autonomous_discover.py` | LLM discovery → `targets/queue.json` (has `--dry-run`) |
| `scripts/agent_day.py` | budget-bounded prove loop over the queue |
| `scripts/agent_prove.py` | single-target propose → server-verify primitives (reused) |
| `scripts/generator.py` | deterministic corpus → stems (Layer 3; now exhausted) |
| `.github/workflows/prove.yml` | the older tier-0 tactic-ladder loop (Featherless models) |
| `targets/queue.json` | the current target batch (regenerated each run) |
