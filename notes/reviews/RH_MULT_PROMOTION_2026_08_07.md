# RH multiplicity/divisor package promotion review record (RH-010)

Date: 2026-08-07

Scope: promotion of the independently accepted M1-M17 statement surface of
`domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` into the built module
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean`. This record is
cited by the thirty-four `RH-MULT-*` rows in `VERIFIED_RESEARCHOS.md`.

## Review basis

1. **Independent statement acceptance (RH-009).** The contract's 34-signature
   statement surface was accepted 2026-08-07 under owner-delegated review
   authority — three lenses (mathematical truth, pin fidelity, claim boundary),
   verdict ACCEPT WITH APPLIED EDITORIAL FIXES, zero blocking items. Record:
   `notes/reviews/RH009_MULT_CONTRACT_ACCEPTANCE_2026_08_07.md`.
2. **Prerequisites merged.** All three package prerequisites are kernel-checked
   on `main`: the target bridge (PR #299), the xi package (PR #304), and the
   conjugation package (PR #307). The module imports all three directly.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed under two adversarial lenses (statement fidelity + API existence;
   soundness + elaboration mechanics) with zero S0/S1 findings and the three
   S2 findings applied; thirty of the thirty-four declarations verified
   character-identical to the contract by mechanical comparison, the remaining
   four being the carrier instances the contract spells in its M15 section.
4. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it,
   the regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py`
   enforce the per-row `standard` axiom base, and
   `gen_researchos_registry.py --check` enforces inverse coverage. If any gate
   is red, no row is counted.

## Load-bearing checks

- **Order vocabulary.** Every "finite order" statement is a finite LOCAL
  analytic or meromorphic order; nothing anywhere is a growth order of an
  entire function, which belongs to the still-open `S1-GROWTH` barrier.
- **Reflection leg.** Local-order transport under `s ↦ 1 − s` comes from the
  pinned `analyticOrderAt_comp_of_deriv_ne_zero` through the affine map, with
  the beta-redex hazard at its conclusion discharged by `simpa only
  [sub_sub_cancel]`, never by `rw`.
- **Composite leg.** `s ↦ 1 − conj s` composes the reflection leg with the
  merged conjugation transport; together with the conjugation rows this
  supplies the divisor-invariance exit item of `S1-CONJ`.
- **Divisor discipline.** The divisor carrier is Mathlib's own
  `MeromorphicOn.divisor` (untop-zero totalized); the finite-local-order
  statements (M12/M16') land BEFORE the support identifications (M13/M16''),
  so the totalization can never conflate "not a zero" with "identically zero
  nearby". Only local finiteness and support-equals-zero-set on the carrier
  region are asserted; no infinitude, no enumeration, no counting function.
- **Zeta scoping.** Every zeta statement is confined to the open critical
  strip, where zeta is analytic; the zeta divisor on sets containing `1`
  remains explicitly deferred.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/RiemannMult.lean`) are byte-identical from
the first `import` through end of file; they differ only in their leading
status header. Any proof-only kernel repair must be applied to both copies
before a new CI run; a statement change stops promotion and returns to
contract review.

## Claim boundary

Once and only once the exact merged head passes the full build, the
no-incomplete-proof gate, inverse ledger coverage, and both axiom audits:
this package closes `S1-MULTIPLICITY` (divisor/multiplicity interface plus
the three multiplicity-preserving symmetries for xi, and the strip versions
for zeta) and, together with the merged conjugation package, completes the
exit evidence of `S1-CONJ`. It builds no zero enumeration and no counting
function (`S1-GLOBAL-ZEROS` is untouched), proves no growth bound
(`S1-GROWTH` is untouched), selects no route, and proves, disproves, or
evidences nothing about the truth of the Riemann Hypothesis.
