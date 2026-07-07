# ENVIRONMENT_PLAN — a verified, navigable substrate for a future strong AI

**North star.** Build a machine-checked, machine-*navigable* knowledge **environment**
around ECDLP / secp256k1 that maximizes the leverage of a future strong reasoning system:
every fact kernel-verified (trustable without re-checking), every gap precisely mapped
(so the frontier is explicit), and the whole thing queryable and extensible by an agent.

**Honest boundary (held throughout).** This environment does **not** make ECDLP solvable
and does not contain a solution. ECDLP's hardness is computational (~2¹²⁸) and its open
directions may be permanent walls. What the environment does: give a future reasoner (a)
verified foundations to build on without blind trust, (b) a precise map of what is known
vs blocked and *by which missing foundation*, and (c) reusable machinery to extend itself.
That is the strongest thing that can honestly be built — a maximal-leverage substrate, and
a rigorous frontier map that is scientifically valuable even if the frontier never moves.

## The environment, as layers
- **L1 Verified core** — kernel-checked theorems (`VERIFIED.md`, `Ecdlp/Proved/*`). The
  ground truth. *Status: see **STATUS.md** for the live row/distinct count (canonical in
  `data/stats.json`); 0 sorry, no custom axioms.*
- **L2 Frontier map** — exactly what is open / blocked / by which missing Mathlib
  foundation (`BARRIERS.md`, `COVERAGE.md`). *The single most valuable layer for a
  reasoning AI: its map of the problem.*
- **L3 Navigable structure** — machine-readable graph + queryable data
  (`data/knowledge_graph.json`). Lets an agent ingest and query, not just read prose.
- **L4 Formalized objects** — GLV endomorphism (proved an *additive* endomorphism
  `glvHom`; the `[λ]` eigenvalue action `glvPoint = [λ]` is still **open**, gated on point
  counting), plus its cube relation φ²+φ+1=0, torsion, division polynomials; the pairing
  (missing) — the machinery reasoning runs on.
- **L5 Engine** — the AI+kernel formalization pipeline; a future agent could use it to
  extend the environment (self-improving substrate).

## Three tracks (run in parallel; each has checkpoints and a live metric)

### Track A — Frontier map, made machine-actionable  ⟵ highest leverage-per-effort
Turn `BARRIERS.md`/`COVERAGE.md` prose into a **structured, queryable** `data/frontier_map.json`:
each frontier item = {id, statement, status ∈ {verified, open, blocked}, blocking_foundation,
mathlib_gap, unlocks (which/how-many claims), refs}. An agent ingests this to see the whole
problem and where to push. Metric: **frontier completeness** = % of the 486 corpus claims
with an assigned status + (if blocked) a named blocking foundation.
- ✅ Checkpoint A1: `data/frontier_map.json` + generator, every barrier encoded; queryable
  (`scripts/build_frontier_map.py --query <foundation>`).
- 🔄 Checkpoint A2: assign status + blocking foundation to every claim. **~80.5% done**
  (frontier completeness — live figure in **STATUS.md**) (corpus areas + content
  heuristics, each tagged `confidence: corpus|heuristic`); the hardest-to-classify
  remainder still `unassigned` (see STATUS.md's corpus table for the live count;
  honestly left, not force-fit).
- Checkpoint A3: richer query interface + per-foundation "unlocks" claim lists.

### Track B — Depth: verified foundations, checkpointed DAG
Grow L1/L4 by closing reachable objects, each a kernel-verified rung; when a foundation is
missing, decompose it into a rung DAG and track k/N.
- ✅ Done: GLV endomorphism object (equation/nonsingular/map/slope/addX-addY/**additivity**/
  **cube relation φ²+φ+1=0**).
- Next rung ladder (medium → hard), tracked in `notes/FOUNDATIONS.md`:
  B1 division-polynomial degree → torsion-point-count bounds;
  B2 general `ψₙ`-vanishing ⟺ `n`-torsion equivalence;
  B3 **`E[n] ≅ (ℤ/n)²`** (torsion structure — feeds both pairing and point-counting);
  B4 **Weil pairing** `eₙ` (divisors → function fields → Miller) — the multi-month summit;
  B5 **point counting `#E(𝔽ₚ)=n`** (unlocks GLV `[λ]` + protocol instantiation).
Metric: rungs closed / total in the active DAG; each rung = one green CI theorem.

### Track C — Engine & extensibility
Keep the formalization pipeline reusable so the environment is self-extensible: the
generator (corpus → target stems), the prover loop — in practice the **zero-cost tactic
ladder** is the only tier that has landed proofs; external model-provers (Pythagoras-4B →
Goedel-V2-32B) have been *attempted with 0 accepted*, so promotion stays **human-in-loop** —
the CI trust gates (no-sorry, axiom audit, count/import guards). Optional: a warm server node (results
pushed to `server/candidates`) for throughput. Metric: targets auto-proposed & auto-verified.

## Measurement & reporting (so progress is legible)
- `COVERAGE.md` (auto): asset size + corpus triage + barriers — re-run `scripts/coverage_report.py`.
- Track-B DAG: rungs k/N in the active foundation (this file, updated per rung).
- Every substantive step is one kernel-verified CI commit → the git log *is* the progress log.

## Honest timeline
- Tracks A & C: days–weeks (mostly engineering + data).
- Track B mid-rungs (B1–B3): weeks each.
- Track B summit (B4 Weil pairing / B5 point counting): **months**, research-grade, high
  risk. Not compressible to a week by orchestration — orchestration buys *measurability and
  parallel breadth*, not a shortcut through a dependency chain of new deep mathematics.

## Current position
L1 strong and growing; L2/L3 exist (prose + graph) and are Track A's target to make
machine-actionable; L4 has the full GLV object; L5 exists but underused (server idle).
Immediate next: **Track A checkpoint A1** (machine-actionable frontier map) + **Track B**
continues toward `E[n] ≅ (ℤ/n)²`.
