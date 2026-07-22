# N7 even-x doubling identities — machine-verified analysis (2026-07-22)

Rigorous CAS (sympy/Gröbner) investigation of the two polynomial identities the `even_x_algebra`
wall of `Ecdlp/Targets/n7_uniform_carrier_induction.lean` reduces to. **Purpose:** record exactly
what is true, why there is no blind shortcut, and the turnkey structure for completion once a
Lean-*running* certificate generator (polyrith+solver / a prover-loop drafter / local Lean) is
available. All facts below are machine-checked (sympy scripts in the session scratchpad).

## The two identities (secp256k1, `y²=x³+7`; univariate in `ℤ[X]`, all `k:ℤ`)

    (I1)  ΨSq(2k) = 4·ΨSq(k)·(Φ(k)³ + 7·ΨSq(k)³)
    (I2)  Φ(2k)   = Φ(k)⁴ − 56·Φ(k)·ΨSq(k)³

**Status: TRUE.** Verified as exact `ℤ[X]` identities for `k = −4 … 7` against Mathlib's exact
`preNormEDS` recurrence (`ground_truth.py`). Base sanity: `ΨSq(1)=1, Φ(1)=X, ΨSq(2)=4X³+28,
Φ(2)=X⁴−56X`.

## Mathlib definitions used (all confirmed against v4.31.0, rev `fabf563a…`)

    preΨ n = preNormEDS (Ψ₂Sq²) Ψ₃ preΨ₄ n
    ΨSq n  = preΨ(n)² · (Even n ? Ψ₂Sq : 1)
    Φ n    = X·ΨSq n − preΨ(n+1)·preΨ(n−1)·(Even n ? 1 : Ψ₂Sq)
    Ψ₂Sq = 4X³+28,  Ψ₃ = 3X⁴+84X,  preΨ₄ = 2X⁶+280X³−784
    preΨ_even m: preΨ(2m)   = preΨ(m−1)²preΨ(m)preΨ(m+2) − preΨ(m−2)preΨ(m)preΨ(m+1)²
    preΨ_odd  m: preΨ(2m+1) = preΨ(m+2)preΨ(m)³·(Even m?Ψ₂Sq²:1) − preΨ(m−1)preΨ(m+1)³·(Even m?1:Ψ₂Sq²)

## No Mathlib shortcut

Mathlib's division-polynomial API gives only the `n ↦ 2m` recurrence direction
(`preΨ_even/odd`, `ΨSq_even/odd`, `ΨSq_two/Φ_two`, the `@[simp]` `*_neg` evenness lemmas). There is
**no** lemma expressing `ΨSq`/`Φ` at the *doubling* `k ↦ 2k` in terms of level-`k` data. Repo grep
confirms none exists.

## No finite / local certificate — proven

After a one-level expansion (via `ΨSq_even k`), the residual of (I1) modulo the Somos ideal at a
bounded window is a nonzero remainder (25 terms mod `⟨Somos(k−1,k,k+1)⟩`; still ≠0 mod
`⟨Somos(k−2..k+2)⟩`). **Root cause:** the squared term `preΨ(k±2)²` ("distance-0") is not reducible
by the *product-only* Somos-4 relation (which relates only the product `preΨ(k+2)·preΨ(k−2)`);
reducing a square introduces `preΨ(k±3)`, cascading outward without bound. So (I1)/(I2) are **not**
a finite `linear_combination` over the recurrences — no blind shortcut exists.

## The `preΨ`-Somos-4 relation (companion brick — landable now)

    preΨ(m+2)·preΨ(m−2) = (Even m ? 1 : Ψ₂Sq²)·preΨ(m+1)·preΨ(m−1) − Ψ₃·preΨ(m)²

