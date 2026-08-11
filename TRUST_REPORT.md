# TRUST_REPORT.md — trust-boundary report for the ECDLP Lean layer

> Counts here are a snapshot; the single canonical figure is **`STATUS.md`** (generated from `data/stats.json`). If they differ, STATUS.md wins.

**Scope of the verified body.** `327 ledger rows / ~288 distinct kernel-verified
results`. A row may group several supporting declarations; the exact expansion is
generated in `data/result_registry.json`. The built surface has **0 `sorry`, 0
`admit`, and 0 custom axioms**. Open target stems are explicitly outside the built
surface and are counted in `repo/FORMAL_SUBSTRATE.json`.

This document states *precisely* what "verified" rests on, which results extend the
trusted computing base (TCB) via the Lean compiler, and what CI actually enforces
versus merely documents. It is the catalogue referenced by the axiom-audit note in
`VERIFIED.md` and by the generated `Ecdlp/LedgerAxiomAudit.lean`.

---

## 1. Trusted computing base

A "verified" result in this repo is a Lean 4 / Mathlib theorem that the Lean **kernel**
accepts. The kernel is a small, fixed type-checker; trusting a proof means trusting:

1. **The Lean 4 kernel** — the type-checker that re-validates every proof term. This is
   the primary judge of correctness.

2. **The three standard Lean/Mathlib axioms** that essentially every Mathlib proof
   depends on:
   - `propext` (propositional extensionality),
   - `Classical.choice` (the axiom of choice),
   - `Quot.sound` (soundness of quotient types).

   When this repo says "**0 axioms**" / "no custom axioms," it means **no axioms beyond
   these three** (and no `sorryAx`). It does *not* mean the empty axiom set. No result
   introduces a project-specific or `sorry`-derived axiom.

3. **For `native_decide` results only — the Lean COMPILER**, surfaced as the axiom
   `Lean.ofReduceBool`. `native_decide` does **not** discharge a goal by kernel
   reduction. Instead it compiles a `Decidable` instance to native code, runs it, and
   asks the kernel to *trust* that the compiled program returned `true`. That trust is
   recorded as a dependency on `Lean.ofReduceBool`. This is a **real extension of the
   TCB**: it adds the Lean compiler, its code generator, and the runtime to the set of
   things that must be correct. A miscompilation could in principle admit a false
   `native_decide` goal that the kernel would never accept under pure reduction.

   This is the single caveat to CLAUDE.md's "the Lean kernel is the only judge of
   correctness": for the `native_decide` rows, the compiler is *also* a judge. The
   axiom audit (Section 3) makes this dependency explicit rather than hidden.

Nothing in the repo depends on `sorryAx`, `Lean.trustCompiler`, or `Lean.guardMsgsAx`;
these are on the audit's permanent forbidden list.

---

## 2. Method classification of the verified results

Every result falls into exactly one of three buckets. The partition is by whether the
result's proof term depends on `Lean.ofReduceBool` (i.e. uses `native_decide` anywhere,
directly or transitively). The kernel `decide` tactic is also used, for a handful of
small finite checks (e.g. `¬ (p ∣ m)` for tiny `m`, and `Fin`/`ZMod` residue facts);
unlike `native_decide`, `decide` is **kernel-checked** — it emits a proof term the kernel
re-validates — so those results stay in bucket (a) and add **nothing** to the TCB. Only
`native_decide` (the compiler path) extends it, and those facts are catalogued in (b).

### (a) Pure Mathlib / kernel — NO `native_decide` (kernel-only TCB)

These rest only on the kernel + `{propext, Classical.choice, Quot.sound}`. This is the
large majority of the ledger: the entire abstract discrete-log protocol algebra, the
generic-group combinatorial core, the torsion/division-polynomial algebra, and the
ring-identity curve invariants. Representative theorems (file → theorem):

- `Ecdlp/Proved/GenericGroupBound.lean` → `generic_dlog_query_bound`,
  `generic_dlog_sqrt_bound`, `generic_success_le`, `collisionSet_card_le_one`,
  `badSet_card_le`, `eval_add`, `eval_neg`, `eval_zero`
- `Ecdlp/Proved/BabyStepGiantStep.lean` → `bsgs_decomp`, `bsgs_steps_sq_ge`
- `Ecdlp/Proved/PollardRho.lean` → `pollard_rho_collision`, `pollard_rho_periodic`
- `Ecdlp/Proved/CollisionEquation.lean` → `collision_modEq`, `collision_zmod`,
  `collision_recovers_log`, `dlog_unique`
- `Ecdlp/Proved/SchnorrSoundness.lean` → `schnorr_extract`, `schnorr_witness_unique`,
  `pedersen_binding_extract`, `secp256k1_schnorr_extract`, `adaptor_extract`,
  `blind_unblind`
- `Ecdlp/Proved/DlogCompleteness.lean` → `schnorr_verify`, `dh_agree`,
  `threshold_schnorr_aggregate`, `feldman_vss_verify`, `musig_key_aggregate`,
  `threshold_elgamal_combine`, `schnorr_batch_verify`, `adaptor_complete`,
  `taproot_tweak_verify`
- `Ecdlp/Proved/DlogPrimitives.lean` → `elgamal_decrypt`, `pedersen_homomorphic`,
  `elgamal_rerandomize_decrypt`, `elgamal_additively_homomorphic`,
  `pedersen_vector_homomorphic`
- `Ecdlp/Proved/DlogAdvanced.lean` → `okamoto_extract`, `chaum_pedersen_verify`
- `Ecdlp/Proved/PohligHellman.lean` → `projection`, `component`, `reconstruct`
- `Ecdlp/Proved/Torsion.lean` + `CurveTorsion.lean` → `mem_torsionBy_iff_addOrderOf_dvd`,
  `torsionBy_dvd_le`, `zmod_module_nsmul_eq_zero`, `torsionBy_eq_top`,
  `torsionBy_eq_ker_nsmul`, `zmultiples_le_torsionBy`, and the `secp256k1_*` curve-named
  copies, `secp256k1_G_ne_zero`
- `Ecdlp/Proved/DivisionPolynomial.lean` → `secp256k1_b₂`, `secp256k1_b₄`,
  `secp256k1_b₆`, `secp256k1_b₈`, `secp256k1_Ψ₂Sq`, `secp256k1_Ψ₃`
