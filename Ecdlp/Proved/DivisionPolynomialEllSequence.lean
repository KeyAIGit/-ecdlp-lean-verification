/-
# The elliptic-net (EDS) algebraic engine for division polynomials — ω-free (N7 grind)

The ultracode attack on the uniform-N7 step wall settled that the x-coordinate recursion is
provable **ω-free** (no y-coordinate division polynomial) via the elliptic-net structure of `ψ`.
This file lands that engine, curve-generic (any Weierstrass curve over any `CommRing`), upstream-grade:

* `ψ_isEllSequence` — `ψ` satisfies Mathlib's three-term elliptic-net relation (it IS `normEDS`
  definitionally, so the repo's `normEDS_isEllSequence` applies verbatim).
* `ψ_succ_mul_ψ_pred` — `ψ(n+1)·ψ(n-1) = X·ψₙ² − φₙ` (a rearrangement of Mathlib's `φ` definition).
* `φ_ψ_diff` — the **x-coordinate difference identity** `φₙ·ψₘ² − φₘ·ψₙ² = ψ(m+n)·ψ(m-n)`
  (Silverman, *Arithmetic of Elliptic Curves*, III Ex. 3.7): the `r=1` specialisation of the net
  relation, the ω-free core of the multiplication-by-`n` x-formula.

These are the algebraic soul of the uniform N7 induction. The **residual barrier** stays the
`Point`-group assembly (double induction on consecutive pairs `(nP,(n-1)P)`, degenerate-case
analysis, and the still-absent-from-Mathlib `Point ↔ ψ/φ` map) — see `BARRIERS.md §B3`. Grind-in-
progress: not imported into `Ecdlp.lean`, held on the branch per the "no merges until the wall
cracks or a final barrier" directive.
-/
import Mathlib
import Ecdlp.Proved.NormEDSIsElliptic

namespace Ecdlp.Curve

open Polynomial

variable {R : Type*} [CommRing R] (W : WeierstrassCurve R)

/-- **`ψ` is an elliptic (net) sequence** — the three-term addition relation
`ψ(m+n)·ψ(m-n)·ψ(r)² = ψ(m+r)·ψ(m-r)·ψ(n)² − ψ(n+r)·ψ(n-r)·ψ(m)²`, holding because
`W.ψ = normEDS ψ₂ (C Ψ₃) (C preΨ₄)` definitionally. -/
theorem ψ_isEllSequence (m n r : ℤ) :
    W.ψ (m + n) * W.ψ (m - n) * W.ψ r ^ 2
      = W.ψ (m + r) * W.ψ (m - r) * W.ψ n ^ 2 - W.ψ (n + r) * W.ψ (n - r) * W.ψ m ^ 2 :=
  normEDS_isEllSequence W.ψ₂ (C W.Ψ₃) (C W.preΨ₄) m n r

/-- **Neighbour-product identity** `ψ(n+1)·ψ(n-1) = X·ψₙ² − φₙ` (Mathlib's `φ` definition,
rearranged). -/
theorem ψ_succ_mul_ψ_pred (n : ℤ) :
    W.ψ (n + 1) * W.ψ (n - 1) = C X * W.ψ n ^ 2 - W.φ n := by
  have hφ : W.φ n = C X * W.ψ n ^ 2 - W.ψ (n + 1) * W.ψ (n - 1) := rfl
  rw [hφ]; ring

/-- **The x-coordinate difference identity** (Silverman, AEC III Ex. 3.7):
`φₙ·ψₘ² − φₘ·ψₙ² = ψ(m+n)·ψ(m-n)` — the `r=1` specialisation of the net relation, the ω-free
core of the multiplication-by-`n` x-coordinate formula (`x(nP) − x(mP) = −ψ(m+n)ψ(m-n)/(ψₙ²ψₘ²)`). -/
theorem φ_ψ_diff (m n : ℤ) :
    W.φ n * W.ψ m ^ 2 - W.φ m * W.ψ n ^ 2 = W.ψ (m + n) * W.ψ (m - n) := by
  have h := ψ_isEllSequence W m n 1
  rw [W.ψ_one, one_pow, mul_one] at h
  have hφm : W.φ m = C X * W.ψ m ^ 2 - W.ψ (m + 1) * W.ψ (m - 1) := rfl
  have hφn : W.φ n = C X * W.ψ n ^ 2 - W.ψ (n + 1) * W.ψ (n - 1) := rfl
  rw [hφm, hφn]; linear_combination -h

end Ecdlp.Curve