Verified `m = −3 … 7`. **Provable from the landed `Ecdlp.NormEDS.normEDS_somos4`** (no new
induction): adjoin `b` with `b²=Ψ₂Sq` (so `b⁴=Ψ₂Sq²` = `preΨ`'s first `preNormEDS` parameter),
whence `normEDS b Ψ₃ preΨ₄ n = preΨ(n)·(Even n ? b : 1)`; substitute into `normEDS_somos4`, cancel
parity `b`-factors, pull back through the injective coefficient map. (Being landed separately as
`secp256k1_preΨ_somos4`.)

## The `normEDSRec'` induction closes — verified

Predicate `P k := (I1@k) ∧ (I2@k)`. With inductive hypothesis `P` at `{M−1, M, M+1}` (even step,
`M=m+3`) resp. `{M, M+1}` (odd step, `M=m+2`), **plus** the `preΨ`-Somos-4 relation at
`{M−1,M,M+1}`, **all 8 step obligations** (even/odd × `M` even/odd × I1/I2) reduce to `0` modulo the
ideal (Gröbner, `allsteps.py`). The `M±1` hypotheses are required — `IH@M` alone does not close.

## Why it is not completable as a blind `linear_combination`

The fully-expanded even-step goal is **degree 36** in the 7 level-`M` `preΨ` atoms; the required
cofactors are **≈1400–2500 terms each (degree 28–34)**, and `sympy.reduced` leaves a nonzero
remainder (the 9 relation generators are not a Gröbner basis, so cofactors are not cleanly
extractable). Root cause: `P(2M)` reaches `ΨSq(4M)=preΨ(4M)²·Ψ₂Sq`, a *double* doubling (deg ≈32),
and odd-index `ΨSq(2M±1)=preΨ(2M±1)²` is not captured by `P` (only even indices `2k`), forcing a
deg-16 level-`M` chunk. A `linear_combination` of this size can neither be written by hand nor
elaborated by `ring1` (OOM/timeout even at `maxHeartbeats 6400000`).

## Completion paths (turnkey)

1. **Certificate generator inside Lean** — `polyrith` with a Sage/solver backend, or a prover-loop
   drafter (Kimi/DeepSeek) iterating `linear_combination` candidates against the kernel. The
   induction scaffold + the 8 Gröbner-verified obligations tell the generator exactly what to prove.
2. **Group-law / coordinate-ring bridge** — `x([2k]P) = x([2]∘[k]P)`, using the landed point bridges
   (`ΨSq_eval_eq_ψ_evalEval_sq`, `Φ_eval_eq_φ_evalEval`) + tangent-doubling `addX` + coprimality of
   `Φ(2k),ΨSq(2k)` (degree/root matching). Avoids the giant certificate but needs the mult-composes
   fact at the point level.
3. **Upstream Mathlib** — a general division-polynomial duplication formula.

`even_y_algebra` has the identical structure (ω-recurrence at `2k`) and the same verdict.

## All four walls: independent point-level validation (2026-07-22)

Separately from the univariate `(I1)/(I2)` check above, all **four** algebra walls were validated
directly at the group-law/point level (`odd_wall_verify.py`): build the secp256k1 division
polynomials in `E = ℚ[x,y]/(y²−x³−7)` (elements `a(x)+b(x)·y`, exact `/(2y)` in the even
recurrence), form the point coordinates `x(nP)=φₙ/ψₙ²`, `y(nP)=(ψ_{n+2}ψ_{n−1}²−ψ_{n−2}ψ_{n+1}²)/(4y·ψₙ³)`,
apply the affine group law (tangent slope `3X²/2Y` for `2k`; secant slope `(Yₖ−Y_{k+1})/(Xₖ−X_{k+1})`
for `2k+1`), and compare to the canonical ratio/`ψ`-product at the doubled index.

**Result — all TRUE for `k = 1,2,3,4`:** `even_x`, `even_y`, `odd_x`, `odd_y` each hold as exact
identities on the curve. This independently confirms the four wall *statements* (as restated with
the `Carrier` y-coupling, 2026-07-21) are genuine theorems — a fact the open `sorry`s cannot attest.

**Degree profile.** `deg_x ψ_{2k+1} = (n²−1)/2` (4, 12, 24, 40 at `n = 3,5,7,9`), so the concrete
per-`k` polynomials grow quadratically — there is no fixed-degree per-`k` certificate, and the
uniform (symbolic-`k`) proof must go through the `ψ`-net relations.

**Odd (secant) walls — same verdict.** The `odd_x`/`odd_y` closure has both halves already landed
(`secp256k1_secant_addX_cleared` geometry, `φ_ψ_diff_evalEval` arithmetic), but assembling them pins
`Yₖ·Y_{k+1}` from the two `Carrier` y-conjuncts (products of `ψ` over `k−2 … k+3`) and must reduce
those to `ψ_{2k+1}²` — i.e. bridge the `{k}`-cluster to the `{2k}`-cluster, the *same* degree-heavy
doubling step as `even_x`. So the odd walls are in the same certificate-generator class, not a short
`linear_combination` fill; the completion paths above apply uniformly to all four.
