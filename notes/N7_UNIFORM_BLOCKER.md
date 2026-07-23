# N7 uniform blocker record

Status: **blocked, accepted at the formal-substrate release boundary**

Last bounded pass: **2026-07-22**

This record distinguishes a verified fixed-`n` substrate from the still-open
uniform theorem. It does not claim that N7 is proved.

## Residual obligations

`Ecdlp/Targets/n7_uniform_carrier_induction.lean` elaborates with seven bare
`sorry` obligations:

| obligation | class | blocker |
|---|---|---|
| `nsmul_eq_zero_iff_psi_evalEval_zero` | conceptual bridge | no uniform Point-to-`ψₙ` multiplication theorem |
| `even_x_algebra` | symbolic certificate | degree-heavy doubling/elimination certificate |
| `odd_x_algebra` | symbolic certificate | the same cross-index `ψ` reduction |
| `even_y_algebra` | symbolic certificate | omega-free doubling certificate |
| `odd_y_algebra` | symbolic certificate | omega-free secant certificate |
| `odd_step_group`: `k • P = O` branch | downstream torsion branch | uniform Point-to-`ψₙ` bridge |
| `odd_step_group`: `(k+1) • P = O` branch | downstream torsion branch | uniform Point-to-`ψₙ` bridge |

`Ecdlp/Targets/n7_uniform_secp256k1_x.lean` contains one additional wrapper
`sorry`; it consumes the carrier theorem and is not an eighth independent
mathematical wall.

## Bounded pass evidence

The following committed, independently executable CAS checks passed with
`CERT_OK` under SymPy 1.14:

- `scripts/certs/division_doubling_secp.py`: exact doubling identities for
  `ΨSq(2k)` and `Φ(2k)`, `k=1..8`, plus a finite-field spot check.
- `scripts/certs/eval_bridge_check.py`: even/odd evaluation-bridge identities.
- `scripts/certs/triple_mult_formula_check.py`: the fixed `n=3` formula.
- `scripts/certs/quad_mult_formula_check.py`: the fixed `n=4` formula and
  checked cofactors.
- `scripts/certs/quint_mult_formula_check.py`: the fixed `n=5` formula and
  checked cofactors.

These tests validate landed leaves and candidate identities. They do not create
Lean proof terms and do not imply the all-`n` induction.

The broader four-wall point-level test described in
`notes/N7_EVEN_X_DOUBLING_ANALYSIS.md` was run in an earlier scratch session,
but its `odd_wall_verify.py` script was not committed. It is therefore
historical supporting evidence, not a reproducible release gate.

## Upstream state

[Mathlib PR #13782](https://github.com/leanprover-community/mathlib4/pull/13782),
"ZSMul formula in terms of division polynomials", is still open and unmerged.
At this pass it is reported non-mergeable and still depends on open PRs #13057,
#13155, and #13847. Its intended theorem is exactly the upstream foundation that
would remove the conceptual bridge wall.

## Decision

No statement was weakened, no axiom was added, and no target was promoted. The
target registry status is `blocked`, not `todo`; the active paid prover queue
remains empty.

Resume only when at least one condition holds:

1. Mathlib lands a usable uniform multiplication-coordinate theorem.
2. A reproducible generator emits Lean-checkable certificates for all four
   algebra walls.
3. A new proof decomposition removes one named blocker and passes standalone
   stem elaboration before promotion.
