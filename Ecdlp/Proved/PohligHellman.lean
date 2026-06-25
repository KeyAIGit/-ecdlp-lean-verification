import Mathlib

/-!
# The Pohlig–Hellman reduction

Why the discrete-log problem is only as hard as its largest prime-power-order
subgroup — hence why secp256k1 fixes the base-point order `n` to be **prime** (one
large factor, no reduction to smaller DLPs).

For `g` of order `n` and `h = g^x`, Pohlig–Hellman recovers `x` by:
1. **Projection** — for each `d ∣ n`, the element `g^(n/d)` has order exactly `d`,
   so the DLP projects into the order-`d` subgroup `⟨g^(n/d)⟩`.
2. **Component** — the image `h^(n/d)` of `h` there depends only on `x mod d`, so
   recovering `x mod d` is a discrete log in the *smaller* group of order `d`.
3. **Reconstruction (CRT)** — over the coprime prime-power factors of `n`, the
   residues `x mod pᵢ^eᵢ` reconstruct `x` uniquely.

These three steps (composing Mathlib's `orderOf_pow_orderOf_div`, `pow_mod_orderOf`,
and `ZMod.chineseRemainder`) are the full reduction, recorded here as explicit,
verified nodes in the ECDLP knowledge base.
-/

namespace Ecdlp.PohligHellman

variable {G : Type*} [Group G]

/-- **Projection.** For `d ∣ orderOf g`, the element `g ^ (orderOf g / d)` has order
exactly `d`: the discrete log in `⟨g⟩` projects into an order-`d` subgroup. -/
theorem projection (g : G) {d : ℕ} (hg : orderOf g ≠ 0) (hd : d ∣ orderOf g) :
    orderOf (g ^ (orderOf g / d)) = d :=
  orderOf_pow_orderOf_div hg hd

/-- **Component.** The image of `h = g^x` in the order-`d` subgroup depends only on
`x mod d`: `(g^(n/d))^x = (g^(n/d))^(x mod d)`. Recovering `x mod d` is therefore a
discrete log in the smaller group of order `d`. -/
theorem component (g : G) {d : ℕ} (hg : orderOf g ≠ 0) (hd : d ∣ orderOf g) (x : ℕ) :
    (g ^ (orderOf g / d)) ^ x = (g ^ (orderOf g / d)) ^ (x % d) := by
  rw [← pow_mod_orderOf, projection g hg hd]

/-- **Reconstruction (CRT).** For coprime `a b`, a residue `x : ZMod (a*b)` is in
bijection with its components `(x mod a, x mod b)`; so the per-subgroup discrete logs
reconstruct the full discrete log. -/
theorem reconstruct {a b : ℕ} (h : a.Coprime b) :
    Function.Bijective (ZMod.chineseRemainder h) :=
  (ZMod.chineseRemainder h).toEquiv.bijective

end Ecdlp.PohligHellman
