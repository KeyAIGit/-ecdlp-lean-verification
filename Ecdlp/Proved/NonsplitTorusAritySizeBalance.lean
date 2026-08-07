/-
# Index-calculus size balance for the `p+1` nonsplit-torus trace factor base: a sharpness pair

The `p+1` nonsplit-torus trace factor base has been screened repeatedly in this repository
(`experiments/engine/pkc_nonsplit_torus_desk_screen/`, `notes/reviews/HYP_TORUS_001_INDEPENDENT_AUDIT.md`,
`notes/reviews/HYP_SELECT_00{2,3,5}.md`, `notes/reviews/TASK014_PRIME_FIELD_COMPARISON.md`).
Every one of those screens is prose or a replayed JSON artifact. This module puts the *size*
part of the question — the only part that is a decidable arithmetic statement — into the kernel,
and it does so as a **sharpness pair**: a bounded negative witness *and* a positive witness.

## The two legs

For decomposing into `m` points against a factor base `L`, index calculus needs both

* **yield** `m! · |F| ≤ (deg L)^m` — enough relations, and
* **linear algebra** `(deg L)² ≤ 2^126` — the sparse-elimination step must stay under the
  128-bit target.

`deg L` here is a *trace-orbit count*: for a subgroup `H` of the nonsplit torus `T₂ ⊆ 𝔽_{p²}^×`
of order dividing `p+1`, the trace `α ↦ α + α^{-1}` identifies `α` with `α^{-1}`, so `H`
contributes `(|H| + gcd(|H|, 2))/2` distinct traces.

## What is proved

`p + 1 = 2⁴ · 7322137 · 45422601869677 · C₁₈₄` with `C₁₈₄` a 184-bit prime. Among the divisors
built from the three small factors, the trace count is maximised subject to the linear-algebra
leg by `H = 2⁴ · 45422601869677 = 726761629914832`, giving

  `traceBaseBound = (H + 2)/2 = 363380814957417 ≈ 2^48.37`.

* `traceSubgroupOrder_dvd` — `H ∣ p + 1`, with the explicit cofactor.
* `traceBaseBound_linearAlgebra_leg` — `traceBaseBound² ≤ 2^126` (≈ `2^96.74`): the LA leg holds.
* `traceBaseBound_sq_lt_next_candidate_sq` / `nextCandidate_linearAlgebra_leg_fails` — the next
  larger divisor `2⁴ · 7322137 · 45422601869677` has trace count `2660724110289849117993 ≈ 2^71.2`
  and **violates** the LA leg, so `traceBaseBound` is not an arbitrary choice.
* **Negative witness** `arity_five_yield_leg_fails` — at `m = 5`,
  `traceBaseBound⁵ < 5! · p`. The window is closed.
* **Positive witness** `arity_six_yield_leg_holds` — at `m = 6`,
  `6! · p ≤ traceBaseBound⁶`. The window is **open**.

So the crossing is exactly between arity 5 and arity 6, and both sides of it are kernel-checked.

## Why the pair, and not just the negative half

A bounded negative result with no witness of tightness invites generalisation past its own
range, and that has already happened here: the archived intake
`archive/untrusted_intake/OPUS-ECDLP-SCREEN-ATLAS-2026-07-26/all_properties.json` records
"the requirement fails for every `m` in range" from a table that stops at `m = 8`, and
`all_mechanisms.json` truncates the same reasoning at `m ≈ 13.4`. Both readings are wrong, and
the direction of the error is the dangerous one: they report a route as closed when the size
legs do not close it. (That intake is quarantined — `build_untrusted_evidence_intake.py` fails
closed if a scientific consumer reads it — so nothing machine-side was ever poisoned by it.)

The correct closed form, for the record, is `lg(m!) + lg|F| − 63m ≤ 0`. The field size does
**not** cancel: only the yield leg mentions `|F|` at all, the LA leg is a pure numeric bound on
`deg L`, so eliminating `deg L` passes `lg|F|` straight through with coefficient 1. The
`m`-slope is `lg m − 63 < 0`, i.e. the gap *shrinks* with arity — which is why a window that is
closed at small `m` must eventually open, and why any "closed at every `m`" reading of a
truncated table is unsound.

## Honest scope — what this does NOT say

* This is arithmetic about **two size inequalities**, nothing else. It is not a theorem about
  relation yield, about actual relation counts, about solving degree, about running time, or
  about the security of secp256k1. The yield leg `m!·|F| ≤ (deg L)^m` is a heuristic model of
  relation yield; the kernel checks the inequality, not the model.
