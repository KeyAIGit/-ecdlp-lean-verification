# NEXT - active Research OS queue

This file is the small-context task queue. Keep it short: 3-7 active tasks,
each with a contract that an agent can execute without rediscovering the
project from scratch.

> **Unattended operation:** an hourly self-firing cycle advances this queue per
> `AUTONOMY.md` (loop governance: rails, human-only escalations, robustness). The
> kernel/CI is the sole judge; merges happen only on green CI; novelty/priority
> claims never enter the ledger. Read `AUTONOMY.md` before acting as the loop.

Canonical start order for agents:

1. Read `STATUS.md`.
2. Read this file.
3. Read `experiments/HYPOTHESES.yaml` only when the task touches hypotheses,
   experiments, frontier interpretation, or publication planning.

If prose elsewhere conflicts with `STATUS.md`, `STATUS.md` wins. If this file
conflicts with `STATUS.md`, update both in the same PR and run the consistency
checks.

## Active Tasks

### TASK-001 - Harden the Research OS truth layer

Kind: ops | data | site
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Low-context agents and public readers need one reliable route
from machine facts to next work.
Inputs:
- `STATUS.md`
- `data/stats.json`
- `data/frontier_map.json`
- `data/knowledge_graph.json`
- `index.html`
- `dashboard.html`
Expected output:
- A drift gate that verifies stats, frontier, graph, status, site counters,
  task queue, and hypothesis registry agree at the obvious machine-readable
  seams.
Exit criteria:
- `python3 scripts/check_counts.py` passes.
- `python3 scripts/gen_stats.py --check` passes.
- `python3 scripts/check_status_consistency.py` passes.
Files allowed to edit:
- `scripts/check_status_consistency.py`
- `scripts/gen_status.py`
- `.github/workflows/ci.yml`
- `.github/workflows/docs-sync.yml`
- `STATUS.md`
- `tasks/NEXT.md`
- `experiments/HYPOTHESES.yaml`

### TASK-002 - Export small/medium/large agent bundles

Kind: ops | agent
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Small-context agents should not waste turns reconstructing the
same orientation from scattered prose.
Inputs:
- `STATUS.md`
- `tasks/NEXT.md`
- `data/stats.json`
- `data/frontier_map.json`
- `VERIFIED.md`
- `BARRIERS.md`
- `notes/FOUNDATIONS.md`
- `notes/SECURITY_SCOPE.md`
Expected output:
- `scripts/export_agent_bundle.py`
- Generated bundle files under a documented output path or ignored cache path.
Exit criteria:
- Small bundle contains only the current status, active queue, and core machine
  counts.
- Medium bundle adds ledger/barrier/security/foundation context.
- Large bundle can include graph excerpts and task-relevant Lean files.
Files allowed to edit:
- `scripts/export_agent_bundle.py`
- `AGENTS.md`
- `README.md`
- `.gitignore`

### TASK-003 - Add dashboard Sync Health

Kind: site | data
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: The public surface should show whether the Research OS state is
fresh and internally consistent.
Inputs:
- `scripts/check_status_consistency.py`
- `data/stats.json`
- `data/frontier_map.json`
- `data/knowledge_graph.json`
- `STATUS.md`
- `scripts/build_dashboard.py`
Expected output:
- A dashboard section or tab that reports sync health, canonical counts, and
  regeneration commands.
Exit criteria:
- Dashboard displays current ledger rows, distinct results, frontier
  completeness, graph theorem count, and last regeneration source.
- Consistency check covers the machine-readable values used by the dashboard.
Files allowed to edit:
- `scripts/build_dashboard.py`
- `dashboard.html`
- `index.html`
- `scripts/check_status_consistency.py`

### TASK-004 - Formalize experiment manifests

Kind: experiment | data
Hypothesis: `H5_SEMAEV_WINDOW`
Why it matters: Negative computational results should compress the search space
instead of disappearing into notes.
Inputs:
- `experiments/HYPOTHESES.yaml`
- `notes/ENGINE.md`
- `notes/SECURITY_SCOPE.md`
- `BARRIERS.md`
Expected output:
- A minimal experiment manifest schema for reproducible runs.
- A first Semaev/Groebner benchmark task contract.
Exit criteria:
- Every experiment run records hypothesis id, script, input dataset, commit,
  machine profile, and result summary.
Files allowed to edit:
- `experiments/`
- `datasets/`
- `scripts/`
- `notes/`

### TASK-005 - Weil pairing, ground one rung per cycle (primary) + general-`n` separability

