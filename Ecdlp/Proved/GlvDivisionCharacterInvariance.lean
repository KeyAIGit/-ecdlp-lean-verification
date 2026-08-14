import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# UORC-056 GLV division-character invariance boundary

The mathematical V13 note proves that every classical division-polynomial
quadratic-character atom is invariant under the secp256k1 order-three GLV
automorphism.  This file kernel-checks the generic closure step and the fixed
public arithmetic mismatch: products, inverses and powers of invariant atoms
remain invariant, whereas canonical scalar parity differs between `G` and
`[lambda]G` because the public lambda representative is even.

The division-polynomial CM-weight induction itself is source-level mathematics
plus an executable exact replay; elliptic curves and quadratic characters are
not re-formalized here.
-/

namespace Ecdlp.GlvDivisionCharacter

variable {A B : Type*}

def Invariant (phi : A → A) (f : A → B) : Prop :=
  ∀ x, f (phi x) = f x

section Mul

variable [CommGroup B]

 theorem invariant_one (phi : A → A) :
    Invariant phi (fun _ : A => (1 : B)) := by
  intro x
  rfl

 theorem invariant_mul
    (phi : A → A) (f g : A → B)
    (hf : Invariant phi f) (hg : Invariant phi g) :
    Invariant phi (fun x => f x * g x) := by
  intro x
  rw [hf x, hg x]

 theorem invariant_inv
    (phi : A → A) (f : A → B)
    (hf : Invariant phi f) :
    Invariant phi (fun x => (f x)⁻¹) := by
  intro x
  rw [hf x]

 theorem invariant_zpow
    (phi : A → A) (f : A → B) (e : ℤ)
    (hf : Invariant phi f) :
    Invariant phi (fun x => (f x) ^ e) := by
  intro x
  rw [hf x]

end Mul

/-- An invariant candidate cannot equal a target that changes at one explicit
point of the automorphism orbit. -/
theorem invariant_cannot_equal_nonInvariantTarget
    [DecidableEq B]
    (phi : A → A) (candidate target : A → B)
    (hcandidate : Invariant phi candidate)
    (x : A)
    (htarget : target (phi x) ≠ target x) :
    ¬ (∀ q, candidate q = target q) := by
  intro hall
  apply htarget
  calc
    target (phi x) = candidate (phi x) := (hall (phi x)).symm
    _ = candidate x := hcandidate x
    _ = target x := hall x

/-- Public secp256k1 GLV eigenvalue is even in its canonical representative. -/
theorem secp_lambda_even : Secp256k1.lam % 2 = 0 := by
  native_decide

/-- The canonical scalar representatives `1` and `lambda` therefore have
opposite parity bits. -/
theorem secp_one_lambda_parity_mismatch :
    (1 % 2 : Nat) ≠ Secp256k1.lam % 2 := by
  native_decide

/-- The public field cube root `beta` is itself a square: `beta^2` is an
explicit square root because `beta^3=1`.  The literal modular identity is kept
as a small fixed arithmetic certificate. -/
theorem secp_beta_is_square_witness :
    ((Secp256k1.beta ^ 2) ^ 2) % Secp256k1.p = Secp256k1.beta := by
  native_decide

/-- The public lambda is a nonzero canonical subgroup scalar. -/
theorem secp_lambda_nonzero_lt_order :
    0 < Secp256k1.lam ∧ Secp256k1.lam < Secp256k1.n := by
  constructor
  · native_decide
  · exact Secp256k1.lam_lt_n

end Ecdlp.GlvDivisionCharacter