- `Ecdlp/Proved/TwoTorsion.lean` / `ThreeTorsion.lean` / `FourDivisionPolynomial.lean`
  (ring-identity parts) → `secp256k1_Ψ₂Sq_root_of_two_torsion`, `secp256k1_Ψ₃_ne_zero`,
  `secp256k1_three_torsion_x_card_le`, `secp256k1_Ψ₂Sq_ne_zero`,
  `secp256k1_two_torsion_x_card_le`, `secp256k1_preΨ₄`, `secp256k1_preΨ₄_ne_zero`
- `Ecdlp/Proved/Invariants.lean` → `secp256k1_c₆`, `secp256k1_c_relation`
- `Ecdlp/Proved/Secp256k1Curve.lean` → `secp256k1_c₄_eq_zero`, `secp256k1_j_eq_zero`
- `Ecdlp/Proved/AnomalousScope.lean` → `anomalous_iff_trace_one`
- `Ecdlp/Proved/CubeRoot.lean` → `cube_root_of_eigenvalue`, `orderOf_eigenvalue_eq_three`
- `Ecdlp/Proved/Cofactor.lean`, `PrimeOrder.lean`, `Lagrange.lean`,
  `Statements.lean` → `cofactor_card_mul_index`, `orderOf_eq_card_of_prime`,
  `order_dvd_card`, `glv_eigenvalue_zmod`
- `Ecdlp/Proved/GlvSlope.lean`, `GlvSlopeTangent.lean`, `GlvSlopeAll.lean`,
  `GlvAddFormula.lean`, `GlvHom.lean` → `secp256k1_glv_slope_of_X_ne`,
  `secp256k1_glv_slope_of_Y_ne`, `secp256k1_glv_slope`, `secp256k1_glv_addX`,
  `secp256k1_glv_addY`, **`glvPoint_add`** / **`glvHom`**
- `Ecdlp/Proved/FrozenProjectiveGuardSystem.lean` →
  `guardedEquation_totalDegree_le_four`,
  `frozenProjectiveChain_iff_guardedProjectiveSystem`,
  `frozenRecS17_iff_guardedProjectiveSystem_over` (the literal finite
  polynomial-family equivalence and degree upper bound are standard
  kernel/Mathlib proofs)
- `Ecdlp/Proved/FrozenProjectiveChartSystem.lean` →
  `card_chartVar`, `frozenProjectiveChain_iff_chartPolynomialCover`,
  `frozenGuardedProjectiveSystem_iff_chartPolynomialCover`,
  `frozenRecS17_iff_chartPolynomialCover_over`, and the base/step/final and
  uniform chart-polynomial degree upper bounds (the exact chart-cover
  equivalences, variable-count formula, and degree ceilings are standard
  kernel/Mathlib proofs)
- `Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean` →
  `HValue_third_infinity`, `HValue_first_infinity`,
  `HValue_middle_infinity`, `HValue_first_third_infinity`,
  `frozenChartSystem_separatedInfinityMask`, the endpoint and forced-neighbor
  theorems, and the admissible/interior cover equivalences (the identities,
  necessary-mask results, and exact cover restrictions are standard
  kernel/Mathlib proofs)
- `Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean` →
  `frozenChartSystem_gapTwoInfinity_forces_det_zero`,
  `frozenChartSystem_gapThreeInfinity_forces_HValue_zero`, the two
  boundary-near propagation theorems,
  `specializeOver_frozenC_eq_zero_of_projectiveChain`, the prefix/suffix and
  empty-mask theorems, the conditional single-affine-chart equivalences, and
  `frozenRecS17_iff_affineChartPolynomialCover_over_of_balancedPropagatedRegular`
  (the local implications and the one-way resultant propagation hold over any
  field; the final source bridge reuses the injective algebraically closed
  target assumption; none of these structural results uses `native_decide`)
- `Ecdlp/Proved/SemaevLeftFoldAffine.lean` → `f3_eq_S₃`,
  `localSlice_eq_eliminationOrder`, `HValue_affine_eq_f3`, the two explicit
  slice-map lemmas, `dehom_frozenC_eq_semaevLeftFoldC`,
  `eval_dehom_eq_frozenSpecialize`, and `S17At_eq_frozenSpecialize` (the
  independently transcribed Semaev-2004 left fold and its coefficient-unit-one
  bridge are generic kernel/Mathlib proofs; the file contains no
  `native_decide` and introduces no compiler-trusted owner)
- `Ecdlp/Proved/M16FactorBaseLiftableDefs.lean` → `boolCountAcc_eq` (the
  predicate-abstract accumulator proof is a generic kernel/Mathlib argument and
  introduces no closed secp256k1 computation)

### (b) `native_decide` / compiler-trusted — TCB INCLUDES the Lean compiler

These depend on `Lean.ofReduceBool`. The proof's truth rests on the compiler in
addition to the kernel. These are the concrete 256-bit / large-integer facts that no
kernel reduction could feasibly check. Exact `file:line → theorem`:

- `Ecdlp/Secp256k1Verified.lean:8`  → `Secp256k1.p_special_form` (`p = 2²⁵⁶−2³²−977`)
- `Ecdlp/Secp256k1Verified.lean:10` → `Secp256k1.glv_lambda_eigenvalue`
- `Ecdlp/Secp256k1Verified.lean:12` → `Secp256k1.lambda_is_cube_root`
- `Ecdlp/Secp256k1Verified.lean:14` → `Secp256k1.lambda_ne_one`
- `Ecdlp/Secp256k1Verified.lean:16` → `Secp256k1.beta_field_eigenvalue`
- `Ecdlp/Secp256k1Verified.lean:18` → `Secp256k1.beta_is_cube_root`
- `Ecdlp/Secp256k1Verified.lean:20` → `Secp256k1.lam_lt_n`
- `Ecdlp/Secp256k1Verified.lean:21` → `Secp256k1.beta_lt_p`
- `Ecdlp/Secp256k1Verified.lean:29` → `Secp256k1.generator_on_curve` (`Gy²≡Gx³+7 mod p`)
- `Ecdlp/Proved/Secp256k1Params.lean:8`  → `p_mod_four` (`p ≡ 3 mod 4`)
- `Ecdlp/Proved/Secp256k1Params.lean:11` → `three_dvd_p_sub_one`
- `Ecdlp/Proved/Secp256k1Params.lean:15` → `three_dvd_n_sub_one`
- `Ecdlp/Proved/Secp256k1Curve.lean:27`  → `secp256k1_Δ_ne_zero`
- `Ecdlp/Proved/Invariants.lean:28`      → `secp256k1_c₆_ne_zero`
- `Ecdlp/Proved/EmbeddingDegree.lean:32/34` → `secp256k1_embedding_degree_gt_100`
  (`pᵏ ≢ 1 mod n` for `1≤k≤100`; MOV/FR resistance)
