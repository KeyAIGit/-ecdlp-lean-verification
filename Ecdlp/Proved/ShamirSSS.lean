import Mathlib

/-!
# Shamir's Secret Sharing — Lagrange reconstruction correctness

Shamir's `(t, n)` threshold secret-sharing scheme distributes a secret `S ∈ F`
(a field, in practice `𝔽_p`) among `n` participants as follows.

* The dealer picks a polynomial `f ∈ F[X]` of degree `< t` whose constant term is
  the secret: `f.eval 0 = S`.
* Participant `i` — with a public, pairwise-distinct evaluation node `vᵢ ∈ F` —
  receives the **share** `f.eval vᵢ`. So a share is the pair `(vᵢ, f.eval vᵢ)`.

**Reconstruction (this file).** Any `t` participants whose nodes `vᵢ` are pairwise
distinct recover `f`, and therefore the secret `S = f.eval 0`, by Lagrange
interpolation through their `t` points. Concretely, if `s : Finset ι` indexes the
`t = s.card` cooperating participants and `v` is injective on `s` (distinct nodes),
then a degree-`< t` polynomial equals the Lagrange interpolant of its own
evaluations on `s`:

  `f = Lagrange.interpolate s v (fun i => f.eval (v i))`      (`shamir_reconstruct_poly`)

Evaluating both sides at `0` yields secret recovery:

  `f.eval 0 = (Lagrange.interpolate s v (fun i => f.eval (v i))).eval 0`  (`shamir_reconstruct`)

The entire content here is the **information-theoretic recovery direction**: `t`
shares with distinct nodes uniquely determine the degree-`< t` polynomial `f`
(`t` values pin down a degree-`< t` polynomial — Mathlib's `Lagrange.eq_interpolate`)
and hence the secret `f.eval 0`.

The complementary **security** direction — that any `t − 1` shares leave the secret
`f.eval 0` uniformly distributed and thus reveal *nothing* — is a statement about a
probability model over the dealer's random coefficients and is deliberately
**out of scope** here: there is no adversary, no distribution, and no probability
space, consistent with `ABSTRACT_SCOPE.md`. This file records only the algebraic
Lagrange-interpolation identity that makes reconstruction work.

Core Mathlib API used: `Lagrange.interpolate`, `Lagrange.eq_interpolate`.
-/

namespace Ecdlp.Schnorr

open Polynomial

/-- **Shamir reconstruction, polynomial form.** A polynomial `f` of degree `< t`
(`= s.card`) equals the Lagrange interpolant of its own evaluations `f.eval (v i)`
at the distinct nodes `v i`, `i ∈ s`. This is the recovery identity underlying
Shamir's `(t, n)` secret sharing: the `t` shares `(vᵢ, f.eval vᵢ)` determine `f`
uniquely. It is exactly `Lagrange.eq_interpolate`. -/
theorem shamir_reconstruct_poly {F : Type*} [Field F] {ι : Type*} [DecidableEq ι]
    (s : Finset ι) (v : ι → F) (hv : Set.InjOn v s) (f : F[X])
    (hdeg : f.degree < s.card) :
    f = Lagrange.interpolate s v (fun i => f.eval (v i)) :=
  Lagrange.eq_interpolate hv hdeg

/-- **Shamir secret recovery.** The Shamir secret is the constant term `f.eval 0` of
the sharing polynomial `f`. Given `t = s.card` shares `(vᵢ, f.eval vᵢ)` with
pairwise-distinct nodes (`Set.InjOn v s`) and `f.degree < t`, interpolating the
shares and evaluating at `0` returns the secret. This is the `eval 0`-corollary of
`shamir_reconstruct_poly`, obtained by evaluating the polynomial identity at `0`. -/
theorem shamir_reconstruct {F : Type*} [Field F] {ι : Type*} [DecidableEq ι]
    (s : Finset ι) (v : ι → F) (hv : Set.InjOn v s) (f : F[X])
    (hdeg : f.degree < s.card) :
    f.eval 0 = (Lagrange.interpolate s v (fun i => f.eval (v i))).eval 0 :=
  congrArg (Polynomial.eval 0) (shamir_reconstruct_poly s v hv f hdeg)

end Ecdlp.Schnorr
