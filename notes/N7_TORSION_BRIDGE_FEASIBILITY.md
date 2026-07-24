# N7 uniform torsion bridge — feasibility audit and handoff

**Target.** `Ecdlp/Targets/n7_uniform_carrier_induction.lean` →
`nsmul_eq_zero_iff_psi_evalEval_zero (n : ℕ) : n • Point.some x y h = 0 ↔ (secp256k1.ψ (n:ℤ)).evalEval x y = 0`
— the stem's single conceptual wall.

**Method.** Four independent audits (pinned-Mathlib API, PR #13782 dependency DAG, in-repo
inventory, consumer minimality) → four candidate routes → adversarial refutation of each →
synthesis. Every existence claim below was checked against fetched source at the pin
(`refs/tags/v4.31.0`) or against this working tree.

**Status of this document.** Findings only; the one implementation it recommends has landed
(§4). Nothing here asserts a proof the kernel has not seen.

---

## 1. Verdict

Split the question, because the answer differs by half:

| Obligation | Verdict |
|---|---|
| Remove the bridge from the **generic path** of both step lemmas (its 3 live call sites) | **BOUNDED — done**, see §4 |
| The `.mpr` half (`ψₙ(P) = 0 → n•P = 0`) as a standalone theorem | **NOT bounded today** |
| The `.mp` half (`n•P = 0 → ψₙ(P) = 0`) — needed only by 2 degenerate branches | **NOT bounded today** |

**The wall is real and is not open mathematics — but it is not cheap either.** The only known
complete routes are (a) a port of Mathlib PR #13782, realistically 3–6 weeks of expert work,
or (b) a ladder induction resting on an identity that is *numerically verified but unproven*.
Neither should be started without an explicit decision. What *was* cheap is the
de-circularization in §4, and that is now in the built base.

---

## 2. Exact missing API at the pin (Mathlib v4.31.0)

**The first genuinely absent thing: any lemma connecting an `Affine.Point` (or `nsmul`/`zsmul`)
to `ψ`/`φ`/`Ψ`/`ΨSq`/`Φ`.** Verified: in `DivisionPolynomial/Basic.lean` the token `Point`
occurs *once*, on the import line; `evalEval` occurs zero times; in `Degree.lean` both are
absent. Across the whole v4.31.0 `EllipticCurve/` tree `nsmul`/`zsmul` appear only as
`AddCommGroup` instance fields. The Point↔ψ link does not exist at the pin under any name.

Also absent at the pin:

* any `IsCoprime`/`gcd`/`Squarefree` statement about `Φ` and `ΨSq` (**note:** this repo has its
  own — `secp256k1_isCoprime_Φ_ΨSq`, `Ecdlp/Proved/DivisionPolynomialCoprime.lean`, in the built
  base, for every `n : ℤ` with no `char ∤ n` hypothesis);