- `Ecdlp/Proved/TraceOfFrobenius.lean:33/37` → `secp256k1_trace_ordinary_nonanomalous`
  (`t≠0`, `t≠1`, `t²≤4p`; Smart/SSSA + supersingular resistance)
- `Ecdlp/Proved/Secp256k1GenericSecurity.lean:21` → `two_pow_255_lt_secp256k1_n`
  (`2²⁵⁵ < n`)
- `Ecdlp/Proved/FrozenProjectiveGuardSystem.lean:52,56` →
  `card_guardVar_fourteen`, `card_guarded_equations_fourteen` (the raw counts
  56 and 29 only; these two facts use `native_decide`, while the guarded-system
  equivalence and degree-bound theorems do not)
- `Ecdlp/Proved/FrozenProjectiveChartSystem.lean` →
  `card_chartEquation` (the fixed-mask count of fifteen equations only;
  `card_chartVar`, the chart-cover equivalences, and all degree-bound theorems
  do not use `native_decide`)
- `Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean` →
  `card_infinityMask`, `card_separatedInfinityMask`,
  `card_interiorSeparatedInfinityMask` (the exact logical mask counts 16384,
  987, and 377 only; the infinity identities, necessity and forced-neighbor
  results, and cover equivalences do not use `native_decide`)
- `Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean` →
  `card_gapTwoInteriorInfinityMask`,
  `card_gapThreeInteriorInfinityMask`,
  `card_boundaryPropagatedInfinityMask`,
  `card_boundaryGapThreeInfinityMask` (the exact logical candidate-mask counts
  129, 69, 60, and 36 only; the local propagation, base-field one-way
  resultant argument, balanced obstruction, empty-mask, and affine-cover
  theorems do not use `native_decide`)
- `Ecdlp/Proved/M16SolverGate.lean:36,41,58,63,75,80` → exactly six native
  arithmetic owners: `relationTermGate_at_max`, `relationTermGate_succ_max_fails`,
  `two_pow_114_le_maxRelationTermBudget`,
  `maxRelationTermBudget_lt_two_pow_115`,
  `factorBaseDegree_pow_five_le_maxRelationTermBudget`, and
  `maxRelationTermBudget_lt_factorBaseDegree_pow_six`. Derived gate/window
  theorems inherit these leaves as applicable; they are not solver or complexity
  bounds.
- `Ecdlp/Proved/M16FactorBaseLiftableGeneratorCertificate.lean:15` and
  `Ecdlp/Proved/M16FactorBaseLiftableCountCertificate.lean:21` → exactly two new
  liftable-census native owners: `factorBaseGenerator_certificate` and
  `representative_count_native`. `M16FactorBaseLiftableDefs.lean` and the facade
  `M16FactorBaseLiftable.lean` contain no `native_decide`; public generator/orbit,
  liftable/nonliftable, character-sum, and signed-point counts inherit these two
  new certificate leaves where applicable, in addition to pre-existing
  compiler-trusted secp256k1 parameter and primality dependencies.
- `Ecdlp/Proved/M16SixWidthNoGo.lean:72` → exactly one native owner,
  `card_sym_factorBaseX_six_lt_two_pow_106`; the `2^112` signed-index and
  `q > 2^141` fixed-oblivious coverage results inherit it.
- `Ecdlp/Proved/M16LiftableSixWidthNoGo.lean:87` → exactly one private native
  owner, `closed_two_pow_148_half_bound`; the public `q > 2^148`
  fixed-oblivious coverage result inherits it.

These M16 additions are representation and counting certificates only. The two
coverage theorems apply only to their explicit fixed target-independent
translated-image model, and their `q` parameter counts literal residual slots.
They prove no calibrated runtime or memory lower bound, no general M16 lower
bound, no ECDLP lower bound, and no shortcut below the generic baseline. Across
the nine modules there are no `sorry`, `admit`, custom axioms, or additional
new compiler-trusted owners beyond the exact `6 + 2 + 1 + 1` inventory above.
Public M16 conclusions can also transitively inherit older compiler-trusted
secp256k1 parameter, factorization, primality, and cardinality leaves; the
full-ledger audit reports those dependencies rather than misclassifying the
conclusions as pure-kernel results.

The new `SemaevLeftFoldAffine.lean` and `M16DirectSystemRootBridge.lean`
modules add **zero** `native_decide` owners. The latter's concrete `Fp`
statements, including `chainEquations_iff`, `directSolEquivReduced`, and
`S17At_eq_zero_iff_chartPolynomialCover_over`, nevertheless transitively
inherit the repository's pre-existing compiler-trusted secp256k1 Pratt and
primality leaves through the canonical finite-field instances. This is
inherited trust, not a new closed computation in either module.

`M16FrobeniusPointSplit.lean` also adds **zero** `native_decide` owners. Its
coordinatewise Frobenius, point descent, and additive split proofs are ordinary
Lean/Mathlib composition. Because the statements use the concrete secp256k1
base field and curve, their audited conclusions transitively inherit the
repository's pre-existing compiler-trusted secp256k1 parameter/primality
leaves; the final split additionally reuses the existing base-field
`secp256k1_no_nonzero_two_torsion` dependency chain. This is inherited trust,
not a new closed computation in this module.

`FrozenProjectiveSecpLocalFiber.lean` adds **zero** `native_decide` owners. Its
canonical Kummer map, sign quotient, and normalized/determinant local-fiber
proofs are ordinary Lean/Mathlib composition and do not use the base-field
no-nonzero-two-torsion theorem. The audited public surface is not standard-only:
through the concrete secp256k1 `Fp`/`FpBar` instances it transitively inherits
the three standard axioms plus **10 existing secp256k1 primality native-owner
families**. This is inherited compiler trust, not a new closed computation in
this module.

`FrozenProjectiveSecpChainSemantics.lean` and
`M16DirectPointSemantics.lean` add **zero** `native_decide` owners. Their
recursive signed-sum equivalences and direct existential point/root semantics
are ordinary Lean/Mathlib compositions of the local Kummer fiber, complete
chart cover, direct `S17At` bridge, and algebraic-closure square-root
existence. The audited public surface transitively inherits the standard
axioms plus the same **10 existing secp256k1 primality native-owner families**
through the concrete `Fp`/`FpBar` instances. It introduces no new compiler-
trusted owner and does not reuse the base-field no-two-torsion certificate
chain.

