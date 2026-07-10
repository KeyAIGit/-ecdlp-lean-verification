# TRUST_REPORT.md — trust-boundary report for the ECDLP Lean layer

> Counts here are a snapshot; the single canonical figure is **`STATUS.md`** (generated from `data/stats.json`). If they differ, STATUS.md wins.

**Scope of the verified body.** `221 ledger rows / ~185 distinct kernel-verified
results` (≈36 of the 221 rows are alternate-form or `supporting:` restatements of the
same underlying fact — e.g. the `ZMod`/ring forms of the GLV eigenvalue, or the
concrete-`⟨G⟩` instantiations of the abstract protocol suite — so they do
not add new content). **0 `sorry`, 0 `admit`, 0 open obligations, 0 custom axioms.**

This document states *precisely* what "verified" rests on, which results extend the
trusted computing base (TCB) via the Lean compiler, and what CI actually enforces
versus merely documents. It is the catalogue referenced by the axiom-audit note in
`VERIFIED.md` and by `Ecdlp/AxiomAudit.lean`.

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
directly or transitively). There are **no uses of the kernel `decide` tactic anywhere**
in `Ecdlp/` (a grep for the `decide` tactic returns no matches); the only decision
procedure that appears at scale is `native_decide`.

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

**Count.** Approximately **33 load-bearing results depend on `Lean.ofReduceBool`**
(buckets (b) + (c) combined, including the two primality theorems) — the disclosed
compiler-trusted set. The large majority of the ledger is pure-kernel (bucket (a)); for
the current ledger total see **`STATUS.md`** / `data/stats.json`.

---

## 3. What CI actually ENFORCES vs documents

`.github/workflows/ci.yml` runs the following gates on every push / PR / dispatch.
Distinguishing *machine-enforced* (a red build blocks merge) from *documentation-only*:

| Step (ci.yml) | What it does | Enforced? |
|---|---|---|
| `Check count consistency (docs)` — `scripts/check_counts.py` | Fails if any **retired** headline count string ("128 theorems verified", "~99 named", …) reappears in the narrative docs, and asserts the canonical strings `"210 ledger rows"` and `"~177 distinct"` are present in `VERIFIED.md`. | **MACHINE-ENFORCED** (substring scan; build-breaking). Note: it pins the *wording*, not the actual theorem count — it cannot detect a genuinely miscounted ledger, only drift back to a retired phrasing. |<!-- count-check: ignore (this row documents the gate and quotes retired strings as examples) -->
| `Ensure no incomplete proofs remain` | `grep -rniI --include='*.lean' --exclude-dir=Targets 'sorry' Ecdlp/` — fails if `sorry`/`admit` text appears in any **built** `.lean` file. `Ecdlp/Targets/` (open stems) is excluded by design. | **MACHINE-ENFORCED**, with the documented scope limit that it is a *text* grep over built files and deliberately skips `Targets/`. |
| `Ensure no built file imports an open target stem` | `grep` for `import Ecdlp.Targets` outside `Targets/`. Closes the hole where a built file could pull a `sorry`-bearing stem into the build graph (since `sorry` is only a warning). | **MACHINE-ENFORCED.** This is the guard that makes the previous grep sound. |
| `Fetch prebuilt Mathlib cache` + `Build and verify ALL proofs` — `lake build` | The **kernel** re-checks every built proof term. A `sorry` that reached the build graph, or any type error, fails here. | **MACHINE-ENFORCED.** This is the core verification: a green `lake build` means the kernel accepted every built theorem. |
| `Axiom audit (no sorryAx, no custom axioms)` — `lake env lean Ecdlp/AxiomAudit.lean` → `scripts/check_axioms.py` | Runs `#print axioms` on the headline results and fails if any depends on `sorryAx`, `Lean.trustCompiler`, `Lean.guardMsgsAx`, or **any axiom outside** `{propext, Classical.choice, Quot.sound, Lean.ofReduceBool}`. Also reports which audited results use `native_decide`. The checker also fails closed if the audit file does not elaborate (unknown name / Lean error). | **MACHINE-ENFORCED** — this is what upgrades "no custom axioms" from a claim to a checked property, and what surfaces every `Lean.ofReduceBool` dependency. **Caveat:** it audits only the *explicitly listed* theorems in `AxiomAudit.lean` (a representative headline set), not the entire ledger; a custom axiom introduced in an un-listed theorem would not be caught by this gate (though it would still need to pass `lake build`). |
| `Typecheck open target stems (non-blocking)` | `lake env lean` over `Ecdlp/Targets/*.lean`; `continue-on-error: true`. | **DOCUMENTATION/INFO ONLY.** A stem failing to typecheck emits a warning, never blocks. |
| `Featherless API smoke test`, `Prover target attempt`, report upload | All `continue-on-error: true` and skipped on PRs. | **DOCUMENTATION/INFO ONLY.** Prover orchestration; cannot affect the verification verdict. |

