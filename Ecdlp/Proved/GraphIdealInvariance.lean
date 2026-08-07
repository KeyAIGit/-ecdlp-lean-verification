/-
# Graph-ideal invariance: adjoining `t = g` changes only the presentation

A recurring re-encoding move in algebraic attacks on ECDLP is to *adjoin an auxiliary
variable together with its defining equation*: replace a system `I ⊆ k[x]` by the system
`I + ⟨t₁ − g₁(x), …, t_m − g_m(x)⟩ ⊆ k[x, t]`, where each `g_j` is a polynomial in the
variables already present. Straight-line/circuit encodings, the `U = X³` Semaev
re-encoding of `experiments/p3_sm_system/`, and the auxiliary-variable splittings of
`experiments/p4_petit/` are all instances of this move.

This module proves, over an arbitrary `CommRing k` and arbitrary (possibly infinite)
index types `σ` (original variables) and `τ` (auxiliary variables), that the move only
changes the **presentation**: the extended ideal is exactly the contraction of `I` along
a retraction, and contracting it back to `k[x]` returns `I` on the nose.

## Mechanism

Adjoining the graph produces a retraction pair of `k`-algebras

    ι = rename Sum.inl              : k[x] →ₐ k[x, t]
    π = aeval (Sum.elim X G)        : k[x, t] →ₐ k[x]

with `π ∘ ι = id` (`aeval_sumElim_comp_rename_inl`). Everything else is formal. For *any*
retraction pair of algebras:

* `comap_eq_map_sup_ker` : `comap π I = map ι I ⊔ ker π`;
* `comap_comap_eq_self`  : `comap ι (comap π I) = I`.

For the graph retraction the kernel is exactly the ideal of defining equations,
`ker π = ⟨t_j − g_j(x)⟩` (`ker_aeval_sumElim`, via `sub_rename_aeval_mem`: modulo the
defining equations every polynomial equals the pullback of its own image). Combining:

* `comap_aeval_sumElim` : `map ι I ⊔ ⟨t_j − g_j⟩ = comap π I` — the re-encoded system
  *is* the contraction, so no information was added;
* `elimination_eq_self` : `comap ι (map ι I ⊔ ⟨t_j − g_j⟩) = I` — the elimination ideal
  of the re-encoded system, read back in the original variables, is bit-for-bit the
  ideal one started with. No relation among the original variables is created or
  destroyed by the re-encoding.

`aeval_comp_aeval_sumElim` records the point-level counterpart: evaluating at any point
`u` of the original variables, extended by `t_j ↦ g_j(u)`, is the same as substituting
first and evaluating afterwards.

Mathlib v4.31.0 states nothing of this kind for `MvPolynomial`; the closest existing
item is `Polynomial.quotientSpanXSubCAlgEquiv`
(`Mathlib/RingTheory/Polynomial/Quotient.lean`), the univariate case with constant `g`.

**Honest scope — what this does NOT say.** These are statements about *ideals and their
contractions*, i.e. about the variety and about which relations are derivable. They say
**nothing whatever** about the cost of computing with either presentation: not about
Gröbner/F4 running time, not about solving degree or degree of regularity, not about
Macaulay matrix size, not about the leading-term ideal or the standard-monomial
staircase. Every one of those depends on the presentation *and* on the monomial order,
and every one of them is observed in this repository to move by orders of magnitude
under exactly the re-encodings covered here (both directions: a degree proxy can fall
while wall-clock rises by three orders of magnitude). Citing this module to argue
"therefore a compact circuit encoding cannot help" is an overclaim. Its correct use is
narrow and negative: it falsifies **one** class of explanation for a re-encoding —
"the re-encoding shrank the variety, lowered the solution count, or manufactured a new
algebraic consequence" — and nothing beyond that.

Two further limits. (i) Only *graph* adjunctions `t = g(x)` are covered; proposals that
project, restrict, or adjoin field equations are not retractions and genuinely can
change the variety, so applying this module to them is a category error. (ii) The `G`
here are polynomials in the original variables only — a *flat* adjunction. A chained
straight-line program `t₂ = g₂(x, t₁)` reduces to this form only after a triangular
change of generators, which is not carried out here.
-/
import Mathlib

namespace Ecdlp.GraphIdeal

open MvPolynomial

/-! ### Abstract retraction pairs -/

section Retraction

variable {R A B : Type*} [CommSemiring R] [CommRing A] [CommRing B] [Algebra R A] [Algebra R B]