**STANDING DIRECTIVE (maintainer, 2026-07-18): grind the Weil pairing autonomously,
one rung per cycle, per `notes/WEIL_LADDER.md`.** Each cycle: take the top un-done rung
of the cycle queue (W3-eval → W4 reciprocity → W5 `eₙ`/bilinear/non-degenerate), draft →
CI (kernel) judges → adversarially verify → merge on green (pure-fact ledger row, no
novelty claims). A rung that is a genuine Mathlib gap and resists an honest cycle → freeze
a precise blocker in `BARRIERS.md`, mark the target `blocked`, take the next independent
rung. **Progress (2026-07-18): W3e-1** (`divEval` multiplicativity, `WeilDivisorEval.lean`),
**W3e-2** (Miller-representative scaling law + conditional representative-independence,
`WeilDivisorRepIndep.lean`) **and W3e-3** (raw-value domain: support-disjointness → joint
regularity + `divEval` unit law, `WeilMillerEval.lean`) **are landed**; **W4-1** (Weil
reciprocity) **is a frozen no-go** (`BARRIERS.md` §B3). **The reachable Weil-evaluation
scaffolding is now complete** — W3e-4 (`millerEval^n = 1`), W4-2, and all of W5 (`eₙ`,
bilinear/alternating/non-degenerate) each depend on the blocked W4, so the Weil track is
parked at the Mathlib pin.

**REACHABLE SINGLE-CYCLE FRONTIER IS SATURATED (empirically confirmed 2026-07-18).** A
cycle-by-cycle audit found every remaining critical-path *leaf* already landed, general `n`:
**N4** degree/monic (`secp256k1_Φ_natDegree`/`_monic`, `NumeratorDominates.lean`), **N5**
coprimality (`secp256k1_isCoprime_Φ_ΨSq (n:ℤ)`, `DivisionPolynomialCoprime.lean`), the scalar
no-consecutive-zeros engine (`normEDS_not_consecutive_zeros`, unconditional), small-`n` N7
(`n=2,3,4,5`), the `E[n]≅(ℤ/n)²` structure for `n∈{2,3,5,7}`, and the whole Weil W3-eval layer.
**The only remaining items are the two genuinely hard gates:** (a) **N7 uniform**
(`x∘[n]=Φₙ/ΨSqₙ` in `k(E)` for all `n` — a large induction, "effort not theory") and
(b) **N10 separability** (`[n]*ω=nω`, the one CORE-by-theory item). Neither is a single blind-CI
rung; both need a **multi-cycle focused grind with fast feedback**.

**FAST-FEEDBACK LEVER IS LIVE (confirmed 2026-07-18).** The `server-run.yml` bridge works: a
`workflow_dispatch` succeeded end-to-end (step "Run command on server" green in ~9 s), SSHing to
the maintainer's server and running `lake env lean` on its warm Lean+Mathlib toolchain — and a
prior successful run dates to 2026-07-10, so the secrets (`SERVER_HOST`+`SSH_PRIVATE_KEY`) have
been set and the box bootstrapped all along (an earlier "blocked on maintainer secrets" note was
wrong — the bridge was never tested until now). **Workflow for the grind:** draft a proof locally
→ dispatch `server-run.yml` with a command that fetches the branch/patch and runs
`lake env lean <file>` (single-file, seconds on the warm box; ~15-30 s round trip) to pre-verify
BEFORE pushing → only push the CI-gated PR once the server is green. This makes N7-uniform /
N10-separability tractable.
**Loop directive (UPDATED): the fast-feedback lever is available — begin the N7-uniform grind,
using `server-run.yml` for single-file pre-verification each iteration; the cloud `ci.yml` (kernel)
remains the sole merge gate (the server is a fast pre-check only, never the trust root).** Do not
manufacture single-cycle filler; the remaining work is the two hard gates, now attackable. Reopen
the Weil track only if the pin gains residue/tame-symbol/divisor-degree machinery.

