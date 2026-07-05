import Mathlib
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.GlvAutomorphism
import Ecdlp.Proved.GlvFixedLocus

/-!
# The GLV automorphism acts on the torsion of secp256k1

The GLV / complex-multiplication endomorphism `glvPoint : (x, y) ↦ (β·x, y)` of secp256k1
is already known in this repository to be

* an **additive endomorphism** of the point group (`glvHom : Point →+ Point`,
  `GlvHom.lean` / `GlvMonoidHom.lean`);
* an **order-3 automorphism**: `glvPoint³ = id` (`glvPoint_cube_eq_id`) and hence
  bijective (`glvPoint_bijective`), a primitive cube root of unity in `End(E)`
  (`GlvOrderThree.lean` / `GlvMinPoly.lean`);
* with fixed locus inside `E[3]`: `glvPoint P = P ⇒ 3·P = O`
  (`secp256k1_glvPoint_fixed_three_torsion`, `GlvFixedLocus.lean`).

This file records two "endomorphism ↔ torsion" interaction facts that follow from those
objects.

**CM automorphism acts on torsion.** Because `glvHom` is an additive homomorphism it
commutes with `n • (·)`, so it sends the `n`-torsion set `E[n] = {P | n • P = 0}` into
itself; being an order-3 *automorphism* (inverse `glvPoint²`, also mapping `E[n]` into
itself) it restricts to a **bijection** of `E[n]`. This is `secp256k1_glvPoint_bijOn_torsion`:
the CM automorphism permutes the `n`-torsion.

**Fixed locus of the GLV endomorphism meets `E[n]` trivially when `gcd(n, 3) = 1`.** A
point fixed by `glvPoint` lies in `E[3]` (the ramification locus of `E → E/⟨φ⟩`). If it is
also in `E[n]` with `n` coprime to `3`, then its order divides both `n` and `3`, hence
divides `gcd(n, 3) = 1`, so the point is `O`. This is
`secp256k1_glvPoint_fixed_coprime_three` — the same `Nat.Coprime`/`addOrderOf`-divides
idiom as `secp256k1_odd_two_torsion_disjoint` (`TorsionCoprime.lean`).

Both facts need only the machine-checked primality of `p` (for the point group); no new
axioms.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The GLV endomorphism maps `E[n]` into itself.** If `n • P = O` then, since `glvHom`
is additive (`glvHom (n • P) = n • glvHom P`) and `glvPoint = glvHom`, we get
`n • glvPoint P = glvHom (n • P) = glvHom O = O`. So `glvPoint` restricts to a self-map of
the `n`-torsion set `{P | n • P = 0}`. -/
theorem secp256k1_glvPoint_mapsTo_torsion (n : ℕ) :
    Set.MapsTo glvPoint {P : secp256k1.toAffine.Point | n • P = 0}
                        {P : secp256k1.toAffine.Point | n • P = 0} := by
  intro P hP
  simp only [Set.mem_setOf_eq] at hP ⊢
  rw [← glvHom_apply, ← map_nsmul, hP, map_zero]

/-- **The CM automorphism permutes the `n`-torsion: `glvPoint` is a bijection of `E[n]`.**
The GLV endomorphism restricts to a `Set.BijOn` of the `n`-torsion set `{P | n • P = 0}`
onto itself. *Maps into itself*: `secp256k1_glvPoint_mapsTo_torsion` (additivity of
`glvHom`). *Injective on the set*: from the global injectivity `glvPoint_bijective`.
*Surjective onto the set*: given `Q ∈ E[n]`, the preimage `glvPoint (glvPoint Q)` lies in
`E[n]` (apply the maps-into fact twice) and `glvPoint (glvPoint (glvPoint Q)) = Q` by
`glvPoint³ = id` (`glvPoint_cube_eq_id`). Thus the order-3 CM automorphism acts as a
permutation of `E[n]`. -/
theorem secp256k1_glvPoint_bijOn_torsion (n : ℕ) :
    Set.BijOn glvPoint {P : secp256k1.toAffine.Point | n • P = 0}
                       {P : secp256k1.toAffine.Point | n • P = 0} := by
  refine ⟨secp256k1_glvPoint_mapsTo_torsion n, ?_, ?_⟩
  · -- injective on the set (from global injectivity)
    exact fun a _ b _ h => glvPoint_bijective.injective h
  · -- surjective onto the set: the inverse `glvPoint²` also stays in `E[n]`
    intro Q hQ
    exact ⟨glvPoint (glvPoint Q),
      secp256k1_glvPoint_mapsTo_torsion n (secp256k1_glvPoint_mapsTo_torsion n hQ),
      glvPoint_cube_eq_id Q⟩

/-- **The fixed locus of the GLV endomorphism meets `E[n]` trivially when `gcd(n, 3) = 1`.**
If `n` is coprime to `3`, then the only `n`-torsion point fixed by `glvPoint` is `O`.
Indeed a fixed point satisfies `3 • P = O` (`secp256k1_glvPoint_fixed_three_torsion`, the
fixed locus lies in `E[3]`), and combined with `n • P = O` its order divides both `n` and
`3`, hence divides `gcd(n, 3) = 1`, forcing `P = O`. The coprime-`3` fixed-point-freeness
of the CM automorphism — the group-law shadow of `ker(φ − 1) ⊆ E[3]`. -/
theorem secp256k1_glvPoint_fixed_coprime_three {n : ℕ} (hcop : Nat.Coprime n 3)
    (P : secp256k1.toAffine.Point) (hn : n • P = 0) (hfix : glvPoint P = P) :
    P = 0 := by
  have h3 : (3 : ℕ) • P = 0 := secp256k1_glvPoint_fixed_three_torsion P hfix
  have hdn : addOrderOf P ∣ n := addOrderOf_dvd_of_nsmul_eq_zero hn
  have hd3 : addOrderOf P ∣ 3 := addOrderOf_dvd_of_nsmul_eq_zero h3
  have hcop' : Nat.gcd n 3 = 1 := hcop
  have h1 : addOrderOf P ∣ 1 := hcop' ▸ Nat.dvd_gcd hdn hd3
  have h0 : (1 : ℕ) • P = 0 := addOrderOf_dvd_iff_nsmul_eq_zero.mp h1
  simpa using h0

end Ecdlp.Curve
