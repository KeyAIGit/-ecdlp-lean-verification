# PR #172 split plan — four atomic PRs (work package B)

Input: PR #172 (head `5f61fa5`, 13 new Lean modules, ~5 000 Lean lines + certs + docs).
Verdict of the audit (`GEOMETRIC_TORSION_AUDIT.md`): the mathematics is layered and the
layers are separable; a single 22-commit monolith defeats semantic review. Split into four
PRs, merged in dependency order. #173 merges **before** all of them (its one module is
upstream of PR-2's `n=3` content, and #172 subsumes it — see §3 of the audit).

## The four PRs (dependency order)

### Split-PR 1 — EDS rigidity & coprimality (N5), curve-agnostic
- **Modules:** `NormEDSConsecutiveZeros.lean`, `DivisionPolynomialCoprime.lean`,
  `CoprimePsi2Psi7.lean`.
- **Public content:** `normEDS_not_consecutive_zeros` (Ward apparition rigidity over any
  integral domain — an **upstream-candidate** for Mathlib, no curve), `secp256k1_isCoprime_Φ_ΨSq`
  (node N5, all `n:ℤ`), `Ψ₂Sq ⊥ preΨ₇`.
- **Downstream users:** the root-count layer (PR-3) and every structure file (PR-4).
- **Acceptance checks:** `lake build`; no-sorry/axiom audit; **disclose** the transitive
  `native_decide` Bézout dependency in the module docstring (audit red flag); this PR also
  **discharges PR #174's open stem** `normeds_no_consecutive_zero` — reconcile that target
  (statement-identity check → `verified`, consume stem) in the same PR.
- **Docstring fix required:** `CoprimePsi2Psi7` header must state `IsCoprime` only, drop the
  "E[2]⊥E[7] points / y≠0 at every root" reading (unformalized).

### Split-PR 2 — multiplication formulas N7@{2,3,5}
- **Modules:** `TripleMultiplicationFormula.lean`, `QuintupleMultiplicationFormula.lean`
  (n=2 already on `main`). **Depends on #173** (`TripleDivisionPolynomial.lean`): after #173
  lands, drop #172's private `Φ₃_eval`/`ΨSq₃_eval` duplicates and `import` the public forms.
- **Public content:** `x(3•P)=Φ₃/ΨSq₃`, `x(5•P)=Φ₅/ΨSq₅` (the `5=3+2` step prototypes the
  general-N7 addition).
- **Downstream users:** the bridge layer (PR-3) and structure (PR-4).
- **Acceptance checks:** `lake build`; correct the "side-condition-free" prose (the `y≠0` /
  non-2-torsion branch is real, via the coprimality import).

### Split-PR 3 — separability, exact root counts, closure bridges
- **Modules:** `DivisionPolynomialSquarefree.lean`, `DivisionPolynomialSeparable.lean`,
  `{Three,Five,Seven}TorsionBridgeBar.lean`.
- **Public content:** squarefree/separable `ψₙ`; exact `(ℓ²−1)/2` distinct roots over 𝔽̄_p;
  `ℓ•P=O ⟺ ψₗ(P)=0` over the closure, ℓ∈{3,5,7}.
- **Downstream users:** structure (PR-4).
- **Acceptance checks:** `lake build`; keep the "token-identical port" prose but note the
  closure statements are genuinely new (audit §Layer 4).

### Split-PR 4 — generic counting/structure + the ℓ∈{3,5,7} instances
- **Depends on this branch's** `Ecdlp/Proved/TorsionCounting.lean` (the generic API landing
  first, or folded in here once CI-green).
- **Modules:** `TorsionStructure.lean` (N10(iii), already on `main`), `TorsionCounting.lean`
  (generic), and `{Three,Five,Seven}TorsionStructure.lean` **rewritten as thin instances**
  of `nonempty_addEquiv_zmod_prod_of_divpoly_data` — passing only the four per-ℓ inputs
  `{bridge iff, root-count pair, coprimality cert, prime fact}` instead of re-proving the
  18-role skeleton. Target: ~400 lines each → ~40–80 lines each.
- **Public content:** `E[ℓ](𝔽̄_p) ≃+ (ℤ/ℓ)²` and `#E[ℓ]=ℓ²`, ℓ∈{3,5,7}.
- **Acceptance checks:** `lake build`; **fix** `SevenTorsionStructure`'s false "no decide"
  header; normalize the ≥5 private `algebraMap` re-declarations to one shared abbrev.

### Ops-PR (separate, not bundled with mathematics)
The counting-script findings and count-integrity fixes (audit §5: `explore.html` stale
counter, alternate-form re-bucket 39→41, stale-high fail-open, table-identity anchoring) go
in their own ops PR, tied to the promotion-gate §3.6 typed-registry work — never mixed into a
math PR.

## Merge order & conflict surface

1. **#173** (one module) — review ~minutes; then rebase #172's content and dedup (§Split-PR 2).
2. **Split-PR 1 → 2 → 3 → 4** in the order above.
3. **#174** — merges independently; on Split-PR 1's merge, reconcile the open stem.

Shared mechanical surfaces for every PR: `Ecdlp.lean` import list, `VERIFIED.md` (canonical
line + rows), and **14** generated artifacts (`data/*`, `STATUS.md`, `COVERAGE.md`,
`BARRIERS.md`, badges, bundles, dashboards). All regenerate deterministically via the
9-generator battery; conflicts there are resolved by **re-running generators**, never by
hand-merging counts.

## Non-negotiables (from the audit)

- Every split PR: 0 `sorry`, 0 custom axioms, gate battery green, prose no stronger than the
  types (the *allowed interpretation* rows in the audit tables are the ceiling).
- The three per-ℓ structure files land only **after/with** the generic API, as instances —
  not as three architecture copies.
- Count-script changes never ride with mathematics (own ops PR).
- Each PR carries its own `#print axioms` disclosure for new public results (native_decide
  vs kernel), per `PROMOTION_GATE_DESIGN.md` §3.4.