`M16BaseRecoveryFiber.lean` adds **zero** `native_decide` owners. Its
square-root/actual-point equivalence, target-labelled global-negation
equivalence, finite specification, nonemptiness criterion, and direct-system
specialization are ordinary Lean/Mathlib composition. The audited public
surface inherits the three standard axioms, the existing secp256k1
discriminant owner, and the same **10 existing secp256k1 primality
native-owner families**. It does not inherit the liftable-census owners or the
base-field no-two-torsion chain. These are pre-existing transitive leaves, not
new closed computations in this module. The finite enumeration remains a
semantic specification, and the exact doubling counts Boolean orientation
labels rather than necessarily distinct unlabelled recoveries.

`M16CanonicalRecoveryRows.lean` adds **zero** `native_decide` owners. Its
lower-residue reference/sign classification, repeated-coordinate `Finsupp`
aggregation and evaluation, target-sign normalization, global-sign
invariance, and finite image/backpointer/multiplicity partition are ordinary
Lean/Mathlib composition. The reference is a noncomputable mathematical
convention using `Classical.choice`, not an implemented square-root,
point-decompression, or recovery procedure. The audited declarations inherit
the existing secp256k1 discriminant owner, the three existing `rhs ≠ 0` support owners
(`three_dvd_p_sub_one`, `secp256k1_seven_ne_zero`, and
`secp256k1_neg7_pow_ne_one`), and the same **10 existing secp256k1 primality
native-owner families**, in addition to the three standard axioms. They do not
inherit the liftable-census owners or the base-field no-two-torsion chain.
These are pre-existing transitive leaves, not new closed computations in this
module; the finite `Finset` row-image specification is semantic rather than an
enumeration or cost claim.

`M16GLVCanonicalRows.lean` adds **zero** `native_decide` owners. Its exact
three-phase census equivalence, lower-residue reference-point covariance,
integral and mod-`n` compression identities, the direct global-sign identity
`canonicalGLVRow_globalNegate`, explicit noninjectivity witness, split
surjectivity, and ambient finrank calculation are ordinary Lean/Mathlib
composition. The census equivalence and lower-residue reference are
noncomputable mathematical conventions using `Classical.choice`, not an
enumerator, square-root, point-decompression, or recovery implementation. The
audited declarations inherit the three standard axioms and only already
catalogued native-owner families reached through their dependencies: the
secp256k1 discriminant/parameter and ten primality families;
`Secp256k1.beta_field_eigenvalue`; the curve-cardinality/cofactor-one and
generator/GLV-eigenvalue chains used to promote `[lambda]` to the whole
base-point group; the three `rhs ≠ 0` support owners
`three_dvd_p_sub_one`, `secp256k1_seven_ne_zero`, and
`secp256k1_neg7_pow_ne_one`; and the two liftable-census owners
`factorBaseGenerator_certificate` and `representative_count_native`. Not every
export reaches every listed family, and the newly public factor-base wrapper
helpers introduce no owner. The dimensions `283527`, `94509`, and `189018`
describe ambient coefficient spaces, not collected relation rank or yield; no
theorem identifies the census reference with the separate experimental
minimum-point-encoding convention or supplies a recovery/solver/cost result.

`M16FiniteGLVRelationRank.lean` adds **zero** `native_decide` owners. Its
subgroup-valued mod-`n` row evaluator, certified-target and nonzero-row bridges,
labelled coefficient and augmented matrices, `Finsupp` synthesis/range
identities, matrix-rank equalities, rank-nullity formulas, one-column rank
comparison, and distinct-row upper bounds are ordinary Lean/Mathlib
composition. The sample type is abstract and finite: no recovery witness or
matrix is constructed or enumerated, and repeated rows at different labels are
not deduplicated. The audited declarations inherit the three standard axioms
and only already catalogued native-owner families reached through their
dependencies: secp256k1 parameter/primality and concrete subgroup structure,
the full-group/GLV chains, the three `rhs ≠ 0` support owners, and the two
liftable-census owners. Not every export reaches every listed family, and no
new closed computation is introduced. Coefficient rank and augmented rank are
separate conventions; the module proves no achieved rank, independence, yield,
distribution, sparse-linear-algebra outcome, solver, recovery, runtime/memory/
cost, minimum-encoding comparison, scalar recovery, or ECDLP shortcut.

`M16PartitionedPointSemantics.lean` likewise adds **zero** `native_decide`
owners, but its trust inheritance is deliberately stated separately: the
partition theorem calls the existing final Frobenius split, so its audited
public conclusions inherit both the existing secp256k1 primality native-owner
families and the existing base-field no-two-torsion certificate chain. This is
transitive reuse of previously catalogued compiler-trusted leaves, not a new
closed computation or a new native owner in the partition module.

`M16CancellationRootLowerBound.lean` adds **zero** `native_decide` owners. Its
labelled-pair injections and cardinal inequalities are ordinary Lean/Mathlib
composition. The root lower bounds transitively reuse the existing secp256k1
parameter/primality and factor-base certificate families, the two existing
liftable-census native owners, and the existing base-field no-two-torsion
certificate chain. The budget corollaries additionally reuse the already
catalogued `M16SolverGate.maxRelationTermBudget_lt_two_pow_115` arithmetic
owner. These are inherited leaves, not new closed computations in this module;
the comparison remains output cardinality rather than a PFPO or runtime charge.

`M16CancellationBackpointerCollapse.lean` adds **zero** `native_decide`
owners. It noncomputably fixes the affine target coordinate and canonical
reference lifts, then uses ordinary Lean/Mathlib composition to package an
injective seven-choice cancellation family as root-plus-recovery
backpointers. Every displayed witness has canonical row
`Finsupp.single a (-2)`, including when pair coordinates repeat or equal the
anchor, so one constant-row subtype has cardinality at least `283527^7`.
The audited declarations inherit the three standard axioms and exactly the
already catalogued native-owner families reached by their dependencies:
`secp256k1_Δ_ne_zero`; the three `rhs ≠ 0` support owners
`three_dvd_p_sub_one`, `secp256k1_seven_ne_zero`, and
`secp256k1_neg7_pow_ne_one`; `secp256k1_p_sub_one_factorization`,
`Secp256k1.beta_field_eigenvalue`, `secp256k1_two_nsmul_eq_zero_iff`, and
`secp256k1_no_nonzero_two_torsion`; the same ten secp256k1 primality families;
and the two factor-base/liftable-census owners
`factorBaseGenerator_certificate` and `representative_count_native`. Only the
final desk-budget comparison additionally inherits the existing
`M16SolverGate.maxRelationTermBudget_lt_two_pow_115` owner. These are
pre-existing transitive leaves, not new closed computations. The subtype
counts constructed labelled root-plus-recovery backpointers over one row; it
does not count recoveries of one fixed root, classify every recovery, make row
evaluation injective, or supply a PFPO, enumeration, rank, recovery, cost, or
ECDLP result.