**Net guarantee:** a green `main` machine-guarantees that (i) every built theorem is
kernel-accepted with no `sorry`, (ii) no built file imports an open stem, and (iii) the
audited headline results depend only on the allowed trusted base — i.e. no custom
axioms, and every compiler-trusted (`native_decide`) result is disclosed. The
count-consistency and stem-typecheck steps are doc-hygiene, not correctness guarantees.

---

## 4. Honest caveats

- **"0 axioms" is shorthand for "no axioms beyond the standard three."** Every result
  uses Mathlib and therefore transitively `{propext, Classical.choice, Quot.sound}`.
  The honest claim is: **no custom axioms, no `sorryAx`** — machine-enforced by the
  axiom-audit gate. It is *not* a claim of axiom-free foundations.

- **~33 load-bearing 256-bit facts are `native_decide` and therefore compiler-trusted.**
  These extend the TCB beyond the kernel to include the Lean compiler/runtime, via
  `Lean.ofReduceBool`. This means CLAUDE.md's invariant "the Lean kernel is the only
  judge of correctness" is, strictly, **not true for these ~33 rows** — the compiler is
  also a judge. This is **REVIEW_DOSSIER.md finding 9** ("`native_decide` enlarges the
  TCB beyond the kernel"; severity LOW), whose verdict is *ACCEPTABLE trade-off,
  honestly fixable*: the mitigation is correct where it matters most — the primality of
  `p` and `n` structures `native_decide` to discharge only small checks inside a
  kernel-checked Lucas argument (Section 2(c)). This report is the disclosure that
  finding 9 asked VERIFIED.md to carry.

- **The GLV map is proved an ADDITIVE endomorphism, but the eigenvalue identity is
  NOT proved.** `Ecdlp.Curve.glvPoint_add` (bundled as `glvHom : Point →+ Point` in
  `Ecdlp/Proved/GlvHom.lean`) establishes `glvPoint(P+Q) = glvPoint P + glvPoint Q` for
  all branches — the homomorphism *half* only. The cryptographically operative claim
  **`glvPoint = [λ]`** (that the endomorphism acts as scalar multiplication by the GLV
  eigenvalue λ on ⟨G⟩) is **not** proved. The eigenvalue facts that *are* proved
  (`glv_lambda_eigenvalue`, `lambda_is_cube_root`, etc.) are statements about the scalar
  λ in `ℤ/n` / β in `𝔽_p`, not about the action of `glvPoint` on the point group.

- **Scope reminder (not a TCB issue, but bears on "what verified means").** The
  discrete-log protocol algebra (Schnorr/EdDSA, DH, ElGamal, Pedersen, Okamoto,
  Chaum–Pedersen, MuSig2/Taproot, Feldman VSS, adaptor/blind Schnorr) is proved over an
  **abstract** `[Module (ZMod n) G]`, **not instantiated at the secp256k1 point group**,
  and encodes **no adversary / hash / probability model** (see `ABSTRACT_SCOPE.md`).
  Several "soundness/extraction" rows are scalar-field ring identities. These are sound
  Lean theorems; they are simply narrower than their cryptographic prose suggests.
