# RH-019 Weierstrass draft review — 2026-08-09

Status: **FINAL — ACCEPT FOR THE NON-BUILT DRAFTS LANE; NO KERNEL VERDICT**

## Reviewed artifacts

- accepted contract:
  `domains/riemann-hypothesis/WEIERSTRASS_FACTORS_CONTRACT.md`
  - SHA-256:
    `24d9630f7758d927c36e018683cf47c510c0ea2e8a71da5780ebd0909d438e31`
  - Git blob: `3b13f7d4eeeb27fd2c963d50def046ebd2310512`
- non-built draft:
  `domains/riemann-hypothesis/drafts/WeierstrassFactors.lean`
  - SHA-256:
    `fe34390369b02dc0eea9f318ba60f971ff1fc6e170634ecdacbda9823160a810`
  - Git blob: `bb222e271051b6ae39851ddf3460640f44bf7b10`
- pinned Mathlib:
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0)

The draft is outside every Lake target and is not imported from
`ResearchOS.lean`. Repository CI does not elaborate it. This review is static
evidence only; it is not a Lean kernel result.

## Verdict

**ACCEPT for the drafts lane.** Two independent lenses found zero blocking
items and requested zero changes to the final reviewed file. The draft contains
complete proof-shaped bodies for all accepted declarations, but those bodies
remain unelaborated until a separately authorized promotion task places a copy
under a Lake target.

This acceptance closes only `RH-019`. It does not promote the file, add a ledger
row, move a barrier, select a route, or change any claim about RH.

## Lens 1 — exact statement surface

The accepted W1–W12 surface and the draft were compared declaration by
declaration after removing only a leading contract doc comment and, for
theorems/lemmas, truncating the draft immediately before its terminal top-level
`:= by`. The two definitions were compared through their complete right-hand
sides.

Result:

- **28/28 exact character matches**;
- declaration kinds: 2 `def`, 19 `lemma`, 7 `theorem`;
- per-section counts: `4/2/2/2/1/1/3/2/2/3/1/5`;
- zero additional public declarations;
- the deliberately omitted 29th `analyticOrderAt_fun_finsetProd` declaration
  remains absent;
- all nine imports and their order match the contract preamble;
- dependency order is W1 → W2/W3/W4 → W5 → W6; W7; W8; W9; W10; W11;
  W12, with the generic finite-product order lemma before the capstone.

For a reproducible aggregate, join the 28 normalized declaration records with
exactly two LF bytes (`\n\n`) between records and no final LF. Both contract and
draft then hash to:

`5c1bbe331f63ae63bb31c88d80e2af6442562091a1996f799e132d254d62d735`

The historical `414948…` digest recorded during `RH-018` has no preserved
serialization algorithm and is not claimed reproduced here. The controlling
`RH-019` evidence is the 28 individual byte comparisons plus the explicitly
defined `5c1bbe…` aggregate above.

## Lens 2 — mathematics, pinned API, and proof mechanics

Every proof body was read against the accepted contract, its re-verification
addendum, and the pinned Mathlib declarations it consumes. No mathematical
counterexample, hidden strengthening, weakening, extra assumption, or API-name
blocker was found.

Load-bearing checks:

- **W4:** the draft performs the required `sum_range_succ'` reindex, absorbs
  the zero denominator term, proves the sign identity, and handles the cast
  seam explicitly before `ring`;
- **W5/W6:** slit-plane membership is named before applying `log_inv`; W6 uses
  a named inverse bound and the repaired pre-combined `hL2`, not a bare
  congruence step that silently emits the false goal `2 ≤ 4/(p+1)`;
- **W7:** escape to infinity uses the genuine inverse and positive-power
  monotonicity directions, then derives finite fibers from the cofinite bound;
- **W8:** boundedness is repaired with `R := max r 0`; the proof derives the
  named `hxR : ‖x‖ ≤ R`, normalizes the division-shaped power, and only then
  applies the summable majorant and uniform-product congruence;
- **W9/W10:** the finite partial products have the required differentiability
  shape, and the complement split first obtains `Multipliable` for both actual
  subtype factor families;
- **W11:** the singleton head is collapsed through `tprod_fintype` and
  `Finset.prod_eq_zero`, while the tail is irrelevant after multiplication by
  zero;
- **W12:** the elementary-factor order, derivative-nonzero transport, finite
  product induction, subtype split, and analytic nonzero tail all follow the
  pinned APIs. The proof sets `S := {i | a i = w}`, proves `S.Finite` through
  W7, installs its finite type, and only then identifies the order with
  `(Nat.card S : ℕ∞)`.

The final exact-hash replay also checked the body-local `classical` declarations
in W11, the generic finite-product lemma, and the W12 capstone. They supply only
local decidability/choice instances and change no statement or trust boundary.

## Trust and isolation checks

- no `sorry`, `admit`, custom `axiom`, `unsafe`, `partial`, `native_decide`, or
  `sorryAx` token;
- no ζ, ξ, `RiemannHypothesis`, or repo theorem dependency;
- no import from `ResearchOS` and no import of the draft from a built root;
- no ledger, registry, axiom-audit, barrier, workflow, or toolchain edit;
- no inaccessible `ℂ_ℤ`, forbidden 29th declaration, conflict marker, or
  trailing-whitespace defect;
- repository artifact, domain, count, status, semantic-drift, target,
  registry, source-registry, lane-isolation, generated-fixpoint, and
  `git diff --check` gates pass on the assembled drafts-lane change.

## Residual risk and promotion gate

The remaining risk is elaboration, concentrated where the contract predicted:
W4's cast/ring seam, W8's locally uniform product inference, and W12's
Pi/subtype/cardinality coercions. That is not a draft blocker and is not hidden:
the future promotion task must copy the reviewed body without changing a
signature, build it under the pinned kernel, and pass the full axiom audits on
the exact PR head. Any statement change returns the surface to contract review.

## Claim boundary

The package is generic fixed-finite-genus complex analysis over arbitrary `p`
and `a`. W12's `Nat.card` is only the local multiplicity of one proved-finite
fiber. Nothing here supplies a ζ/ξ zero enumeration, a global zero count, a
growth theorem, a genus-selection or Hadamard-existence theorem, route
selection, barrier closure, or progress on RH. `S1-GLOBAL-ZEROS` and
`S1-GROWTH` remain OPEN and every RH route remains PARKED.