`M16CancellationRelationRank.lean` adds **zero** `native_decide` owners. It
noncomputably packages the explicit seven-choice cancellation family as an
injective labelled sample, proves that all coefficient and augmented rows are
constant and nonzero, and uses ordinary Lean/Mathlib span and rank-nullity
arguments to obtain both matrix ranks `1` and both exact kernel dimensions
`283527^7 - 1`. The audited declarations inherit the three standard axioms and
only already catalogued native-owner families reached through the two imported
layers: secp256k1 parameter/primality and concrete-subgroup/full-group/GLV
structure, the `rhs ≠ 0` support and base-field no-two-torsion chains, and the
factor-base/liftable-census owners. No solver-budget owner is reached because no
budget comparison is used, and no new closed computation is introduced. The
large synthesis kernels certify duplicate-row dependencies in this one
deliberately constant-row family; they do not supply useful relation yield,
independence, rank growth, enumeration, sparse linear algebra, recovery, cost,
scalar recovery, or an ECDLP shortcut.

### (c) Mathlib + `native_decide` MIX — kernel proof skeleton, compiler-checked leaves

Here the *argument* is a kernel-checked Mathlib proof, but one or more small numeric
side-conditions inside it are discharged by `native_decide` (so the result still
depends on `Lean.ofReduceBool`). These are the rows tagged "Mathlib + native_decide" in
`VERIFIED.md`:

- `Ecdlp/Proved/Secp256k1GenericSecurity.lean:49` → `secp256k1_bsgs_steps_le` and the
  `2²⁵⁵<n`-fed `secp256k1_generic_security` (`Nat.sqrt_lt'` reduces the goal, leaf by
  `native_decide`)
- `Ecdlp/Proved/Secp256k1Order.lean:28,42` → `secp256k1_beta_orderOf`,
  `secp256k1_lambda_orderOf`, `secp256k1_three_cube_roots_of_unity` (order-3 / cube-root
  count; the `≠ 0` leaves go via `ZMod.natCast_eq_zero_iff` + `native_decide`)
- `Ecdlp/Proved/DivisionPolynomialDegree.lean:25,53` → `secp256k1_Ψ₂Sq_natDegree`,
  `secp256k1_Ψ₃_natDegree` (leading-coeff `≠ 0` leaf via `native_decide`)
- `Ecdlp/Proved/FourDivisionPolynomial.lean:42` → `secp256k1_preΨ₄_natDegree`
- `Ecdlp/Proved/Secp256k1Curve.lean:76` → `IsElliptic` instance,
  `secp256k1_generator_equation`, `secp256k1_generator_nonsingular`
- `Ecdlp/Proved/GlvEndomorphism.lean:` → `secp256k1_glv_preserves_equation`,
  `secp256k1_glv_preserves_nonsingular` (β³=1 leaf is `native_decide`)
- `Ecdlp/Proved/M16FactorBaseFinite.lean` → `card_factorBaseX`, and
  `Ecdlp/Proved/M16FactorBaseSymmetricGate.lean` → the exact
  width-six/width-seven symmetric-power counts and budget comparisons. Their
  representation/counting proof bodies introduce no native owner, but the
  public conclusions transitively inherit the existing compiler-trusted
  secp256k1 factorization/primality leaves used by the root cardinality; solver
  budget conclusions additionally inherit the six new owners catalogued above.
- `Ecdlp/Proved/M16DirectSystemRootBridge.lean` → `chainEquations_iff`,
  `directSolEquivReduced`, and
  `S17At_eq_zero_iff_chartPolynomialCover_over`. Their proof bodies are
  ordinary kernel/Mathlib composition and the source file contains no
  `native_decide`; the concrete `Fp` specialization inherits only the existing
  compiler-trusted secp256k1 Pratt/primality dependency chain.
- `Ecdlp/Proved/M16FrobeniusPointSplit.lean` →
  `frobeniusPoint_eq_of_liesOver_of_isLiftable`,
  `frobeniusPoint_eq_neg_of_liesOver_of_not_isLiftable`,
  `frobenius_split_before_two_torsion`,
  `frobenius_split_of_base_subtotal`, and
  `split_partitioned_point_witnesses`. Their proof bodies introduce no
  `native_decide` owner; the concrete `Fp` point and curve instances inherit
  the existing secp256k1 parameter/primality leaves, and the final elimination
  step reuses the existing base-field no-nonzero-two-torsion dependency chain.
- `Ecdlp/Proved/FrozenProjectiveSecpLocalFiber.lean` → `barKummer_eq_iff`,
  `HValue_barKummer_normalize_zero_iff`, `HValue_barKummer_zero_iff`, and
  `HValue_barKummer_zero_iff_projectiveDet`. Their proof bodies introduce no
  `native_decide` owner and do not use the base-field no-two-torsion theorem;
  the concrete `Fp`/`FpBar` instance chain transitively contributes the three
  standard axioms plus the 10 existing secp256k1 primality native-owner
  families.
- `Ecdlp/Proved/FrozenProjectiveSecpChainSemantics.lean` →
  `frozenProjectiveChain_barKummer_iff_signedPrefixSum`,
  `frozenProjectiveChain_barKummer_iff_explicitSigns`,
  `frozenChartCover_barKummer_iff_signedPrefixSum`, and
  `frozenChartCover_barKummer_iff_explicitSigns`; and
  `Ecdlp/Proved/M16DirectPointSemantics.lean` →
  `S17At_eq_zero_iff_exists_point_sum_liesOver`,
  `S17At_eq_zero_iff_exists_point_sum_eq_target_or_neg`,
  `S17At_eq_zero_iff_exists_point_sum_add_target_eq_zero`, and
  `S17At_eq_zero_iff_exists_point_relation`. Their proof bodies introduce no
  `native_decide` owner; the concrete `Fp`/`FpBar` instance chain contributes
  only the standard axioms and the 10 inherited secp256k1 primality native-
  owner families.