/-- **Retraction decomposition.** If `π ∘ ι = id`, then the contraction of any ideal `I`
along `π` splits as the extension of `I` along `ι` joined with the kernel of `π`.

Nothing is assumed about `A`, `B` beyond being commutative `R`-algebras; surjectivity of
`π` is *not* an extra hypothesis, it follows from `π ∘ ι = id`. -/
theorem comap_eq_map_sup_ker (iota : A →ₐ[R] B) (pi : B →ₐ[R] A)
    (hretract : pi.comp iota = AlgHom.id R A) (I : Ideal A) :
    Ideal.comap pi I = Ideal.map iota I ⊔ RingHom.ker pi := by
  have hpi : ∀ a : A, pi (iota a) = a := by
    intro a
    rw [← AlgHom.comp_apply, hretract, AlgHom.id_apply]
  have hsurj : Function.Surjective pi := fun a => ⟨iota a, hpi a⟩
  have hmap : Ideal.map pi (Ideal.map iota I) = I := by
    rw [Ideal.map_mapₐ, hretract, Ideal.map_idₐ]
  calc Ideal.comap pi I
      = Ideal.comap pi (Ideal.map pi (Ideal.map iota I)) := by rw [hmap]
    _ = Ideal.map iota I ⊔ RingHom.ker pi :=
        Ideal.comap_map_of_surjective' pi hsurj (Ideal.map iota I)

/-- **Contraction is undone by the retraction.** Pulling an ideal `I` of `A` back to `B`
along `π` and then back again along `ι` recovers `I` exactly. For the graph adjunction
below this is the elimination statement: eliminating the adjoined variables returns the
original ideal, not merely something containing or contained in it. -/
theorem comap_comap_eq_self (iota : A →ₐ[R] B) (pi : B →ₐ[R] A)
    (hretract : pi.comp iota = AlgHom.id R A) (I : Ideal A) :
    Ideal.comap iota (Ideal.comap pi I) = I := by
  rw [Ideal.comap_comapₐ, hretract, Ideal.comap_idₐ]

end Retraction

/-! ### The graph adjunction `t_j = G j` -/

section GraphAdjunction

variable {k σ τ : Type*} [CommRing k] (G : τ → MvPolynomial σ k)

/-- The graph adjunction is a retraction: substituting `t_j ↦ G j` after renaming the
original variables into `σ ⊕ τ` is the identity on `k[x]`. -/
theorem aeval_sumElim_comp_rename_inl :
    (aeval (R := k) (Sum.elim X G)).comp (rename (R := k) (Sum.inl : σ → σ ⊕ τ))
      = AlgHom.id k (MvPolynomial σ k) :=
  MvPolynomial.algHom_ext fun i => by
    simp only [AlgHom.comp_apply, rename_X, aeval_X, Sum.elim_inl, AlgHom.id_apply]

/-- Pointwise form of `aeval_sumElim_comp_rename_inl`. -/
theorem aeval_sumElim_rename_inl (p : MvPolynomial σ k) :
    aeval (R := k) (Sum.elim X G) (rename (R := k) (Sum.inl : σ → σ ⊕ τ) p) = p := by
  have h := AlgHom.congr_fun (aeval_sumElim_comp_rename_inl G) p
  simpa using h

/-- **Modulo the defining equations, every polynomial is the pullback of its own image.**
For any ideal `J` of `k[x, t]` containing all the defining equations `t_j − G j`, and any
`f : k[x, t]`, the difference `f − ι(π f)` lies in `J`.

This is the one step that is not pure formal nonsense, and it needs no induction on `f`:
the two algebra maps `mk ∘ ι ∘ π` and `mk` into `k[x, t] ⧸ J` agree on every variable, so
`MvPolynomial.algHom_ext` makes them equal. -/
theorem sub_rename_aeval_mem (J : Ideal (MvPolynomial (σ ⊕ τ) k))
    (hJ : ∀ j : τ,
      (X (Sum.inr j) : MvPolynomial (σ ⊕ τ) k)
        - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (G j) ∈ J)
    (f : MvPolynomial (σ ⊕ τ) k) :
    f - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (aeval (R := k) (Sum.elim X G) f) ∈ J := by
  have hcomp :
      (Ideal.Quotient.mkₐ k J).comp
          ((rename (R := k) (Sum.inl : σ → σ ⊕ τ)).comp (aeval (R := k) (Sum.elim X G)))
        = Ideal.Quotient.mkₐ k J := by
    apply MvPolynomial.algHom_ext
    rintro (i | j)
    · simp only [AlgHom.comp_apply, aeval_X, Sum.elim_inl, rename_X]
    · simp only [AlgHom.comp_apply, aeval_X, Sum.elim_inr, Ideal.Quotient.mkₐ_eq_mk]
      exact ((Ideal.Quotient.mk_eq_mk_iff_sub_mem _ _).mpr (hJ j)).symm
  have hf := AlgHom.congr_fun hcomp f
  simp only [AlgHom.comp_apply, Ideal.Quotient.mkₐ_eq_mk] at hf
  exact (Ideal.Quotient.mk_eq_mk_iff_sub_mem _ _).mp hf.symm

