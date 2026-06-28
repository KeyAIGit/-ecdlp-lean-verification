import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# secp256k1 Weierstrass `c₆` invariant

The `c`-invariants `(c₄, c₆)` are the standard short-Weierstrass coordinates of an
elliptic curve. We already have `c₄ = 0` (the `j = 0` / CM signature). Here we pin
down `c₆`. From Mathlib's `WeierstrassCurve.c₆ = -b₂³ + 36·b₂·b₄ - 216·b₆` and the
proved `b₂ = b₄ = 0`, `b₆ = 28`, we get `c₆ = -216·28 = -6048`, a nonzero residue in
`𝔽_p`. Combined with `c₄ = 0`, Mathlib's `c_relation` (`1728·Δ = c₄³ - c₆²`)
collapses to `1728·Δ = -c₆²` for secp256k1.
-/

namespace Ecdlp.Curve

open WeierstrassCurve

/-- **The secp256k1 `c₆` invariant equals `-6048`.** From `c₆ = -216·b₆` with
`b₆ = 28` (since `b₂ = b₄ = 0`). Mirrors `secp256k1_c₄_eq_zero`. -/
theorem secp256k1_c₆ : secp256k1.c₆ = -6048 := by
  simp only [WeierstrassCurve.c₆, WeierstrassCurve.b₂, WeierstrassCurve.b₄,
    WeierstrassCurve.b₆, secp256k1]
  ring

/-- **The secp256k1 `c₆` invariant is nonzero in `𝔽_p`** (`-6048 ≢ 0 mod p`).
Mirrors `secp256k1_Δ_ne_zero`. -/
theorem secp256k1_c₆_ne_zero : secp256k1.c₆ ≠ 0 := by native_decide

/-- **The discriminant identity for secp256k1.** Mathlib's general
`c_relation : 1728·Δ = c₄³ - c₆²` instantiated at secp256k1; with `c₄ = 0` it
reduces to `1728·Δ = -c₆²`. -/
theorem secp256k1_c_relation : 1728 * secp256k1.Δ = -secp256k1.c₆ ^ 2 := by
  rw [secp256k1.c_relation, secp256k1_c₄_eq_zero]
  ring

end Ecdlp.Curve