- `Ecdlp/Proved/M16PartitionedPointSemantics.lean` →
  `partitionedPointWitness_of_compatible_point_relation`,
  `partitionedPointWitness_iff_exists_compatible_point_relation`,
  `S17At_eq_zero_iff_partitionedPointWitness`, and
  `S17At_factorBase_eq_zero_iff_partitionedPointWitness`. Its proof bodies add
  no `native_decide` owner. Through the existing final Frobenius split, these
  conclusions transitively inherit the secp256k1 primality native-owner
  families **and** the pre-existing base-field no-two-torsion certificate
  chain.
- `Ecdlp/Proved/M16BaseRecoveryFiber.lean` →
  `liftAtEquivActualLiftAt`, `recoveryGlobalNegate_ne`,
  `recoveryFiberEquivNormalizedFiberProdBool`,
  `recoveryFiberEquivRecoveryFinsetSubtype`,
  `nonempty_recoveryFiber_iff_S17At_eq_zero_and_all_isLiftable`, and
  `nonempty_recoveryFiber_of_directSystem4_iff_all_isLiftable`. Their proof
  bodies add no `native_decide` owner. The audited declarations inherit only
  the existing secp256k1 discriminant owner and ten primality native-owner
  families in addition to the standard axioms; they do not pull in the
  liftable-census or base-field no-two-torsion owners.
- `Ecdlp/Proved/M16CanonicalRecoveryRows.lean` → `referenceLift`,
  `existsUnique_lowerResidueLift`, `referenceSignEquiv`,
  `coefficientVector_apply`, `evalRow_coefficientVector`,
  `canonicalRow_globalNegate`, `evalRow_canonicalRow_of_compatible`,
  `canonicalRow_recoveryGlobalNegate`,
  `mem_canonicalRows_iff_backpointers_nonempty`,
  `evalRow_eq_target_of_mem_canonicalRows`, and
  `card_recoveryFiber_eq_sum_rowMultiplicity`. Their proof bodies add no
  `native_decide` owner. The audited declarations inherit the existing
  secp256k1 discriminant owner, three `rhs ≠ 0` support owners, and ten
  primality native-owner families, but neither the liftable-census owners nor
  the base-field no-two-torsion chain.
- `Ecdlp/Proved/M16GLVCanonicalRows.lean` → `liftableGLVPhaseEquiv`,
  `referencePoint_glvPhase`, `glvCompress_single_phase`,
  `evalGLVRow_comp_glvCompress`, `canonicalGLVRow_globalNegate`,
  `evalGLVRow_canonicalGLVRow`,
  `glvCompress_not_injective`, `glvCompressModN_reduceModN`,
  `glvCompressModN_comp_glvPhaseZeroSectionModN`,
  `glvCompressModN_surjective`, `finrank_rawRowModN`,
  `finrank_glvRowModN`, and `finrank_ker_glvCompressModN`. Their proof bodies
  add no `native_decide` owner. They inherit only the pre-existing secp256k1
  parameter/primality, GLV/full-group, `rhs`-support, and liftable-census
  certificate families described above; the three newly public
  `M16FactorBaseLiftable` wrappers likewise add no owner.
- `Ecdlp/Proved/M16FiniteGLVRelationRank.lean` →
  `coe_evalGLVRowModN_reduceModN`,
  `evalGLVRowModN_certifiedRowModN`, `certifiedRowModN_ne_zero`,
  `certifiedRelation_closes`, `coefficientMatrix`, `augmentedMatrix`,
  `augmentedMatrix_row_closes`, `coefficientRank_add_finrank_ker`,
  `augmentedRank_add_finrank_ker`,
  `coefficientMatrix_rank_eq_coefficientRank`,
  `augmentedMatrix_rank_eq_augmentedRank`,
  `coefficientRank_le_augmentedRank`,
  `augmentedRank_le_coefficientRank_add_one`,
  `coefficientRank_le_distinctCoefficientRows_card`, and
  `augmentedRank_le_distinctAugmentedRows_card`. Their proof bodies add no
  `native_decide` owner. They inherit only the already catalogued secp256k1
  parameter/primality, concrete subgroup, GLV/full-group, `rhs`-support, and
  liftable-census families reached through their dependencies; no achieved-rank
  or solver/cost conclusion is audited.
- `Ecdlp/Proved/M16CancellationRootLowerBound.lean` →
  `cancellation_pair_root_lower_bounds`,
  `exists_nonzero_target_root_lower_bounds`,
  `maxRelationTermBudget_lt_liftable_cancellation_family`, and
  `exists_target_budget_lt_directRoot_card`. Their proof bodies add no
  `native_decide` owner. The root-cardinality conclusions inherit the existing
  secp256k1 parameter/primality and factor-base certificate families, the two
  liftable-census owners, and the base-field no-two-torsion certificate chain;
  the two desk-budget conclusions additionally inherit the existing
  `maxRelationTermBudget_lt_two_pow_115` arithmetic owner.
- `Ecdlp/Proved/M16CancellationBackpointerCollapse.lean` →
  `anchorTarget_ne_zero`, `anchorTarget_liesOver`,
  `coefficientVector_cancellationLiftTuple`, `cancellationCompatible`,
  `cancellationRootWithRecovery_injective`,
  `canonicalRow_cancellationRecovery`,
  `backpointerRow_cancellationRootWithRecovery`,
  `card_constantRowPreimage_lower_bound`, and
  `maxRelationTermBudget_lt_constantRowPreimage_card`. Their proof bodies add
  no `native_decide` owner. They inherit the existing secp256k1
  parameter/primality, `rhs ≠ 0`, base-field no-two-torsion, and
  factor-base/liftable-census certificate families; only the final numeric
  comparison also inherits the existing solver-budget arithmetic owner.
- `Ecdlp/Proved/M16CancellationRelationRank.lean` →
  `cancellationRankSample_injective`,
  `certifiedRowModN_cancellationRankSample`, `cancellationRowModN_ne_zero`,
  `coefficientRank_cancellationRankSample`,
  `augmentedRank_cancellationRankSample`,
  `coefficientMatrix_rank_cancellationRankSample`,
  `augmentedMatrix_rank_cancellationRankSample`, `card_cancellationLabel`,
  `finrank_ker_coefficientSynthesis_cancellationRankSample`, and
  `finrank_ker_augmentedSynthesis_cancellationRankSample`. Their proof bodies
  add no `native_decide` owner. They inherit only already catalogued secp256k1
  parameter/primality, concrete-subgroup/full-group/GLV, `rhs`-support,
  base-field no-two-torsion, and factor-base/liftable-census families reached
  through their dependencies; no solver-budget owner or useful-rank/solver/cost
  conclusion is audited.
