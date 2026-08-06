# RH xi-package promotion review record (RH-007)

Date: 2026-08-06

Scope: promotion of the independently accepted X1-X11 xi-package surface
from `domains/riemann-hypothesis/drafts/RiemannXi.lean` into the built module
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean`. This record is
cited by the twelve `RH-XI-*` rows in `VERIFIED_RESEARCHOS.md`.

## Review basis

1. **Independent statement acceptance.** PR #303 (squash `202eba0`) accepted
   all eleven contract clauses and twelve public declarations after exact
   mathematical, API, integration, and barrier-boundary review. The durable
   evidence is `RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`.
2. **Exact statement surface.** Names, binders, hypotheses, and conclusions
   remain identical across `XI_PACKAGE_CONTRACT.md`, Annex A of
   `TARGET_BRIDGE_CONTRACT.md`, the synchronized draft, and the built module.
   X4 intentionally contributes two declarations.
3. **Dependency boundary.** The built module directly imports the already
   kernel-checked TargetBridge package. X10 uses bridge P2 only for the reverse
   implication's critical-strip localization. No theorem is re-proved through
   an unstated sibling dependency.
4. **Trust boundary.** The promotion is counted only if the exact PR head
   passes the full build, the no-incomplete-proof scan, ResearchOS inverse
   ledger coverage, and both generated axiom audits with every new row at
   axiom base `standard`.

## Load-bearing checks

- X5 uses the pinned sign
  `completedRiemannZeta = completedRiemannZeta₀ - 1/s - 1/(1-s)`, yielding
  the entire normalization's constant `+1`.
- X6 covers the full `Gammaℝ` zero set: `n = 0` is excluded by `s != 0`, and
  `n = m + 1` is excluded by the exact negative-even-zero hypothesis.
- X10 uses Mathlib's canonical `_root_.RiemannHypothesis`; it proves an
  equivalence of formulations and proves neither side.
- X11 transports `analyticOrderAt` only in `0 < re(s) < 1`, through an
  analytic nonzero cofactor. It constructs no divisor and supplies no
  multiplicity-preserving symmetry action.

## Draft synchronization

The built module and the drafts-lane copy are byte-identical from the first
`import` through end of file. They differ only in their leading status header.
The direct TargetBridge import is present in both copies. Any proof-only
kernel repair must be applied to both copies before a new CI run; a statement
change stops promotion and returns to contract review.

## Claim boundary

This package provides a chosen entire xi normalization, its elementary
functional symmetry and endpoint values, exact zero correspondence away from
the exceptional points, critical-strip localization, an equivalent xi-zero
formulation of RH, and local analytic-order transport. It closes no research
route and provides no evidence for or against RH. Before a green merge,
`S1-XI` remains open; after a green merge it may close, while
`S1-MULTIPLICITY` remains open because no divisor or full symmetry package is
present.

## First kernel-feedback repair

The first promotion head (`9180963`) passed Docs sync and every Lean-lane
gate through dependency caching, then failed only when X11 attempted to
compose Gamma differentiability with `t / 2` using a `.comp` call that omitted
the pinned API's explicit section point. The failure was elaboration-only; no
mathematical goal or theorem statement was rejected.

The built module, synchronized draft, and contract skeleton now use

```lean
DifferentiableAt.fun_comp' z
  (Complex.differentiableAt_Gamma _ hz2)
  (differentiableAt_id.div_const 2)
```

A fresh narrow build on Lean 4.31.0 completed all 3520 dependencies and built
`ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi` successfully. No
declaration name, binder, hypothesis, conclusion, or claim scope changed. The
full repository build and both axiom audits must still rerun on the repaired
head before merge.

## Pending kernel verdict

The authoritative verdict belongs to GitHub CI on the exact promotion head.
Until the full build and both axiom audits succeed, the twelve ledger rows are
proposed promotion records only and the module must not be merged.
