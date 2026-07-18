# AUTONOMY.md — operating charter for unattended cycles

This file governs the **self-firing autonomous loop** that advances this repository
without a human in the loop for each step. A scheduled trigger fires one **cycle** per
hour; each cycle reads this charter plus `STATUS.md` and `tasks/NEXT.md`, then does one
well-scoped unit of productive work and stops.

It does **not** replace the domain protocol. Authority order:
`CLAUDE.md` (conventions) → `AGENTS.md` (prover-loop protocol) → this file (loop
governance) → `tasks/NEXT.md` (live queue) → `STATUS.md` (canonical machine snapshot).
If prose conflicts, `STATUS.md` wins on numbers; `AGENTS.md` wins on method; this file
wins on *when to act alone vs. escalate*.

The maintainer delegated merge authority for this loop. That delegation is real but
**bounded by the rails below**. The Lean kernel (CI) remains the sole judge of
correctness — always.

---

## The one invariant (never negotiable)

**A green build means every built theorem is fully proved.** Never `sorry`, `admit`,
weaken, delete, or axiomatize a proof to make CI pass. Never add a custom axiom.
Conditional hypotheses (`[Fact p.Prime]`) are hypotheses, not axioms. The kernel is the
only judge; CI is how the kernel votes here.

## The cycle (each firing does exactly this, then stops)

0. **Orient.** `git fetch origin && git reset --hard origin/main`. Read `STATUS.md`,
   `tasks/NEXT.md`, this file. Never rely on memory across cycles — state lives in git.
1. **Health-gate main (local, no API).** Scan the built base (everything under `Ecdlp/`
   except `Ecdlp/Targets/`) for real `sorry`/`admit`/`axiom`; run the full gate battery
   (`check_counts`, `check_status_consistency`, `check_semantic_drift`, `check_targets`,
   `check_repo_artifacts`, `check_domains`, `gen_result_registry --check`,
   `gen_source_registry --check`). If main is unhealthy, fixing it is the whole cycle.
2. **Reconcile in-flight work.** For each open PR on this account with no active session
   (orphaned parallel work): adversarially audit it for honesty/overclaim/hidden
   assumptions, reconcile onto current main, and land it **only on green CI** — stripping
   any novelty/priority claim (see Rails) from ledger rows before merge.
3. **Advance — one rung, or several independent ones in parallel.** Take the
   highest-priority actionable item(s) from `tasks/NEXT.md` (or the Priority ladder
   below). Prefer to **fan out** with a `Workflow`: draft several *mutually independent*
   rungs concurrently (e.g. the next open rung + an assessment of a harder one), each
   agent adversarially self-verifying its lemma names against real Mathlib source before
   returning. Then *I* re-review each draft independently (never merge a subagent's work
   on faith — reproduce the design and re-check the risky steps) and integrate the ones
   that survive. Sequential single-rung is the fallback when nothing else is independent.
4. **Integrate.** Wire the import into `Ecdlp.lean`; add the `#print axioms` line in
   `Ecdlp/AxiomAudit.lean`; append a **pure-fact** `VERIFIED.md` row; regenerate all
   derived artifacts; run the full gate battery **and** a hard conflict-marker scan as a
   *separate* step (never chain `git add && commit` past a marker scan); commit → push →
   PR → merge on green CI (build + docs-sync).
5. **Bookkeep.** Update `tasks/NEXT.md` (mark done, add the next), keep `STATUS.md`
   canonical, keep the queue 3–7 items.
6. **Report only if it matters.** Message the user (in Russian) only for: a milestone
   landed, a decision that is genuinely theirs, or a blocker. Otherwise end the cycle in
   silence.

## Inviolable rails (apply every cycle, no exceptions)

- **Merge only on green CI.** Never merge red; never merge to bypass a failing gate;
  never disable a gate to go green.
- **Verify before trust.** No local Lean toolchain exists here — the kernel check is CI's
  job, but the honesty / overclaim / hidden-assumption / scope checks are *mine*, and
  must run (adversarially, ideally a `Workflow`) before merging anything nontrivial.
- **Pre-verify every lemma name (the cheapest 10× there is).** A blind proof that fails
  CI on a mistyped Mathlib name burns a full ~10-min cold-build round trip for nothing.
  Before pushing, confirm each Mathlib lemma/def with **no in-repo precedent** against a
  real source: grep a Mathlib checkout if one exists (`.lake/packages/mathlib`, or a
  scratchpad clone), else GitHub code-search the pinned rev (monotone: absent on master ⇒
  absent at the older pin). The `smul_def` step of W3e-2 was retired exactly this way.
