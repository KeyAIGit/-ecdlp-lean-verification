/-
# Prime-field rigidity: `ZMod n` has no proper `Subring`, `F_p` no proper subfield, `G_a` no proper subgroup

A **screening** module for the `R-WEIL-DESCENT` route. It records, as kernel-checked
statements, the three structural rigidity facts that a GHS / Weil-restriction proposal
over a prime base field would have to contradict:

* `zmod_no_proper_subring`: for **every** `n : ℕ`, the only `Subring (ZMod n)` is `⊤`
  (packaged as `Subsingleton (Subring (ZMod n))`). No primality is needed and `n = 0`
  (`ZMod 0 = ℤ`) is included — a `Subring` contains `1`, hence every `Int.cast`, and
  `ZMod.intCast_surjective` exhausts the ring.
* `zmod_prime_no_proper_subfield`: for prime `p`, the only `Subfield (ZMod p)` is `⊤`,
  so there is no proper subfield `F_q ⊊ F_p` to descend to and no intermediate tower.
* `zmod_prime_no_proper_addSubgroup`: for prime `p`, an `AddSubgroup (ZMod p)` is `⊥`
  or `⊤`, so the additive group `G_a` of the coordinate field supplies no proper
  factor base.

**Provenance, stated plainly.** Only the first is new. `Subsingleton (Subfield (ZMod p))`
is already a Mathlib instance (`Mathlib/FieldTheory/PrimeField.lean`,
`Mathlib/FieldTheory/Finite/Basic.lean`), so `zmod_prime_no_proper_subfield` is a named
restatement of `Subsingleton.elim`, not a new proof. The third is
`Ecdlp/Proved/ScalarGroupStructure.lean`'s `secp256k1_scalar_no_proper_subgroup` with the
modulus abstracted; Mathlib also carries `ZMod.instIsSimpleAddGroup`. Mathlib has no
`Subsingleton (Subring (ZMod n))` at the pinned revision — that lemma is the only
non-duplicative content here.

**Honest scope.** Nothing here is an attack, a cost claim, or a statement about
secp256k1 in particular; this is a target-applicability exclusion. Five limits are load
bearing.

1. *The descent conclusion is prose, not a theorem.* Weil restriction, abelian
   varieties and GHS do not exist in Mathlib; no declaration below mentions them. Lean
   proves the rigidity clauses only. The inference "degree 1, so the standard
   extension-field descent buys nothing" is read off by a human, and it excludes the
   **standard extension-field descent setup only**, not every algebraic-geometric
   reformulation over a prime field.
2. *This does not screen out Petit-style prime-field factor bases.* PKC 2016 builds a
   faithful factor base `{(x, y) : L(x) = 0}` over the prime field itself, with `L` a
   composition of low-degree rational maps arising either from a smooth divisor of
   `p - 1` or from a separate auxiliary curve whose self-isogeny defines the root map.
   The root set of a rational map is a fibre of a morphism: it is not a subring, not a
   subfield and not an additive subgroup, so none of the lemmas below touches it. Using
   "no Weil restriction over a prime field" against those constructions is exactly the
   inference `data/research_decisions.md` row 22 retracts, and this module must not be
   cited to revive it.
3. *This is `G_a` only, never `G_m`.* The multiplicative analogue of the third lemma is
   **false**: `(ZMod p)ˣ` is cyclic of order `p - 1`, which is composite for every
   `p > 3`, so proper nontrivial multiplicative subgroups exist. Nothing here constrains
   them.
4. *`Subring` means Mathlib's unital bundling.* `Subring` requires `1 ∈ S`. For composite
   `n` there are subsets of `ZMod n` closed under `+`, `-`, `*` that are rings with a
   *different* identity — `{0, 2, 4} ⊆ ZMod 6` is a field isomorphic to `F₃` with unit
   `4`. Those are not `Subring`s and `zmod_no_proper_subring` says nothing about them.
   The gap closes exactly when `ZMod n` is a field (only idempotents `0`, `1`), which is
   the case actually used here, but the general statement must never be exported as
   "`ZMod n` has no proper subring" without the bundling made explicit.
5. *Read the modulus.* `ZMod p` below is the additive group of the **coordinate field**.
   The discrete logarithm lives in `E(F_p)`, whose order `n` is a different prime; the
   coordinate field's additive group plays no role in the group law. The statements that
   bear on scalar and point structure are `Ecdlp/Proved/ScalarGroupStructure.lean` and
   `Ecdlp/Proved/PointGroupSimple.lean`, not this file.
-/
import Mathlib

namespace Ecdlp.Curve

/-- **`ZMod n` has no proper subring, for every `n : ℕ`.** A `Subring` contains `1` and is
closed under negation and addition, hence contains every integer cast; and every element of
`ZMod n` is such a cast (`ZMod.intCast_surjective`). No primality, finiteness or `NeZero`
hypothesis is used, so this covers `ZMod 0 = ℤ` and the trivial ring `ZMod 1` as well. -/
theorem zmod_no_proper_subring {n : ℕ} (A : Subring (ZMod n)) : A = ⊤ :=
  (Subring.eq_top_iff' A).mpr fun x => by
    obtain ⟨m, rfl⟩ := ZMod.intCast_surjective x
    exact intCast_mem A m

/-- The subring lattice of `ZMod n` is trivial (instance packaging of
`zmod_no_proper_subring`). Mathlib carries the `Subfield` analogue but not this one. -/
instance zmodSubringSubsingleton (n : ℕ) : Subsingleton (Subring (ZMod n)) :=
  ⟨fun A B => (zmod_no_proper_subring A).trans (zmod_no_proper_subring B).symm⟩

/-- **`F_p` has no proper subfield**: for prime `p` the only `Subfield (ZMod p)` is `⊤`.
Hence there is no `F_q ⊊ F_p` to restrict scalars to and no intermediate field tower — the
standard GHS/Weil-descent setting needs an extension degree `> 1` and here it is `1`.
This is a named restatement of Mathlib's `Subsingleton (Subfield (ZMod p))` instance. -/
theorem zmod_prime_no_proper_subfield {p : ℕ} [Fact p.Prime] (F : Subfield (ZMod p)) :
    F = ⊤ :=
  Subsingleton.elim F ⊤

/-- **The additive group of `F_p` has no proper nontrivial subgroup.** Since
`Nat.card (ZMod p) = p` is prime, every `AddSubgroup (ZMod p)` is `⊥` or `⊤`, so `G_a` on
the coordinate line offers no proper additive factor base to decompose over. Generic-`p`
form of `Ecdlp.Curve.secp256k1_scalar_no_proper_subgroup`. -/
theorem zmod_prime_no_proper_addSubgroup {p : ℕ} [hp : Fact p.Prime]
    (H : AddSubgroup (ZMod p)) : H = ⊥ ∨ H = ⊤ := by
  haveI : Fact (Nat.card (ZMod p)).Prime := ⟨by rw [Nat.card_zmod]; exact hp.out⟩
  exact H.eq_bot_or_eq_top_of_prime_card

end Ecdlp.Curve
