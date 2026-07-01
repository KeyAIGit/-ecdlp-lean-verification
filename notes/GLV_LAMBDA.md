# Toward `glvPoint = [λ]` — the honest bottleneck, and a reachable substitute

The cryptographically load-bearing GLV fact is that the endomorphism `glvPoint`
`(x,y) ↦ (β·x, y)` acts as scalar multiplication by `λ` on the base-point subgroup
`⟨G⟩`: `glvPoint G = λ • G`, with `λ ≈ 2^128`, `λ² + λ + 1 ≡ 0 (mod n)`. We proved
`glvPoint` is an additive endomorphism (`glvPoint_add`, bundled as `glvHom`). What is
still open, and why.

## Why `glvPoint G = λ • G` is NOT directly reachable now
- `λ • G` is `G` added to itself `λ ≈ 2^128` times. Direct `nsmul` is infeasible, and
  `native_decide` cannot reach it (it would enumerate ~2^128 group operations).
- The clean structural route is: on the prime-order group `⟨G⟩` (order `n`), every
  endomorphism is `[k]` for a unique `k ∈ ℤ/n` (because `End(ℤ/n) ≅ ℤ/n`), and
  `glvPoint` restricted to `⟨G⟩` is a root of `x²+x+1`, hence `k = λ` or `λ²`. This
  needs: (i) `⟨G⟩` has order exactly `n` and `glvPoint` maps `⟨G⟩` into `⟨G⟩`, which
  needs (ii) **`#E(𝔽_p) = n`** — point counting. **Mathlib has no Schoof/point-counting,
  and `native_decide` cannot compute `#E` over a 256-bit field.** This is the precise
  keystone bottleneck (it also gates instantiating the protocol algebra at the real
  group — see `ABSTRACT_SCOPE.md`).

So `glvPoint = [λ]` is blocked behind `#E(𝔽_p) = n`. Faking it (e.g. closing the abstract
cyclic-propagation stem `glv_root_mod_n_condition_008` and calling `[λ]` done) would be
dishonest — that stem is the eigenvector-propagation step, not the curve-level eigenvalue.

## The reachable substitute (the real algebraic content): `φ² + φ + 1 = 0`
What *is* reachable now — and is the genuine CM/endomorphism-ring fact behind GLV — is the
**minimal-polynomial relation of the endomorphism** on the *whole* curve, no `λ`, no `n`,
no point counting:

> **`glvPoint (glvPoint P) + glvPoint P + P = 0`** for every `P : secp256k1.toAffine.Point`.

i.e. `φ² + φ + 1 = 0` in `End(E)`, the statement that `glvPoint` is a primitive cube root
of unity in the endomorphism ring (the CM-by-ℤ[ζ₃] structure of the `j = 0` curve).

### Why it is true and provable by the addition formula
For `P = (x, y)`, the three points `P = (x,y)`, `φP = (βx, y)`, `φ²P = (β²x, y)` share the
**same `Y`-coordinate** `y`, so they lie on the **horizontal line `Y = y`**. That line
meets `Y² = X³ + 7` where `X³ = y² − 7`, whose three roots are exactly `x, βx, β²x` (the
cube-root-of-unity multiples). Three collinear points on an elliptic curve sum to `O`:

  `(x,y) + (βx,y) + (β²x,y) = O`.

Direct affine-formula check (the secant slope is `0` because the `Y`'s are equal):
- `(x,y) + (βx,y)`: `x₁ ≠ x₂`, slope `= (y−y)/(x−βx) = 0`, so
  `addX = 0 − x − βx = −(1+β)x = β²·x` (using `1 + β = −β²` from `β²+β+1=0`), and
  `addY = −(0·(…) + y) = −y`. Hence `(x,y)+(βx,y) = (β²x, −y) = −(β²x, y)`.
- adding `(β²x, y)`: `−(β²x,y) + (β²x,y) = O`. ∎

So `φ²P + φP + P = O`. This is a concrete coordinate identity, in reach of the same
machinery used for `glvPoint_add` (Mathlib `WeierstrassCurve.Affine` addition + `β²+β+1=0`).

### Edge cases to handle in the Lean proof
- `P = 0` (point at infinity): `0 + 0 + 0 = 0`. Trivial.
- `x = 0` (only if `7` is a square mod `p`, giving `P = (0, ±√7)`): then `x = βx = β²x = 0`,
  the three points coincide, the horizontal line is a *triple* contact (3-torsion), and the
  identity becomes `3 • (0, y) = 0` — the `Ψ₃` 3-torsion fact. Handle via the
  doubling/tangent branch (or show `x = 0` has no curve point if `7` is a non-residue).

## Plan
1. **`secp256k1_glv_cube_relation`** ✅ **DONE** (`Ecdlp/Proved/GlvCubeRelation.lean`,
   kernel-verified): `glvPoint (glvPoint P) + glvPoint P + P = 0` for all `P`. Upgrades
   `glvHom` from "an additive endomorphism" to "a primitive-cube-root-of-unity
   endomorphism" — a verified `ℤ[ζ₃] → End(E)` in spirit. This is a *different, reachable*
   fact from `glvPoint = [λ]` (below), which stays blocked on point-counting.
2. Only **after** `#E(𝔽_p) = n` exists (a separate, hard, point-counting project — likely
   out of reach without new Mathlib foundations) can `φ² + φ + 1 = 0` on `End(E)` be
   transferred to `[λ]` on `⟨G⟩`. Until then, `glvPoint = [λ]` stays explicitly open.

The honest headline: GLV gives a verified **cube-root-of-unity endomorphism** of secp256k1;
the **`[λ]`-scalar** identification is gated on point counting and remains open.