* the `ω` division polynomial — `Basic.lean` carries a literal `TODO: the bivariate polynomials ωₙ`
  (this is why the stem's carrier is stated ω-free);
* `IsEllDivSequence (normEDS …)`, i.e. `m ∣ n → ψₘ ∣ ψₙ`. Only the `n = 2` case is proved
  (`normEDS_mul_complEDS₂`, `normEDS_dvd_normEDS_two_mul`). `EDS.lean` still carries
  `TODO: prove that normEDS satisfies IsEllDivSequence`. **This repo already paid the elliptic
  half** (`normEDS_isEllSequence`, `Ecdlp/Proved/NormEDSIsElliptic.lean`).

**Present but insufficient — why any lift must be characteristic 0.** `ΨSq_ne_zero`,
`preΨ_ne_zero`, `leadingCoeff_ΨSq` all carry the hypothesis `(n : R) ≠ 0`, which over
`R = ZMod p` fails exactly when `p ∣ n` — and the target quantifies over all `n : ℕ`. This is
not an artefact: for `y² = x³ + 2` over `𝔽₅`, `ψ₅ = 4`, a nonzero *constant* (degree collapsed
from 12 to 0). So a naive "work in `Frac(F[W])` for `F = ZMod p`" shortcut is dead.

---

## 3. PR #13782: anatomy, and a correction

**Correction to an earlier working assumption of this track.** It was assumed that #13782 only
proves the *universal/generic* point is non-torsion, so that porting it would still leave a
specialization argument before reaching a statement about a specific curve over `𝔽_p`. **That is
wrong.** The PR's terminal theorem is for an arbitrary field, curve and nonsingular point:

```lean
theorem zsmul_eq_smulEval {x y : F} (h : Affine.Nonsingular W x y) (n : ℤ) :
    (n • Point.fromAffine (Affine.Point.some h)).point = ⟦smulEval W x y n⟧
```

with `smulEval W x y n = evalEval x y ∘ ![W.φ n, W.ω n, W.ψ n]`. The Jacobian `Z` index is `2`,
so the `Z`-coordinate is literally `(W.ψ n).evalEval x y` — the target's right-hand side. The
universal curve is a *proof device* (the PR's own docstring says it is needed only to reach
char 2 by specializing a char-0 result), and the specialization is performed inside the PR.
Torsion over `𝔽_p` is not an obstruction to it — it is the content: when `n•P` is torsion the
transported identity just says the Jacobian triple is `(φₙ, ωₙ, 0)`, i.e. the point at infinity.

So **a complete port does yield the target**, modulo a small `Jacobian Z = 0 ↔ Point = 0`
bridge (~35 lines; every ingredient exists at the pin: `Point.zero_point`,
`Z_eq_zero_of_equiv`, `equiv_zero_of_Z_eq_zero`, `toAffineAddEquiv`, `fromAffine_some_ne_zero`).

**Cost.** Absent at the pin: `Universal.lean` (198 lines), `Group.lean` (709, redistributed at
the pin into `Affine/Point.lean`), `DivisionPolynomial/ZSMul.lean` (553); plus deltas inside
`EDS.lean` (1304 lines at PR head vs 547 at the pin) and `DivisionPolynomial/Basic.lean` (648
vs 588 — the delta is exactly the `ω`/`ψc` family; `ψc` is free at the pin under the name
`complEDS₂`). Faithful port ≈ 1100–1300 new lines; a secp256k1-only ℤ[1/2] variant that deletes
`Universal.lean` and the `redInvar` block ≈ 700–850.

**The line count is not the binding constraint.** ~120 proof scripts written against mid-2024
Mathlib must re-elaborate against v4.31.0 **with no local toolchain** (module headers,
`add_left_neg → neg_add_cancel`, `field_simp` config syntax, `erw`, `Quotient.eq`, …).
Realistically 15–40 CI iterations, 3–6 weeks of expert work. This is not a drafting job.

---

## 4. What landed: de-circularizing the denominator hypothesis

`Ecdlp/Proved/SevenNonResidue.lean` (built base, kernel-verified, 0 `sorry`).

`p ≡ 1 (mod 7)` and `p ≡ 3 (mod 4)`, so reciprocity gives `(7|p) = −(p|7) = −1`: **7 is not a
square in `𝔽_p`** (Euler's criterion against a closed `native_decide` witness `7^(p/2) ≠ 1`).
Hence substituting `x = 0` into `y² = x³ + 7` would exhibit `7` as a square, so
**no affine point of secp256k1 has `x`-coordinate `0`** (`secp256k1_x_ne_zero`).

The consequence is what matters. Coordinate certificates state the `x`-coordinate of `n•P` in
*divided* form `X = Φₙ(x)/ΨSqₙ(x)`. Because `a / 0 = 0` in Lean, such a statement is vacuous
rather than contradictory when the denominator vanishes — so `ΨSqₙ(x) ≠ 0` had to be supplied
from outside, and in this stem it was supplied by the torsion bridge itself. Here the
implication reverses: `ΨSqₙ(x) = 0` would collapse the divided form to `X = 0`, which no affine
point admits. Junk-value semantics becomes the tool rather than the obstacle:

```lean
theorem secp256k1_psiSq_ne_zero_of_x_eq_div {m : ℤ} {X Y x : ZMod Secp256k1.p}
    (h : secp256k1.toAffine.Nonsingular X Y)
    (hX : X = (secp256k1.Φ m).eval x / (secp256k1.ΨSq m).eval x) :
    (secp256k1.ΨSq m).eval x ≠ 0
```

No torsion theory, no multiplication-by-`n` map, no dependence on #13782. Stated for arbitrary
`m : ℤ`, and (as `secp256k1_den_ne_zero_of_x_eq_div`) for an arbitrary quotient — the numerator
is never inspected, so it applies to any divided-form certificate.

### The handover edit (deliberately NOT applied here)

`psiSq_ne_zero_of_nsmul_some` (stem `:342`) is the *only* consumer of the bridge, via a single
`.mpr` at `:349`. It is applied at exactly three sites, all on the generic path of both step
lemmas — i.e. required for every `n`:

| site | current | replacement |
|---|---|---|
| `:479` `hden` | `psiSq_ne_zero_of_nsmul_some hkP` | `secp256k1_psiSq_ne_zero_of_x_eq_div hk_ns hXk` |
| `:566` `hdenk` | `psiSq_ne_zero_of_nsmul_some hkP` | `secp256k1_psiSq_ne_zero_of_x_eq_div hk_ns hXk` |
| `:568` `hdenk1` | `psiSq_ne_zero_of_nsmul_some hk1P` | `secp256k1_psiSq_ne_zero_of_x_eq_div hk1_ns hXk1` |

Hypothesis availability was checked at each site: `hXk` is obtained at `:478` (before `:479`),
`hXk`/`hXk1` at `:529`/`:530` (before `:566`/`:568`), and `hk_ns`/`hk1_ns` at `:471`/`:519`–`:528`.
`hk`/`hk1` are *hypotheses* of the step lemmas, not conclusions, so **no cycle is introduced**
and none of the four open x/y walls is needed.

These three edits live in the same file as `even_x_algebra`/`odd_x_algebra` and are therefore
left to whoever is working those walls, to avoid a collision. **Effect once applied:** the
bridge's live applications drop 1 → 0 and its remaining scope is exactly the two `sorry`s at
`:513`/`:516` (the `.mp` half at degenerate indices).

### Stale prose in the stem, worth fixing with that edit

* `:62` calls the `Point → ψ` direction (`.mp`) "the genuinely missing" one; the file's only
  application is `.mpr`.
* `:64–65` and `:499–501` say the secant `x`-collision branch is a residual `sorry`; it is fully
  closed at `:534–560` (the inline comment at `:538` is the correct one).
* `:328–331` says the only in-repo route is a joint proof entangled with the x/y walls; §4 is a
  counterexample.
* `:339` cites `eval_ΨSq_eq_normEDS_sq`; the proof at `:350–351` uses `ΨSq_eval_eq_ψ_evalEval_sq`.

---

## 5. Bounded follow-ups (not yet done)

Both are small, useful to every route, and need only the pin plus existing repo lemmas:

1. `secp256k1_psi_evalEval_eq_normEDS` — `(secp256k1.ψ n).evalEval x y = normEDS (2y) (Ψ₃.eval x) (preΨ₄.eval x) n`.
   ~12 lines from `ψ`'s definition as `normEDS …` plus `map_normEDS` and `evalEvalRingHom`. All
   the concrete evaluations already exist (`secp256k1_psi2_evalEval`, `secp256k1_Ψ₃_eval`,
   `secp256k1_preΨ₄_eval`, `secp256k1_Ψ₂Sq_eval`). Verified absent from the repo.
2. `secp256k1_psi_evalEval_not_consecutive_zero` — point-level Ward rigidity over `𝔽_p`, ~25
   lines from (1) plus the landed `normEDS_not_consecutive_zeros`, with the two non-degeneracy
   side conditions from `secp256k1_isCoprime_Ψ₂Sq_Ψ₃` and `secp256k1_isCoprime_Ψ₃_preΨ₄` via
   `no_common_root_of_isCoprime`.

---

## 6. Dead ends (recorded so they are not re-attempted)

* **Cleared-`Carrier` + `Φ/ΨSq` coprimality.** The de-circularization is real, but the only
  producer of the x-conjunct at a *symbolic* index is the `normEDSRec'` assembly whose two steps
  are `even_x_algebra`/`odd_x_algebra` — both open. Entangled. It also transfers zero difficulty
  (`even_x_algebra` already takes `hden` as a hypothesis), and coprimality is silent about `.mp`.
  §4 cuts the same cycle for a fraction of the cost and touches no existing statement.
* **Ward rank-of-apparition.** Every cited dependency exists, but the route needs `ρ ∣ N` and its
  own argument delivers `N ∣ ρ`; and reaching the anchor `ψ_N(P) = 0` again needs a cleared
  Carrier, so it is entangled, not independent.
* **Index doubling from the landed n = 2,3,4 bridges.** Mathlib's `ψ_even` gives only the
  *difference* `ψ_{k−1}²ψ_{k+2} − ψ_{k−2}ψ_{k+1}²`, and only via `ψ_{2k}·ψ₂`, whose vanishing is
  equivalent to `y(kP) = 0` — i.e. it needs the y-carrier.
* **`ord(P)` + `ψ_m ∣ ψ_n`.** General EDS divisibility is unproved at the pin (see §2), and
  `ρ = ord(P)` needs the multiplication map — circular at the root.
* **Extending the per-`n` certificate technique to symbolic `n`.** There is no schema:
  `SevenTorsionBridge.lean` carries a single ~4.7 kB `linear_combination`, and certificate size
  grows with `n`. Confirmed across all landed per-`n` bridges.

**General answer to "is there a route avoiding the multiplication-by-`n` coordinate map?" — No.**
`ψₙ`'s zero locus *being* `E[n]` is the whole content of the wall.

---

## 7. The one unproven idea, flagged as such

A ladder route was proposed resting on a new "sum" companion to Somos-4:

```
w(k−1)²·w(k+2) + w(k−2)·w(k+1)²  =  6x²·w(k−1)w(k)w(k+1) − 4y²·w(k)³        (E1)
```

for `w(n) = ψₙ(P)`. Mathlib has the *difference* form (`complEDS₂`); this sum form is **absent
from Mathlib v4.31.0, from PR #13782, and from this repo**.

It was checked numerically and reproduced independently: 5 prime fields × 4 points each ×
indices 1..39, zero failures. That is strong evidence it is a true identity — **it is not a
proof, and no part of it has been through the kernel.** Per the "models are drafters only"
rule, no Lean was written for it.

**If this route is ever taken, the first step is a throwaway CI probe of (E1) alone.** If (E1)
does not close in the kernel, the route is void and everything built on it is wasted. That is
the single decision point.

---

## 8. Recommendation

1. Apply the three-line handover edit of §4 when the stem is next open (whoever owns the x-walls).
2. Land the two bounded follow-ups of §5.
3. Decide explicitly between the #13782 port (§3 — expensive but complete, and the *only* known
   route that also yields the `y`-conjunct the two y-walls need) and the ladder (§7 — cheaper but
   gated on an unproven identity). Do not start both.
4. Do **not** attempt: the naive `Frac(F[W])` shortcut (§2), the dead ends of §6, or a faithful
   full port when the secp256k1-only variant dominates it (§3).
