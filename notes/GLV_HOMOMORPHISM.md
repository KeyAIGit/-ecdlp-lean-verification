# GLV endomorphism is a group homomorphism — the reduction

Goal: prove `glvPoint (P + Q) = glvPoint P + glvPoint Q` on `secp256k1.toAffine.Point`,
where `glvPoint` is the GLV map `(x,y) ↦ (β·x, y)` (`Ecdlp/Proved/GlvEndomorphism.lean`,
rungs 1–3 done: it preserves the equation, preserves nonsingularity, and is packaged as
a `Point → Point` map). `β³ = 1`, `β² + β + 1 = 0`, `β ≠ 0`.

## The whole homomorphism reduces to ONE slope identity

Mathlib's affine addition (`WeierstrassCurve.Affine.{slope,addX,addY,negAddY,negY}`,
`Affine/Formula.lean`) computes `P + Q` from a single scalar `ℓ = slope`. For secp256k1
(`a₁=a₂=a₃=a₄=0`, `negY x y = -y`):

- **slope**, secant (`x₁≠x₂`): `(y₁−y₂)/(x₁−x₂)`.
- **slope**, tangent (`x₁=x₂`, `y₁≠-y₂`): `3x₁²/(2y₁)`.
- `addX x₁ x₂ ℓ = ℓ² − x₁ − x₂`;  `negAddY = ℓ(addX−x₁)+y₁`;  `addY = −negAddY`.

**Key identity (the crux):** under `(xᵢ,yᵢ) ↦ (βxᵢ,yᵢ)`,
> `slope(βx₁,βx₂,y₁,y₂) = β² · slope(x₁,x₂,y₁,y₂)`  — in **both** branches.

- secant: `(y₁−y₂)/(β(x₁−x₂)) = β⁻¹·slope = β²·slope`  (because `β³=1 ⇒ β⁻¹=β²`).
- tangent: `3(βx₁)²/(2y₁) = β²·3x₁²/(2y₁) = β²·slope`.

The apparent mismatch (`β⁻¹` vs `β²`) vanishes because `β³=1`. This single scalar `β²`
governing both branches is what makes the map a homomorphism without a case-specific trick.

**Downstream (mechanical `ring`/`linear_combination` with `β³=1`):**
- `addX(βx₁,βx₂, β²ℓ) = (β²ℓ)² − βx₁ − βx₂ = β⁴ℓ² − β(x₁+x₂) = β·(ℓ²−x₁−x₂) = β·addX`  (β⁴=β).
- `negAddY(βx₁,βx₂,y₁,β²ℓ) = β²ℓ·β·(addX−x₁) + y₁ = β³·ℓ(addX−x₁)+y₁ = negAddY`  (β³=1) → Y unchanged.

So `P+Q = (x₃,y₃)` maps to `(βx₃, y₃)` = `glvPoint (P+Q)`, and the addition branch chosen is
preserved because `βx₁=βx₂ ⟺ x₁=x₂` and `negY` is x-independent. ∎ (modulo the slope lemma)

## Plan (incremental, kernel-verified rung by rung)

1. **`secp256k1_glv_slope_of_X_ne`** (secant) — the cleanest piece. *(in progress)*
2. `secp256k1_glv_slope_of_Y_ne` (tangent/doubling) — `negY` x-independence + `2y₁≠0`.
3. `secp256k1_glv_slope_of_Y_eq` (vertical) — both sides `0`.
4. Assemble `secp256k1_glv_slope` (β²·scaling, all branches).
5. `addX`/`negAddY`/`addY` β-equivariance — mechanical.
6. `glvPoint_add : glvPoint (P+Q) = glvPoint P + glvPoint Q` via the `Point.add` case
   analysis (`add_of_X_ne`/`add_of_Y_ne`/`add_of_Y_eq`, `nonsingular_add`).

Mathlib levers: `slope_of_X_ne`, `slope_of_Y_ne`, `slope_of_Y_eq`, `add_some`,
`add_of_X_ne`, `add_of_Y_ne`, `add_of_Y_eq`, `nonsingular_add` (`Affine/{Formula,Point}.lean`).

**Honest difficulty:** the slope lemma (step 1–4) is the only place real cleverness is
needed; it is delicate field arithmetic (`field_simp` + `linear_combination … β³=1`). The
rest is bookkeeping. This is a multi-session rung, not a one-shot — the payoff is the GLV
endomorphism as a *bona fide* `AddMonoidHom` on the curve, the structural fact behind the
GLV scalar decomposition and a real entry in the isogeny/endomorphism layer.