/-- **The kernel of the graph substitution is exactly the ideal of defining equations.**
This is what connects the abstract retraction to the concrete re-encoding: the "extra"
part of the extended system is neither more nor less than `⟨t_j − G j⟩`. -/
theorem ker_aeval_sumElim :
    RingHom.ker (aeval (R := k) (Sum.elim X G))
      = Ideal.span (Set.range fun j : τ =>
          (X (Sum.inr j) : MvPolynomial (σ ⊕ τ) k)
            - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (G j)) := by
  refine le_antisymm ?_ (Ideal.span_le.mpr ?_)
  · intro f hf
    rw [RingHom.mem_ker] at hf
    have h₀ := sub_rename_aeval_mem G
      (Ideal.span (Set.range fun j : τ =>
        (X (Sum.inr j) : MvPolynomial (σ ⊕ τ) k)
          - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (G j)))
      (fun j => Ideal.subset_span (Set.mem_range_self j)) f
    rwa [hf, map_zero, sub_zero] at h₀
  · rintro _ ⟨j, rfl⟩
    simp only [SetLike.mem_coe, RingHom.mem_ker, map_sub, aeval_X, Sum.elim_inr,
      aeval_sumElim_rename_inl, sub_self]

/-- **The re-encoded system is a contraction.** The ideal generated by (the renamed) `I`
together with the defining equations `t_j = G j` is exactly the preimage of `I` under the
graph substitution. Nothing was added: membership in the extended ideal is decided
entirely by what the substitution does. -/
theorem comap_aeval_sumElim (I : Ideal (MvPolynomial σ k)) :
    Ideal.comap (aeval (R := k) (Sum.elim X G)) I
      = Ideal.map (rename (R := k) (Sum.inl : σ → σ ⊕ τ)) I
        ⊔ Ideal.span (Set.range fun j : τ =>
            (X (Sum.inr j) : MvPolynomial (σ ⊕ τ) k)
              - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (G j)) := by
  rw [← ker_aeval_sumElim G]
  exact comap_eq_map_sup_ker _ _ (aeval_sumElim_comp_rename_inl G) I

/-- **Graph-ideal invariance.** Eliminating the adjoined variables from the re-encoded
system returns the original ideal exactly. Read contrapositively: a polynomial relation
among the original variables holds in the re-encoded system if and only if it already
held in `I`. See the module docstring for what this does *not* say about solving cost. -/
theorem elimination_eq_self (I : Ideal (MvPolynomial σ k)) :
    Ideal.comap (rename (R := k) (Sum.inl : σ → σ ⊕ τ))
        (Ideal.map (rename (R := k) (Sum.inl : σ → σ ⊕ τ)) I
          ⊔ Ideal.span (Set.range fun j : τ =>
              (X (Sum.inr j) : MvPolynomial (σ ⊕ τ) k)
                - rename (R := k) (Sum.inl : σ → σ ⊕ τ) (G j))) = I := by
  rw [← comap_aeval_sumElim G I]
  exact comap_comap_eq_self _ _ (aeval_sumElim_comp_rename_inl G) I

/-- **Point-level counterpart.** Over any commutative `k`-algebra `L`, evaluating at the
extended point `Sum.elim u (fun j => aeval u (G j))` is the same as first substituting
`t_j ↦ G j` and then evaluating at `u`. The auxiliary coordinates of a solution are
determined by the original ones; adjoining them cannot split or merge solutions. -/
theorem aeval_comp_aeval_sumElim {L : Type*} [CommSemiring L] [Algebra k L] (u : σ → L) :
    (aeval (R := k) u).comp (aeval (R := k) (Sum.elim X G))
      = aeval (R := k) (Sum.elim u fun j => aeval (R := k) u (G j)) := by
  apply MvPolynomial.algHom_ext
  rintro (i | j) <;>
    simp only [AlgHom.comp_apply, aeval_X, Sum.elim_inl, Sum.elim_inr]

end GraphAdjunction

end Ecdlp.GraphIdeal