- `Ecdlp/Proved/M16GLVSectionChangeRank.lean` → `rank_rebaseMatrix`,
  `evalSectionRowModN_rebase`, `rebasedCertifiedRelation_closes`,
  `rebasedCoefficientMatrix_rank_eq`, `rebasedAugmentedMatrix_rank_eq`,
  `ker_rebasedCoefficientSynthesis`, `ker_rebasedAugmentedSynthesis`,
  `card_rebasedDistinctCoefficientRows`,
  `card_rebasedDistinctAugmentedRows`,
  `rebasedCoefficientMatrix_rank_cancellationRankSample`,
  `rebasedAugmentedMatrix_rank_cancellationRankSample`,
  `finrank_ker_rebasedCoefficientSynthesis_cancellationRankSample`, and
  `finrank_ker_rebasedAugmentedSynthesis_cancellationRankSample`. Their proof
  bodies add no `native_decide` owner. As applicable, the audited conclusions
  inherit only the already catalogued secp256k1 parameter/primality,
  GLV/full-group, concrete-subgroup, `rhs`-support, base-field no-two-torsion,
  and factor-base/liftable-census families reached through their dependencies;
  no solver-budget owner is introduced. `SignedGLVSection` remains a supplied
  conditional certificate and is not a certificate for, or comparison with,
  the separate experimental minimum-point-encoding convention. No achieved
  experimental rank, useful yield, solver, cost, or ECDLP conclusion is
  audited.
- `Ecdlp/Proved/M16FixedFiberMultiplicityRank.lean` →
  `ker_augmentedSynthesis_eq_inf_ker_coefficientSynthesis_ker_labelSum`,
  `ker_augmentedSynthesis_eq_ker_coefficientSynthesis_of_target_ne_zero`,
  `coefficientRank_eq_augmentedRank_of_target_ne_zero`,
  `coefficientMatrix_rank_eq_augmentedMatrix_rank_of_target_ne_zero`,
  `ker_rebasedAugmentedSynthesis_eq_ker_rebasedCoefficientSynthesis_of_target_ne_zero`,
  `rebasedCoefficientMatrix_rank_eq_rebasedAugmentedMatrix_rank_of_target_ne_zero`,
  `range_coefficientMatrix_row_fixedFiberSample`,
  `range_augmentedMatrix_row_fixedFiberSample`,
  `coefficientRank_fixedFiberSample_eq_normalizedFiberSample`,
  `augmentedRank_fixedFiberSample_eq_normalizedFiberSample`,
  `finrank_ker_coefficientSynthesis_fixedFiberSample`,
  `finrank_ker_augmentedSynthesis_fixedFiberSample`,
  `coefficientRank_fixedFiberSample_le_card_normalizedFiber`,
  `augmentedRank_fixedFiberSample_le_card_normalizedFiber`,
  `card_normalizedFiber_le_finrank_ker_coefficientSynthesis_fixedFiberSample`,
  and
  `card_normalizedFiber_le_finrank_ker_augmentedSynthesis_fixedFiberSample`.
  Their proof bodies add no `native_decide` owner. All sixteen audited
  declarations are transitively compiler-backed only through already
  catalogued secp256k1 parameter/primality, concrete-subgroup/full-group/GLV,
  `rhs`-support, base-field no-two-torsion, and factor-base/liftable-census
  dependency families as applicable; no solver-budget owner, `sorryAx`, or
  custom axiom is introduced. At target zero only the exact kernel intersection
  is audited, while kernel/rank equality requires a nonzero target; the rebased
  results require a supplied `SignedGLVSection`. The full and normalized fibers
  are not identified, and raw integral canonical (`C`) row and GLV/mod-`n` row
  multiplicity, coarsening, and partitions remain deferred. No experimental
  minimum-point encoding, achieved rank, useful yield, solver, cost, scalar
  recovery, or ECDLP conclusion is audited.
- `Ecdlp/Proved/M16FactorBaseLiftable.lean` → the public generator/orbit,
  liftable/nonliftable, character-sum, fiber, and signed-point counts, plus
  `rhs_beta_mul`, `liftableOrbitEquiv`, and
  `liftableOrbitEquiv_apply_fst`. Kernel
  composition surrounds exactly the two new census owners catalogued above and
  also inherits pre-existing compiler-trusted secp256k1 parameter/primality
  leaves.
- `Ecdlp/Proved/M16SixWidthNoGo.lean` → `ncard_coveredTargets_le` and the
  public `q > 2^141` fixed-oblivious coverage conclusion. The range-counting
  skeleton is kernel/Mathlib, while its concrete `SecpPoint` instance and final
  bounds transitively inherit existing curve-cardinality/primality leaves plus
  the one new width-six comparison owner catalogued above.
- `Ecdlp/Proved/M16LiftableSixWidthNoGo.lean` → the exact liftable symmetric
  counts and public `q > 2^148` fixed-oblivious coverage conclusion. These
  transitively inherit the existing secp256k1 leaves, the two new liftable
  census owners, and the one new private comparison owner catalogued above.

#### IMPORTANT mitigation — the primality certificates (`Secp256k1PrimeP.lean` / `Secp256k1PrimeN.lean`)

`secp256k1_p_prime` and `secp256k1_n_prime` are the most security-load-bearing facts in
the repo, and they are deliberately structured to **minimize compiler trust**. They are
**full Pratt certificates**: a kernel-checked recursion using Mathlib's
`lucas_primality`, where the heavy mathematical content (the Lucas/Pocklington
argument, factor primality propagated up a tree of sub-primes) is verified **by the
kernel**, and `native_decide` is invoked only to discharge **small, local checks** —
e.g. a single witness exponentiation `a^((p-1)/q) ≠ 1 mod p`, or a factorization
identity `p − 1 = 2^a·(q₁·…)` (see `Secp256k1PrimeN.lean:10–12`, `:127`, `:160`;
`Secp256k1PrimeP.lean:10–12`, `:175`). The compiler is therefore trusted only for
bounded arithmetic facts that sit *inside* a kernel-checked Lucas argument — not for the
primality conclusion itself. This is the correct way to use `native_decide` for a
high-stakes fact, and is the reason the trade-off in Section 4 is acceptable.
(Note: the ~22 internal recursive Pratt sub-lemmas are *not* counted as separate ledger
results — see the retired "128" figure in `VERIFIED.md`.)

