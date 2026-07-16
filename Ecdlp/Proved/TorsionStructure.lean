import Mathlib

/-!
# N10(iii) — the kernel-structure group lemma: order `n²` + killed by prime `n` ⇒ `(ℤ/n)²`

Node **N10** of the `ψₙ ↔ E[n]` bridge decomposition (`notes/DIVISION_POLY_TORSION_MAP.md`)
has three inputs: (i) the degree of `[n]` from `φₙ/ψₙ²` in lowest terms, (ii) separability
of `[n]` (the one CORE-hard item), and (iii) a **kernel-structure group lemma** turning the
count `#E[n] = n²` into the structure `E[n] ≅ (ℤ/n)²`. This file closes input **(iii)** for
prime `n` — exactly the case of secp256k1's group order.

The mathematical content: a finite abelian group killed by a prime `n` is an `𝔽_n`-vector
space (`AddCommGroup.zmodModule`, the same bridge the protocol algebra uses); if its order
is `n²` then `n² = n^dim` forces `dim = 2`, and a 2-dimensional `𝔽_n`-space is linearly —
in particular additively — equivalent to `ZMod n × ZMod n`. No curve appears: the lemma is
pure group theory, usable for *any* elliptic curve's `E[n]` (indeed any Galois module) the
moment the counting half `#E[n] = n²` lands. What remains open for the full N10 is exactly
inputs (i)+(ii): the degree/separability chain — see `notes/SEPARABILITY_ROUTES.md`.

Structural note: the whole argument lives in `of_module`, where the `𝔽_n`-module structure
is an honest instance parameter; the public statement then *constructs* that structure from
the kill hypothesis and applies `of_module` fully explicitly (elaborating instance searches
against a `letI`-local module instance leaves the elaborator stuck on metavariables).

Upstream note: Mathlib has no torsion-structure theorem for elliptic curves; this lemma is
deliberately stated over a bare `AddCommGroup`, making it a candidate for upstreaming
alongside the eventual counting half.
-/

namespace Ecdlp.Torsion

/-- The classification core, with the `𝔽_n`-module structure as an instance parameter:
an `𝔽_n`-module (`n` prime) of order `n²` has `n² = n^dim`, hence `dim = 2`, hence it is
additively `ZMod n × ZMod n`. -/
theorem nonempty_addEquiv_zmod_prod_of_card_eq_sq_of_module
    {n : ℕ} [hp : Fact n.Prime] (A : Type*) [AddCommGroup A] [Module (ZMod n) A]
    (hcard : Nat.card A = n ^ 2) :
    Nonempty (A ≃+ ZMod n × ZMod n) := by
  have hn2 : 2 ≤ n := hp.out.two_le
  haveI : NeZero n := ⟨hp.out.pos.ne'⟩
  -- `A` is finite and nonempty: its `Nat.card` is the positive number `n²`.
  have hpos : 0 < Nat.card A := hcard ▸ pow_pos hp.out.pos 2
  haveI hfin : Finite A := (Nat.card_pos_iff.mp hpos).2
  haveI : Module.Finite (ZMod n) A := Module.Finite.of_finite
  -- Count the space: `n ^ 2 = n ^ finrank`, so `finrank = 2`.
  have hfr : Module.finrank (ZMod n) A = 2 := by
    haveI : Fintype A := Fintype.ofFinite A
    have hcards : Fintype.card A = Fintype.card (ZMod n) ^ Module.finrank (ZMod n) A :=
      Module.card_eq_pow_finrank
    rw [← Nat.card_eq_fintype_card, hcard, ZMod.card] at hcards
    exact (Nat.pow_right_injective hn2 hcards).symm
  -- Dimension 2 classifies: `A ≃ₗ[𝔽_n] 𝔽_n × 𝔽_n`, hence `≃+`.
  have hfr' : Module.finrank (ZMod n) (ZMod n × ZMod n) = 2 := by
    simp [Module.finrank_prod]
  exact ⟨(LinearEquiv.ofFinrankEq A (ZMod n × ZMod n) (hfr.trans hfr'.symm)).toAddEquiv⟩

/-- **A finite abelian group of order `n²` killed by a prime `n` is `(ℤ/n)²`** — the
kernel-structure input (iii) of node N10: once the counting half `#E[n] = n²` is proved,
this upgrades the *count* to the *structure* `E[n] ≅ (ℤ/n)²`. Killed-by-`n` makes the
group an `𝔽_n`-vector space; `n² = n^dim` pins `dim = 2`; dimension classifies. -/
theorem nonempty_addEquiv_zmod_prod_of_card_eq_sq
    {A : Type*} [acg : AddCommGroup A] {n : ℕ} [hp : Fact n.Prime]
    (hkill : ∀ a : A, n • a = 0) (hcard : Nat.card A = n ^ 2) :
    Nonempty (A ≃+ ZMod n × ZMod n) :=
  -- Killed by `n` ⇒ `𝔽_n`-vector-space structure; apply the core fully explicitly so no
  -- instance search runs against the locally-constructed module instance.
  @nonempty_addEquiv_zmod_prod_of_card_eq_sq_of_module n hp A acg
    (AddCommGroup.zmodModule hkill) hcard

end Ecdlp.Torsion