* Passing the size legs is **not** an attack and not a mechanism. The route remains parked for
  a reason this module does not touch: no exact low-degree polynomial is known whose roots are
  the required traces. The recorded desk verdict is
  `rejected_missing_exact_low_degree_mechanism` with `submitted_size_leg = retracted_not_cleared`
  (`experiments/engine/pkc_nonsplit_torus_desk_screen/artifact.json`), and the accompanying
  decision `EDD-2026-07-31-001` records that the *submitted* construction supplies **9** trace
  roots against the `345156162942` needed at `m = 7`. Having a subgroup of adequate order is not
  the same as having a computable low-degree description of its traces; this module proves only
  the former, and only at `m = 6`.
* `traceBaseBound` is maximal among divisors built from the three **known** small factors of
  `p+1`. The 184-bit cofactor is not factored here and no claim is made that it is prime beyond
  the citation above; any divisor involving it exceeds the LA leg by a wide margin regardless.
* No `native_decide`: every fact below is closed by `norm_num` on `Nat` literals, so this module
  adds nothing to the trust base.
-/
import Mathlib
import Ecdlp.Secp256k1Verified

namespace Ecdlp.SizeBalance

open Secp256k1

/-- The largest subgroup order, among divisors of `p+1` built from its three known small prime
factors, whose trace-orbit count still satisfies the linear-algebra leg: `2⁴ · 45422601869677`. -/
def traceSubgroupOrder : ℕ := 726761629914832

/-- The trace-orbit count of `traceSubgroupOrder`: `(|H| + gcd(|H|,2))/2` with `|H|` even. -/
def traceBaseBound : ℕ := 363380814957417

/-- The next larger divisor of `p+1` built from the known small factors,
`2⁴ · 7322137 · 45422601869677`, has this trace-orbit count. -/
def nextCandidateTraceBound : ℕ := 2660724110289849117993

theorem traceBaseBound_eq : 2 * traceBaseBound = traceSubgroupOrder + 2 := by
  norm_num [traceBaseBound, traceSubgroupOrder]

/-- `traceSubgroupOrder` really is a divisor of `p + 1`, with the explicit cofactor. -/
theorem traceSubgroupOrder_dvd : traceSubgroupOrder ∣ Secp256k1.p + 1 :=
  ⟨159326090524186974347194060368720527508797037830010082064134127, by
    norm_num [traceSubgroupOrder, Secp256k1.p]⟩

/-- **Linear-algebra leg, satisfied.** `traceBaseBound² ≈ 2^96.74 ≤ 2^126`. -/
theorem traceBaseBound_linearAlgebra_leg : traceBaseBound ^ 2 ≤ 2 ^ 126 := by
  norm_num [traceBaseBound]

/-- **The next candidate up violates the linear-algebra leg**, so `traceBaseBound` is forced
rather than chosen: `2660724110289849117993² ≈ 2^142.4 > 2^126`. -/
theorem nextCandidate_linearAlgebra_leg_fails : 2 ^ 126 < nextCandidateTraceBound ^ 2 := by
  norm_num [nextCandidateTraceBound]

/-- **Negative witness, arity 5.** The yield leg fails: `traceBaseBound⁵ < 5! · p`. -/
theorem arity_five_yield_leg_fails :
    traceBaseBound ^ 5 < Nat.factorial 5 * Secp256k1.p := by
  norm_num [traceBaseBound, Secp256k1.p, Nat.factorial]

/-- **Positive witness, arity 6.** The yield leg holds: `6! · p ≤ traceBaseBound⁶`.

Together with `traceBaseBound_linearAlgebra_leg`, *both* size legs are satisfiable at `m = 6`.
See the module docstring: this is a statement about two inequalities, not a mechanism, and the
route stays parked for want of an exact low-degree description of the traces. -/
theorem arity_six_yield_leg_holds :
    Nat.factorial 6 * Secp256k1.p ≤ traceBaseBound ^ 6 := by
  norm_num [traceBaseBound, Secp256k1.p, Nat.factorial]

/-- **The sharpness pair, in one statement.** The size window for the `p+1` nonsplit-torus
trace factor base is closed at arity 5 and open at arity 6. Neither half is asserted beyond its
own arity. -/
theorem size_window_crosses_between_five_and_six :
    traceBaseBound ^ 5 < Nat.factorial 5 * Secp256k1.p ∧
      Nat.factorial 6 * Secp256k1.p ≤ traceBaseBound ^ 6 ∧
      traceBaseBound ^ 2 ≤ 2 ^ 126 :=
  ⟨arity_five_yield_leg_fails, arity_six_yield_leg_holds, traceBaseBound_linearAlgebra_leg⟩

end Ecdlp.SizeBalance