**Count.** The generated full-ledger axiom audit prints the exact compiler-trusted set
for every CI run; `scripts/check_axioms.py` reports the count and fails on any
unregistered or disallowed dependency. The large majority of the ledger is pure-kernel
(bucket (a)); live ledger totals remain in **`STATUS.md`** / `data/stats.json`.

---

## 3. What CI actually ENFORCES vs documents

`.github/workflows/ci.yml` runs the following gates on every push / PR / dispatch.
Distinguishing *machine-enforced* (a red build blocks merge) from *documentation-only*:

| Step (ci.yml) | What it does | Enforced? |
|---|---|---|
| `Check count consistency (docs)` — `scripts/check_counts.py` | Parses the canonical ledger/stats surfaces, rejects retired headline strings, and checks that generated/current counts agree. | **MACHINE-ENFORCED** (build-breaking), complemented by `gen_stats.py --check` and the generated-artifact fixpoint gate. |
| `Ensure no incomplete proofs remain` | `grep -rniI --include='*.lean' --exclude-dir=Targets 'sorry' Ecdlp/` — fails if `sorry`/`admit` text appears in any **built** `.lean` file. `Ecdlp/Targets/` (open stems) is excluded by design. | **MACHINE-ENFORCED**, with the documented scope limit that it is a *text* grep over built files and deliberately skips `Targets/`. |
| `Ensure no built file imports an open target stem` | `grep` for `import Ecdlp.Targets` outside `Targets/`. Closes the hole where a built file could pull a `sorry`-bearing stem into the build graph (since `sorry` is only a warning). | **MACHINE-ENFORCED.** This is the guard that makes the previous grep sound. |
| `Fetch prebuilt Mathlib cache` + `Build and verify ALL proofs` — `lake build` | The **kernel** re-checks every built proof term. A `sorry` that reached the build graph, or any type error, fails here. | **MACHINE-ENFORCED.** This is the core verification: a green `lake build` means the kernel accepted every built theorem. |
| `Axiom audit (no sorryAx, no custom axioms)` — `lake env lean Ecdlp/LedgerAxiomAudit.lean` → `scripts/check_axioms.py` | Generates `#print axioms` for every named declaration resolved from all 327 ledger rows. It fails on `sorryAx`, guard/custom axioms, unknown names, or any mismatch between Lean output and `data/result_registry.json`; compiler-trust markers from `native_decide` are disclosed. | **MACHINE-ENFORCED and exhaustive over the named ledger declaration set.** Seven anonymous instance targets are source-resolved exemptions because they have no source-level declaration name; their defining files are still built and their named load-bearing theorems are audited. |
| `Typecheck open target stems (non-blocking)` | `lake env lean` over `Ecdlp/Targets/*.lean`; `continue-on-error: true`. | **DOCUMENTATION/INFO ONLY.** A stem failing to typecheck emits a warning, never blocks. |
| `Featherless API smoke test`, `Prover target attempt`, report upload | All `continue-on-error: true` and skipped on PRs. | **DOCUMENTATION/INFO ONLY.** Prover orchestration; cannot affect the verification verdict. |

**Net guarantee:** a green `main` machine-guarantees that (i) every built theorem is
kernel-accepted with no `sorry`, (ii) no built file imports an open stem, and (iii) the
all named declarations referenced by the ledger depend only on the allowed trusted
base — i.e. no custom axioms, and every compiler-trusted (`native_decide`) result is disclosed. The
count-consistency and stem-typecheck steps are doc-hygiene, not correctness guarantees.

---

## 4. Honest caveats

- **"0 axioms" is shorthand for "no axioms beyond the standard three."** Every result
  uses Mathlib and therefore transitively `{propext, Classical.choice, Quot.sound}`.
  The honest claim is: **no custom axioms, no `sorryAx`** — machine-enforced by the
  axiom-audit gate. It is *not* a claim of axiom-free foundations.

- **The concrete compiler-trusted set is emitted by every axiom-audit CI run.**
  These declarations extend the TCB beyond the kernel to include the Lean compiler/runtime, via
  `Lean.ofReduceBool`. This means CLAUDE.md's invariant "the Lean kernel is the only
  judge of correctness" is, strictly, **not true for those declarations** — the compiler is
  also a judge. This is **`archive/docs/REVIEW_DOSSIER.md` finding 9** ("`native_decide` enlarges the
  TCB beyond the kernel"; severity LOW), whose verdict is *ACCEPTABLE trade-off,
  honestly fixable*: the mitigation is correct where it matters most — the primality of
  `p` and `n` structures `native_decide` to discharge only small checks inside a
  kernel-checked Lucas argument (Section 2(c)). This report is the disclosure that
  finding 9 asked VERIFIED.md to carry.

- **The GLV map is proved an ADDITIVE endomorphism, but the eigenvalue identity is
  NOT proved.** `Ecdlp.Curve.glvPoint_add` (bundled as `glvHom : Point →+ Point` in
  `Ecdlp/Proved/GlvHom.lean`) establishes `glvPoint(P+Q) = glvPoint P + glvPoint Q` for
  all branches — the homomorphism *half*. The cryptographically operative claim
  **`glvPoint = [λ]`** (that the endomorphism acts as scalar multiplication by the GLV
  eigenvalue λ on ⟨G⟩) is **now also proved** (`secp256k1_glvPoint_eq_lam_on_zmultiples`,
  `GlvSubgroupEigenvalue.lean`); with `#E = n` giving `⟨G⟩ = ⊤` (`grp_eq_top`) it extends to the
  full point group (`secp256k1_glvHom_eq_zsmul_unconditional`). The scalar eigenvalue facts
  (`glv_lambda_eigenvalue`, `lambda_is_cube_root`, etc.) about λ in `ℤ/n` / β in `𝔽_p` are the
  arithmetic inputs to that action statement.

- **Scope reminder (not a TCB issue, but bears on "what verified means").** The
  discrete-log protocol algebra (Schnorr/EdDSA, DH, ElGamal, Pedersen, Okamoto,
  Chaum–Pedersen, MuSig2/Taproot, Feldman VSS, adaptor/blind Schnorr) is proved over an
  **abstract** `[Module (ZMod n) G]` **and** now also instantiated at the concrete secp256k1
  point group `⟨G⟩` (`ProtocolInstantiation.lean`); it still encodes **no adversary / hash /
  probability model** (see `ABSTRACT_SCOPE.md`).
  Several "soundness/extraction" rows are scalar-field ring identities. These are sound
  Lean theorems; they are simply narrower than their cryptographic prose suggests.