- **Anti-inflation.** No duplicate, padded, or restated results to move counts. Ledger
  rows state *what is proved* — never novelty, priority, "first-in-Lean", or superlatives
  (those are the maintainer's prerogative, and unverifiable by the kernel).
- **Honesty over sycophancy.** No overclaim in any artifact. Preserve the distinctions:
  pure-kernel vs. compiler-trusted (`native_decide` → `Lean.ofReduceBool`, directly or
  transitively); rational-points results vs. geometric/closure results; classical/generic
  security envelope vs. hardness proof vs. quantum (Shor breaks ECDLP — out of scope).
- **No secrets** in the repo; the model identifier must never appear in a commit, PR,
  code comment, or any pushed artifact — chat only.
- **Respond to the user in Russian.** No visualizations/artifacts as deliverables unless
  asked.

## Human-only — escalate, never act alone

Park the item and surface a concise note instead of proceeding when the action would:

- **Rewrite pushed git history** (`--amend` / `--force` / `--force-with-lease` / rebase of
  public commits) — needs explicit user consent *each time*.
- Change the **trust posture, TCB framing, or any public novelty/priority claim**.
- Touch the deferred **SECURITY item** (server IPs in public git history, `tasks/NEXT.md`
  / task #36) — rewrite-vs-accept is the user's call.
- **Bump the Mathlib / Lean pin** (`lake-manifest.json` / `lakefile.toml` /
  `lean-toolchain`).
- **Delete or overwrite work not created by this loop** when what is on disk contradicts
  how it was described — surface the contradiction instead.
- Remove a proved theorem or weaken a statement.

## Robustness (tokens, rate limits, container)

- **GitHub API rate-limit** (the account is shared with sibling containers): back off; do
  local-only work this cycle (drafting, local gates, git); retry the API next cycle. Never
  spin.
- **Usage / subscription cap** (the operation is bounded by the maintainer's subscription,
  not a metered API): a cap is a **pause, never a done**. The cycle ends where it is;
  everything worth keeping is already committed and pushed, so when the allowance refreshes
  (rolling window; also the weekly reset) the next scheduled firing resumes cleanly from git
  state. Never treat "hit the limit" as "work finished" — the queue in `tasks/NEXT.md` is
  the source of truth for what remains. No hand-off needed.
- **CI red after a push**: diagnose; fix forward with an additive commit, or revert the
  offending commit. Never merge red. If unfixable this cycle, park with a precise memo.
- **Blocked item**: park it with a memo naming exactly what resists (the failing induction
  step / the missing Mathlib API), then take the next item. If the whole queue is blocked,
  report to the user.
- **Container is ephemeral**: the trigger re-materializes the environment and re-clones on
  each fire; nothing lives in memory — only in git and `tasks/NEXT.md`.
- Never `sleep`-spin to wait on CI; use the scheduled cadence and background waits.

## Speed: the feedback loop is the bottleneck (the 10× question)

Throughput is gated almost entirely by **how fast a written proof is judged**. Today every
proof is written *blind* and judged only by GitHub CI — a ~10-min cold Mathlib build per
round trip. Closing that gap is where a ~10× lives. The levers, split by who can pull them:

- **Mine, in effect now:** (a) pre-verify every non-precedented lemma name against Mathlib
  source before pushing (kills the most common wasted round trip — see the rail above);
  (b) fan out independent rungs per cycle so drafting is parallel, not serial;
  (c) batch *independent, individually pre-verified* rungs into one CI run when they don't
  conflict, so one cold build amortizes several rungs (never batch things that share a risk
  — a batch fails as a unit). These raise throughput without any infra change.
- **The maintainer's to unblock (the real 10×, infra — surface, don't route around):**
  1. **Egress-allowlist the Lean toolchain host** (`release.lean-lang.org`, and the GitHub
     release assets for the toolchain tarball) in the environment's network policy. With
     the toolchain installed and the Mathlib cache warm, `lake env lean File.lean` gives
     **seconds** of local feedback — the CI round trip leaves the *inner* loop entirely and
     becomes only the final gate. This is the single highest-value change. The proxy is
     configured to *block* it (403 on CONNECT); per `/root/.ccr/README.md` I must report it,
     never tunnel around it.
  2. **Register the paid server as a self-hosted CI runner** with a pre-built `.lake`, so CI
     itself runs in seconds instead of rebuilding Mathlib cold — using the box already being
     paid for, while keeping CI as the trusted kernel gate.
  Both require access the container does not have; they are the maintainer's to set up once.
  The repo ships **`scripts/warm_lean.sh`** — once the allowlist is open it installs the
  pinned toolchain + Mathlib olean cache so `lake env lean File.lean` checks in seconds
  (it preflights egress and no-ops with a precise message while the hosts are still blocked).

## Planning & models

- Hard planning / strategy / adversarial design → prefer **Fable** (a `Workflow` agent with
  `model: 'fable'`). If Fable is usage-limited or unavailable, **do the planning on the
  default model and iterate to the same quality — never skip the planning step.** (This
  cycle Fable was limit-blocked; the strategy was done on Opus instead.)
- Routine drafting / verification / integration → the default model, fanned out as above.

## Priority ladder (the standing plan; `tasks/NEXT.md` holds the live detail)

1. **Health of `main`** — the invariant and the gate battery, always first.
2. **Reconcile orphaned parallel PRs** onto main (honest, CI-green, overclaim-stripped).
3. **Geometric torsion frontier** — the `ψₙ ↔ E[n]` critical path toward `E[n] ≅ (ℤ/n)²`
   for general `n` (the uniform separability of `[n]` is the one CORE open item; the
   `n ∈ {3,5,7}` instances land via the reconciliation) and onward to the **Weil-pairing**
   non-degeneracy substrate.
4. **Security/structure surface for secp256k1 & P-256** — extend proved structure
   (full-group `Module (ZMod n)`, twist/security certificates) where unblocked; park
   P-256 `#E = n` on the Hasse gap with an honest note.
5. **Protocol algebra & attack landscape** — additional honest identity-level results
   (malleability, extraction) that stay within `ABSTRACT_SCOPE.md`.
6. **Research-OS hygiene** — keep drift gates, provenance registries, and the public
   surface truthful and in sync.

Deep, honest, kernel-checked progress on one rung beats broad shallow additions. When a
rung is genuinely blocked upstream (Mathlib gap), record the no-go and move down the
ladder — a precise barrier is a first-class result, not a failure.