**N7-UNIFORM BUILD — brick 1 landed (2026-07-18, PR #200).** The maintainer's "build"
directive committed to constructing the N7-uniform infrastructure incrementally. First brick:
`Ecdlp/Proved/MultiplicationXCoordinateRing.lean` — the coordinate-ring translation
`φₙ·ΨSqₙ = Φₙ·ψₙ²` (`mk_ψ_sq`, `mk_φ_mul_ΨSq`), curve-generic, all `n:ℤ`, over Mathlib's
`mk_ψ`/`mk_Ψ_sq`/`mk_φ` congruences. Server-prechecked (`LEAN_OK_S1`, ~4.5 s warm) then CI-gated.
This is node **S1** only (coordinate-ring identity); the Point-level map `x([n]•P)=φₙ(P)/ψₙ(P)²`
on `E(k)` (node **S3**) still needs the multiplication-by-`n` coordinate map, absent from Mathlib.
**Brick 2 landed (2026-07-18, PR TBD):** `Ecdlp/Proved/DivisionPolynomialDoubling.lean` — the
**S2 ω-prerequisite** `ψₙ ∣ ψ₂ₙ` (`ψ_two_mul`: `ψ₂ₖ = ψₖ·complEDS₂…`; `ψ_dvd_ψ_two_mul`), curve-generic,
all `k:ℤ`. Scouting found that Mathlib now carries the scalar 2-complement `complEDS₂`
(`normEDS_mul_complEDS₂`/`normEDS_dvd_normEDS_two_mul`, `NumberTheory/EllipticDivisibilitySequence.lean`),
so the "as a start … `ψₙ∣ψ₂ₙ`" step the ω-`TODO` names is now a direct specialization, not an induction.
Server-prechecked (`LEAN_OK_S2`) then CI-gated. `ωₙ` itself still **not** defined (needs the `÷2`
well-definedness — Mathlib's open `TODO`), no `Point`-level claim.
**Reachable clean substrate is now exhausted (assessed 2026-07-18, after S1+S2).** The `÷2` step
toward defining `ωₙ` reduces (given S2's `ψ₂ₙ/ψₙ = complEDS₂ …`) to `2 ∣ (ψ₂ₙ/ψₙ − ψₙ(a₁φₙ+a₃ψₙ²))`
in `R[X][Y]` — vacuous when `2` is invertible (secp256k1's `𝔽_p`, any char `≠ 2`), but in full
generality needs the char-`0` universal ring `ℤ[A₁..A₆][X][Y]` + specialization, which **Mathlib
lacks** (no `WeierstrassCurve.Universal`). Crucially, **even a defined `ωₙ` proves nothing** without
step (iii), the `Point`↔`ω/ψ` coordinate `[n]`-map — still the true wall (`BARRIERS.md §B3`). So the
candidate "cheap adjacent rungs" (a bare secp256k1 `ωₙ := complEDS₂/2`, small-`n` `complEDS₂` values)
are **thin/circular** (definitional restatements, no new `Point`-level content) and are **not** to be
minted — that would be ledger inflation. **Next real rung is multi-cycle-hard:** either (A) build the
`Point`-level `[n]`-map induction (step iii, the monolith), or (B) build the universal-ring `÷2`
machinery Mathlib omits. Attempt one as a *focused, possibly-non-closing* grind (a precise failing
step is a first-class barrier), not as a one-cycle brick. If neither is attempted a given cycle,
prefer a genuinely independent item off the `AUTONOMY.md` priority ladder over a thin N7 filler.

**S3a base fully landed for n=2 and n=3 (2026-07-19, PRs #204/#205/#206).** The concrete
`y`-coordinate + Point-level layer is done at small `n`: `y(2P)=(x⁶+140x³−392)/(2y)³`
(`MultiplicationYFormula`), **Point-level** `2•P=(Φ₂/Ψ₂Sq, ω₂/(2y)³)` on the actual group
(`DoublingPointFormula`), and `y(3P)=ω₃/(3x⁴+84x)³` (`MultiplicationYTripleFormula`). The computed
`y`-coordinate ("omega") numerators: **ω₂ = x⁶+140x³−392** (even `n`, no `y` factor),
**ω₃ = y·(x¹²+1540x⁹−87024x⁶−109760x³−1229312)** (odd `n`, `y` factor). Note `FiveTorsionBridge`
already carries the `s₂/s₃ → Point`-level `3•P=some(X3,Y3)` connection (`hsl3s` == the y-triple's
`hℓ3`), so per-`n` Point-level assembly is now mechanical. **Decision: stop the fixed-`n` grind
(breadth) here** — more per-`n` formulas do not approach the uniform statement and risk ledger
inflation. **Next is depth:** define the general secp256k1 `ωₙ` bivariately (via the standard
recurrence `ωₙ=(ψ(n+2)ψ(n−1)²−ψ(n−2)ψ(n+1)²)/(4y)` over Mathlib's `W.ψ`, `4y` a unit in `𝔽_p`) and
prove it reproduces the landed `ω₂`, `ω₃` (evalEval anchors) — grounding the general object in two
independent kernel-verified derivations — then the uniform `y(nP)=ωₙ/ψₙ³` and the x-induction (S3b).
Full DAG + anchors recorded in `targets/n7_uniform_secp256k1_x.json`.

**ω-anchors + `n=4` base leaf fully landed (2026-07-19, PRs #209/#210).** The general ωₙ
grounding is done for the anchors: `secp256k1_omega_recurrence_{two,three,four}`
(`OmegaRecurrenceAnchors.lean`) reproduce `ω₂,ω₃,ω₄` off Mathlib's `ψ` (the `n=4` case needed the
fresh even-index brick `secp256k1_psi6_evalEval`). On top, the **`n=4` (even) base rung of the joint
ω-free carrier is fully closed both coordinates**: `secp256k1_quadruple_y`
(`QuadrupleMultiplicationYFormula.lean`) proves the missing `y(4P)=ω₄/ψ₄³` (via `quad_y_core`,
doubling-of-doubling + three CAS `linear_combination` certs, assembled by the exact identity
`(2Y2)³·4096y¹²=ψ₄³`), and `secp256k1_four_nsmul_coords_ωfree` (`NsmulCoordsBaseFour.lean`) reshapes
it into the carrier format — **closing `carrier_four` (both conjuncts) in the induction stem**
(server-confirmed sorry-free). Base leaves `n=0,1,2,3,4` of `normEDSRec'` are now all closed. One
new honest ledger row; count 289 rows / 250 distinct.

**Point-eval substrate + soundness complete; one degenerate branch closed (2026-07-21, PRs #223–#229).**
The reusable point-evaluated bricks and the univariate↔bivariate keystone are all on `main`:
`φ_ψ_diff_evalEval`, `ψ_isEllSequence_evalEval`, `ψ_succ_mul_ψ_pred_evalEval` (transport trio, #223/#224),
`secp256k1_secant_addX_cleared` (odd-step secant geometry, #225), and the keystone
`ΨSq_eval_eq_ψ_evalEval_sq` / `Φ_eval_eq_φ_evalEval` (#227). The three walls flagged under-hypothesized are
now soundly stated: `odd_x/even_y/odd_y_algebra` thread the `Carrier` y-coupling (Y-sign, #226), and
`odd_x/odd_y` also thread the source denominators `ΨSqₖ, ΨSq_{k+1} ≠ 0` (#228). The odd-step secant
`x`-collision degenerate branch is **closed** — a pure `Point`-group contradiction, not a rational
identity (#229). A read-only `.github/workflows/n7-stem-check.yml` (#225) elaborate-checks the open stem
on every `Targets/**` push (fast feedback; not a merge gate). Stem `sorry` count **9 → 8**.

**Sharpened frontier — 8 residual `sorry`, all in two hard cores (no tractable single-cycle rung left):**
(a) the **uniform torsion bridge** `nsmul_eq_zero_iff_psi_evalEval_zero` (`n•P=O ⟺ ψₙ(P)=0`) plus the
lemmas gated on it — `psiSq_ne_zero_of_nsmul_some` and the two `odd_step_group` torsion side-branches
(`k-`, `(k+1)-`torsion) — the one genuine missing-Mathlib `Point→ψ` map, the true conceptual wall;
(b) the **four algebra walls** `even_x/odd_x/even_y/odd_y_algebra`, each reducing (structure supplied by
the bricks above) to a `field_simp`+`linear_combination` whose cofactor certificate needs **offline
Groebner** — infeasible to author blind in CI (`notes/N7_EVEN_X_REDUCTION.md` for even_x).
Next real advance = the **multi-cycle CAS-assisted / torsion-bridge grind** with server pre-verification;
not a one-cycle brick. Do not mint per-`n` filler.

Kind: theorem | research
Hypothesis: `H2_GLV_SUBGROUP_VS_WHOLE_GROUP`
Why it matters: The scoping half of this task is **delivered** (2026-07-16): the
decomposition memo in `notes/POINT_COUNTING_KEYSTONE.md` §"The successor gap"
chose the geometric-torsion branch (P-256 cardinality stays parked on Hasse) and
named the smallest missing piece — the **N5 scalar obligation**, no two
consecutive zeros in the curve-specialized scalar EDS over `𝔽̄_p`. It is
**unblocked**: the L4 engine (`normEDS_isEllSequence`, `normEDS_somos4`) and the
L5/L6/L6b degenerate-case certificates are kernel-verified; the eval-bridge
descent (`DivisionPolynomialEvalBridge.lean`) turns the scalar lemma into node
N5 (`IsCoprime (Φ n) (ΨSq n)`), feeding the counting route toward `#E[n] = n²`
and (via the proved prime-case N10(iii)) `E[n] ≅ (ℤ/n)²` — the Weil-pairing
non-degeneracy substrate.
Inputs:
- `Ecdlp/Targets/normeds_no_consecutive_zero.lean` (the open stem — the target)
- `targets/normeds_no_consecutive_zero.json` (budget + hint with proof shape)
- `notes/POINT_COUNTING_KEYSTONE.md` §successor gap (the memo)
- `notes/DIVISION_POLY_TORSION_MAP.md` (N5 row, critical path)
Expected output:
- A kernel-accepted proof of `secp256k1_normEDS_no_consecutive_zero`, promoted
  per the standard lifecycle (stem consumed, registry verified, ledger row). No
  weakening, no `sorry`. If attempts stall, a frozen memo recording the exact
  failing induction step instead.
- **Landed (2026-07-18):** the `E[n](𝔽̄_p) ≅ (ℤ/n)²` / `#E[n]=n²` structure family for
  **`n ∈ {2,3,5,7}`** is on `main` (PR #186, kernel-verified; PR #172 reconciled &
  closed, novelty/priority claims stripped per `AUTONOMY.md`). The `n`-by-`n` instances,
  the N7 formulas `n=2,3,4,5`, and the Weil W3 function-field evaluation layer
  (`FunctionField{Eval,Repr,Regular}`) all landed. What remains is the **general-`n`**
  program, the genuine open frontier:
  1. **Uniform separability of `[n]`** (N10 (i)+(ii) general core) — the one CORE item;
     the N5 scalar no-consecutive-zeros lemma (`NormEDSConsecutiveZeros.lean`) landed, so
     the descent toward `#E[n]=n²` for all `n` prime to `p` is the next reachable rung.
  2. **Weil pairing non-degeneracy** — the W3 evaluation layer is closed at the
     function-field level; next rungs: divisor evaluation `f_P(D_Q)`, W4 reciprocity,
     the bilinear `eₙ → μₙ` (the multi-month substrate, `notes/FOUNDATIONS.md`).
  Attempt one reachable rung; if it is Mathlib-blocked, record the precise no-go and
  move down the `AUTONOMY.md` priority ladder.
Exit criteria:
- Either the rung proved and promoted (possibly via a reviewed #172 merge with
  statement-identity check), or the blocker memo naming the precise identity
  that resists (with the attempted decomposition).
Files allowed to edit:
- `Ecdlp/Proved/` (new module on success) + `Ecdlp.lean` + `VERIFIED.md`
- `targets/normeds_no_consecutive_zero.json`, `Ecdlp/Targets/`
- `notes/POINT_COUNTING_KEYSTONE.md`, `notes/DIVISION_POLY_TORSION_MAP.md`

### TASK-006 - Prepare publication boundary track

Kind: publication
Hypothesis: `H6_PUBLICATION_BOUNDARY_TRACK`
Why it matters: The verified substrate already supports useful publications
even without a subgeneric ECDLP breakthrough.
Inputs:
- `PUBLISHABLE_UNITS.md`
- `VERIFIED.md`
- `data/knowledge_graph.json`
- `notes/SECURITY_SCOPE.md`
- `TRUST_REPORT.md`
Expected output:
- One publication unit upgraded to an executable outline with claims,
  theorem references, figures, and trust boundaries.
Exit criteria:
- The outline can be reviewed independently from the full repository.
Files allowed to edit:
- `PUBLISHABLE_UNITS.md`
- `docs/`
- `notes/`

### TASK-007 - Declare v0.1 on main

Kind: ops | docs
Hypothesis: `H1_RESEARCH_OS_TRUTH_LAYER`
Why it matters: Consolidation tranches 1 and 2 are executed (ROADMAP.md §4:
archive/, ROADMAP as the one strategy doc, README as the one front door,
AGENTS.md as the one agent doc, notes/INDEX.md). What remains is the release
act itself, which only makes sense on `main`.
Inputs:
- `ROADMAP.md` (§4 structure tables, §5 near-term program)
- `REPOSITORY_ARCHITECTURE.md` + `repo/CLEANUP_PLAN.md` (map + tranche records)
- `README.md` (already states v0.1)
Expected output:
- The consolidation PR merged by the maintainer; the full gate battery green on
  `main`; an annotated git tag `v0.1` on the merge commit.
Exit criteria:
- `git tag v0.1` exists on main; STATUS.md and the site reflect the merged
  state; no known-false statement in canonical docs.
Files allowed to edit:
- none (tagging + a follow-up docs-sync run on main; open a new task for any
  fallout)

## Task Contract Template

```md
# TASK

ID:
Kind: theorem | experiment | data | site | publication | ops | agent
Hypothesis:
Why it matters:
Inputs:
Expected output:
Exit criteria:
Files allowed to edit:
Files that must be regenerated:
How to verify:
```
