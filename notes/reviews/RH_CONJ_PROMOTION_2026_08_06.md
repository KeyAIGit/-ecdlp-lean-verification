# RH conjugation-package promotion review record (RH-008)

Date: 2026-08-06

Scope: promotion of the independently accepted Z1-Z9 conjugation-symmetry
surface of `domains/riemann-hypothesis/CONJ_SYMMETRY_CONTRACT.md` into the
built module `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean`.
This record is cited by the sixteen `RH-CONJ-*` rows in
`VERIFIED_RESEARCHOS.md`.

## Review basis

1. **Independent statement acceptance.** The contract's statement surface was
   accepted in merged PR #301 (`7bf13ab`), whose acceptance note records that
   independent review rechecked all sixteen Z1-Z9 signatures, the
   functional-equation separation, the branch-cut hypotheses, and the pinned
   API surface, finding no mathematical statement blocker. That pass also
   corrected the Annex-B `F1` sign to `linear_combination hΛ - h`, which is
   the sign this module carries.
2. **Prerequisites landed.** The two package dependencies the contract carries
   are now kernel-checked on `main`: bridge P2/P3 (PR #299, `288d65b`) and the
   xi definition X1 (PR #304, `afdae08`). The module imports both built
   modules directly rather than assuming their contents, so no theorem is
   proved through an unstated sibling dependency.
3. **Pre-CI adversarial verification.** Before this promotion was offered, the
   module was reviewed under three independent lenses — contract fidelity and
   protocol, dependency/API surface against the built siblings and the pin,
   and elaboration mechanics — with every cited declaration re-verified at
   Mathlib `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Findings were applied
   before commit. Static review is **not** a kernel verdict.
4. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it,
   and the regenerated `ResearchOS/LedgerAxiomAudit.lean` +
   `scripts/check_axioms.py` enforce the per-row `standard` axiom base, with
   `scripts/gen_researchos_registry.py --check` enforcing inverse coverage.
   If any gate is red, no row is counted.

## Load-bearing checks

- **Conjugation is not inferred from the functional equation.** Z2 proves
  `riemannZeta_conj` from the Dirichlet series on the open half-plane
  `1 < re s` plus the pinned identity principle on the preconnected set
  `{1}ᶜ`, with the totalized value `ζ(1) = (γ − log 4π)/2` handled as the
  coercion of a real number. `1 − s` enters the package only in Z8, through
  the already kernel-checked bridge P3, after conjugation is established.
- **Branch discipline.** Every `cpow` conjugation is discharged with an
  explicit `arg ≠ π` hypothesis on a real-nonnegative base (`↑π` via
  `arg_ofReal_of_nonneg`; ℕ-casts via `natCast_arg`, covering `n = 0`
  uniformly so the Dirichlet term needs no case split).
- **The completion is not transported pointwise across the `Gammaℝ` zero
  set.** `Λ = Gammaℝ · ζ` is used only inside `1 < re w` under proved
  `w ≠ 0` and `Gammaℝ w ≠ 0`; the entire `Λ₀` gets its own puncture-free
  identity-theorem pass, and `Λ` follows by totalized field algebra
  (`1/0 = 0`, `conj 0 = 0`), never by meromorphic reasoning at `0` or `1`.
- **Multiplicity discipline.** `riemannZetaZeros` is used as a set only. The
  only multiplicity-adjacent statements are the pointwise `analyticOrderAt`
  transports of Z9; no divisor is constructed, no zero is enumerated, and no
  sum over zeros appears.
- **Generic lemmas.** `AnalyticAt.conj_conj` and `analyticOrderAt_conj_conj`
  do not exist at the pin (contract obligation `S1C-ORD`, grep-verified) and
  are assembled here from pinned ingredients: `eventually_analyticAt` plus the
  conj-preimage open set for the first, and a three-case split over
  `analyticOrderAt_of_not_analyticAt` / `analyticOrderAt_eq_top` /
  `AnalyticAt.analyticOrderAt_eq_natCast` with witness transport for the
  second. Both are natural Mathlib upstreams.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/RiemannConj.lean`) are byte-identical from
the first `import` through end of file, exactly as for the bridge and xi
packages; they differ only in their leading status header. Any proof-only
kernel repair must be applied to both copies before a new CI run; a statement
change stops promotion and returns to contract review.

## Claim boundary

This package supplies conjugation symmetry for `riemannZeta`, both
completions, and `riemannXi`; set-level zero-set invariance; the fourfold zero
action over `ρ`, `1 − ρ`, `conj ρ`, `1 − conj ρ`; and pointwise analytic-order
transport under conjugation. It proves nothing about the truth of the Riemann
Hypothesis, closes no research route, and touches no route's research
obligation.

**It does not close `S1-CONJ`.** That barrier's exit evidence is the
conjugation theorem *together with* divisor invariance under
`ρ ↦ 1 − conj ρ`, which requires the still-open `S1-MULTIPLICITY` divisor
package. This promotion closes the conjugation leg only; the capability map
must record `S1-CONJ` as still open with its divisor item outstanding.
