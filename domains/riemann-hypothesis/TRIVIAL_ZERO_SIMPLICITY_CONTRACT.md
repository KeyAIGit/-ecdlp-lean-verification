# Simplicity of the negative-even trivial zeros: accepted contract v1

Date: 2026-08-09

Status: **ACCEPTED AT STAGE ONE 2026-08-09; statement surface only; NOT
Lean-checked.** The independent decision is recorded in
`notes/reviews/RH021_TRIVIAL_ZERO_SIMPLICITY_ACCEPTANCE_2026_08_09.md`.

Pinned verifier baseline: Lean 4.31.0 and Mathlib commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

Owning queue: `tasks/RIEMANN_HYPOTHESIS.md`, task `RH-021`.

## 0. Exact result and scope

This contract freezes exactly four root-level public theorem signatures. The
capstone computes the local analytic order of the Riemann zeta function at
each negative-even trivial zero:

```lean
theorem analyticOrderAt_riemannZeta_neg_two_mul_nat_add_one (n : ℕ) :
    analyticOrderAt riemannZeta (-2 * (n + 1)) = 1
```

The other three declarations expose only the load-bearing local seams needed
to reach that capstone:

1. the zeta functional equation as a genuine neighbourhood equality at the
   positive odd point `2n + 3`;
2. the simple zero of `s ↦ cos (πs/2)` at that point; and
3. the resulting order of `ζ ∘ (1 - ·)` there.

There is deliberately no public theorem for the order of the functional
equation's right-hand side. That calculation is proof scaffolding for the
third declaration, not an independent mathematical result. Four declarations
are therefore the anti-inflation surface: every one is consumed downstream,
and none exists only to increase a ledger count.

This is a theorem derived entirely from the pinned formal functional equation
and pinned analytic APIs. It is **not** described as source-transcribed: the
current primary-source register contains no exact page or section locator that
states the all-`n` simplicity theorem. No external or unpinned theorem may
replace the derivation below.

## 1. Proposed imports and namespace boundary

A future drafts-lane file should use explicit imports rather than rely on
transitive availability:

```lean
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Mult
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.Nonvanishing
import Mathlib.Analysis.Analytic.Order
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Complex
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.SpecialFunctions.Gamma.Beta
import Mathlib.Analysis.SpecialFunctions.Gamma.Deriv

open Complex Filter
open scoped Real Topology
```

All four declarations remain in the root namespace, matching the existing
root-level zeta and RH interfaces. This contract introduces no new definition
of `riemannZeta`, no competing RH proposition, no new normalization, and no
new zero set.

The draft and built promotion are not authorized by `RH-021`. If this contract
is accepted, a later queue task may transcribe it into the drafts lane; a
further separate task and PR would be required for kernel promotion, imports,
ledger rows, registries and axiom audits.

## 2. Exact four-declaration surface

### T1. Neighbourhood functional equation at the positive odd point

```lean
theorem riemannZeta_comp_one_sub_eventuallyEq_functionalEquation
    (n : ℕ) :
    (riemannZeta ∘ fun s : ℂ => 1 - s) =ᶠ[𝓝 (2 * (n : ℂ) + 3)]
      (fun s : ℂ =>
        2 * (2 * π) ^ (-s) * Complex.Gamma s *
          Complex.cos (π * s / 2) * riemannZeta s)
```

This is intentionally specialised to the point used by the capstone. A
stronger exported half-plane identity would exceed the task and is not needed.

#### Proof plan

Let `s₀ : ℂ := 2 * (n : ℂ) + 3`. The open set
`{s : ℂ | 1 < s.re}` is a neighbourhood of `s₀`:

```lean
have hs₀ : 1 < s₀.re := by
  dsimp [s₀]
  simp
  positivity
have hV : {s : ℂ | 1 < s.re} ∈ 𝓝 s₀ :=
  (isOpen_lt continuous_const continuous_re).mem_nhds hs₀
```

For every `s` in this neighbourhood:

- `s ≠ -m` for every `m : ℕ`, because equality would force
  `s.re = -(m : ℝ) ≤ 0`, contradicting `1 < s.re`;
- `s ≠ 1`, for the same real-part reason.

Use `filter_upwards [hV]` and apply `riemannZeta_one_sub` pointwise, closing
the composition shape with `simpa only [Function.comp_apply]`.

The proof must produce this actual `EventuallyEq`. Quoting the pointwise
functional equation only at `s₀` is insufficient for
`analyticOrderAt_congr` and is a rejection condition.

#### Pinned dependencies and risks

- `riemannZeta_one_sub` —
  `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:176-178`, with exact
  hypotheses `(∀ n : ℕ, s ≠ -n)` and `s ≠ 1`;
- `isOpen_lt` and `continuous_re` — the same neighbourhood pattern appears
  at `Mathlib/NumberTheory/LSeries/Dirichlet.lean:439` and
  `Mathlib/NumberTheory/LSeries/DirichletContinuation.lean:83`;
- `Complex.neg_re`, `Complex.natCast_re`, `Nat.cast_nonneg` — the real-part
  exclusion bridge;
- `analyticOrderAt_congr` —
  `Mathlib/Analysis/Analytic/Order.lean:175-183`.

Obligation `T1-EVENTUAL` (**MEDIUM**): confirm the exact `filter_upwards`
normal form and the cast arithmetic. A future elaboration repair may change
only the proof body. It may not weaken `=ᶠ[𝓝 ...]` to a pointwise equality.

### T2. The cosine factor has a simple zero

```lean
theorem analyticOrderAt_cos_pi_mul_div_two_at_two_mul_nat_add_three
    (n : ℕ) :
    analyticOrderAt (fun s : ℂ => Complex.cos (π * s / 2))
      (2 * (n : ℂ) + 3) = 1
```

#### Proof plan

Again set `s₀ := 2 * (n : ℂ) + 3` and
`u s := π * s / 2`.

1. **Zero.** Apply `Complex.cos_eq_zero_iff` and choose the integer
   `k = (n : ℤ) + 1`. The remaining equality is
   `π * (2n + 3) / 2 = (2k + 1) * π / 2`; discharge casts explicitly and
   normalize by `ring`/`ring_nf`.
2. **Analyticity.** `Complex.analyticAt_cos` is entire and the inner affine
   map is analytic. `fun_prop` may close the composed `AnalyticAt`, with the
   explicit `AnalyticAt.comp` route retained as fallback.
3. **Derivative.** Do not cite `Complex.deriv_cos'` alone: it differentiates
   `cos`, not the composite. Construct the inner derivative from
   `hasDerivAt_const_mul π` followed by `HasDerivAt.div_const 2`, then use
   `HasDerivAt.ccos`. The derivative is
   `-sin (π * s₀ / 2) * (π / 2)`.
4. **Nonvanishing.** From the already proved cosine zero,
   `Complex.cos_eq_zero_iff_sin_eq` gives
   `sin (π * s₀ / 2) = 1 ∨ sin (π * s₀ / 2) = -1`. Thus the sine term is
   nonzero. The chain factor `π / 2` is nonzero by `Real.pi_ne_zero`,
   `Complex.ofReal_ne_zero` and `two_ne_zero`.
5. Apply
   `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero`.

This route deliberately avoids a second integer-parity proof through
`Complex.sin_ne_zero_iff`; the cosine-zero theorem already supplies the
stronger `sin = ±1` dichotomy.

#### Pinned dependencies and risks

- `Complex.cos_eq_zero_iff` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Complex.lean:33`;
- `Complex.analyticAt_cos` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Deriv.lean:113`;
- `HasDerivAt.ccos` — the composite chain rule at
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Deriv.lean:150-152`;
- `hasDerivAt_const_mul` —
  `Mathlib/Analysis/Calculus/Deriv/Mul.lean:362-363`;
- `HasDerivAt.div_const` — the declaration at
  `Mathlib/Analysis/Calculus/Deriv/Mul.lean:558-560`;
- `Complex.cos_eq_zero_iff_sin_eq` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:1015-1016`;
- `Real.pi_ne_zero` and `Complex.ofReal_ne_zero` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:165` and
  `Mathlib/Data/Complex/Basic.lean:140`;
- `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero` —
  `Mathlib/Analysis/Analytic/Order.lean:328-331`.

Obligation `T2-CAST` (**MEDIUM**): the integer/natural/complex cast
normalisation in the cosine-zero witness.

Obligation `T2-DERIV` (**MEDIUM**): the exact Pi/lambda shape of the inner
derivative and `HasDerivAt.ccos`. A repair may use an equivalent pinned chain
rule, but it must retain the `π / 2` factor and prove it nonzero.

### T3. The reflected zeta function has order one at the positive odd point

```lean
theorem analyticOrderAt_riemannZeta_comp_one_sub_at_two_mul_nat_add_three
    (n : ℕ) :
    analyticOrderAt (riemannZeta ∘ fun s : ℂ => 1 - s)
      (2 * (n : ℂ) + 3) = 1
```

#### Proof plan

Use T1 and `analyticOrderAt_congr` to replace the left side locally by the
functional-equation product. At `s₀ = 2n + 3`, group the right side only
inside the proof as the five Pi-valued factors

```text
constant 2 · (2π)^(-s) · Γ(s) · cos(πs/2) · ζ(s).
```

The order calculation is then

```text
0 + 0 + 0 + 1 + 0 = 1.
```

For every order-zero claim, first construct the corresponding `AnalyticAt`
term, then use `AnalyticAt.analyticOrderAt_eq_zero.mpr` with an explicit
nonvanishing witness:

- **constant `2`:** analytic by `analyticAt_const`; nonzero by
  `two_ne_zero`;
- **complex power `(2π)^(-s)`:** first construct
  `Differentiable ℂ (fun s => (2 * π) ^ (-s))` pointwise with
  `DifferentiableAt.const_cpow` applied to the differentiable exponent
  `-id`, then obtain `AnalyticAt` from `Differentiable.analyticAt`; the base
  `2π` is nonzero, and the value is nonzero by
  `Complex.cpow_ne_zero_iff`;
- **Gamma:** on the open right half-plane `{s : ℂ | 0 < s.re}`, build a
  `DifferentiableOn ℂ Complex.Gamma` term pointwise with
  `Complex.differentiableAt_Gamma`, using positivity to exclude every pole;
  obtain analyticity at `s₀` from `DifferentiableOn.analyticAt` and the
  neighbourhood membership. Nonzero follows from
  `Complex.Gamma_ne_zero_of_re_pos` since `0 < s₀.re`;
- **cosine:** rebuild the local `AnalyticAt` term from
  `Complex.analyticAt_cos` and the analytic inner affine map, then use its
  order-one equality from T2 for the product law; T2 exports the order
  equality, not the proof-local analyticity witness;
- **zeta:** analytic by the pinned neighbourhood theorem
  `analyticOn_riemannZeta`, since `s₀ ≠ 1`; nonzero by
  `riemannZeta_ne_zero_of_one_le_re`, since `1 ≤ s₀.re`.

Apply `analyticOrderAt_mul` repeatedly only after rewriting the lambda into
the matching left-associated Pi multiplication. No separate public
right-hand-side theorem is introduced.

#### Pinned dependencies and risks

- `analyticOrderAt_congr` — Order.lean:175;
- `analyticOrderAt_mul` — Order.lean:497-500;
- `AnalyticAt.analyticOrderAt_eq_zero` — Order.lean:133-135;
- `DifferentiableAt.const_cpow` —
  `Mathlib/Analysis/SpecialFunctions/Pow/Deriv.lean:111-113`;
- `DifferentiableOn.analyticAt` and `Differentiable.analyticAt` —
  `Mathlib/Analysis/Complex/CauchyIntegral.lean:625-650`;
- `Complex.cpow_ne_zero_iff` —
  `Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:49-51`;
- `Complex.differentiableAt_Gamma` —
  `Mathlib/Analysis/SpecialFunctions/Gamma/Deriv.lean:65-83`;
- `Complex.Gamma_ne_zero_of_re_pos` —
  `Mathlib/Analysis/SpecialFunctions/Gamma/Beta.lean:453-456`;
- `analyticOn_riemannZeta` —
  `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:144-145`;
- `riemannZeta_ne_zero_of_one_le_re` —
  `Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410-414`.

Obligation `T3-PI` (**MEDIUM**): expose the functional-equation lambda as the
exact left-associated Pi product consumed by `analyticOrderAt_mul` without
changing the statement.

Obligation `T3-UNIT` (**MEDIUM**): verify the `const_cpow` base/exponent
argument order and the Gamma/zeta cast arithmetic at `s₀`.

### T4. Capstone: every negative-even trivial zero is simple

```lean
theorem analyticOrderAt_riemannZeta_neg_two_mul_nat_add_one (n : ℕ) :
    analyticOrderAt riemannZeta (-2 * (n + 1)) = 1
```

#### Proof plan

Specialise the already built affine-reflection wrapper
`analyticOrderAt_comp_const_sub` at

```text
f = riemannZeta,
c = 1,
z = -2 * (n + 1).
```

It gives the exact transport

```text
analyticOrderAt (riemannZeta ∘ (1 - ·))
  (1 - (-2 * (n + 1)))
= analyticOrderAt riemannZeta (-2 * (n + 1)).
```

Use its symmetry, normalize the point
`1 - (-2 * (n + 1)) = 2 * (n : ℂ) + 3`, and close with T3.

The future proof must reuse the built wrapper rather than reopen the raw
`analyticOrderAt_comp_of_deriv_ne_zero` call. The wrapper already records and
kernel-checks the beta-redex-safe closer
`simpa only [sub_sub_cancel] using ...`; repeating the fragile raw proof would
add risk without mathematical content.

#### Pinned and repository dependencies

- `analyticOrderAt_comp_const_sub` — built
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:128-169`;
- T3;
- cast normalisation only (`push_cast`/`ring`).

Obligation `T4-POINT` (**LOW**): normalize the two syntactic point forms
without changing the capstone statement, whose expression is deliberately
identical to Mathlib's trivial-zero theorem.

## 3. Dependency DAG and exact information flow

```text
riemannZeta_one_sub + open half-plane neighbourhood
  -> T1 neighbourhood functional equation

cos_eq_zero_iff + HasDerivAt.ccos + cos_eq_zero_iff_sin_eq
  -> T2 simple cosine zero

T1 + T2
  + analytic/nonzero constant, cpow, Gamma and zeta cofactors
  + analyticOrderAt_congr/mul/eq_zero
  -> T3 reflected-zeta order at 2n+3

T3 + built analyticOrderAt_comp_const_sub
  -> T4 zeta order at -2(n+1)
```

T1 and T2 are independent. T3 consumes both. T4 consumes only T3 and the
built reflection wrapper. RH-020's Weierstrass package is not a dependency;
it merely freed the queue slot.

## 4. Exceptional-point and junk-value audit

`analyticOrderAt` returns the junk value `0` when a function is not analytic
at the point, and `⊤` when an analytic function vanishes identically near the
point. Neither branch may be mistaken for multiplicity evidence.

### At `s₀ = 2n + 3`

- `s₀.re ≥ 3`, so `s₀ ≠ 1` and zeta is analytic there;
- zeta is nonzero there by the closed-half-plane theorem;
- `s₀` is not a nonpositive integer, so Gamma is analytic there;
- Gamma is nonzero because `s₀.re > 0`;
- the cpow base `2π` is nonzero, so the cpow factor is analytic and nonzero;
- the constant is nonzero;
- the cosine derivative is nonzero, so its order is exactly the finite value
  `1`, not `0` or `⊤`;
- the product order is therefore a finite sum with exactly one nonzero
  summand.

### At `z₀ = -2(n + 1)`

- `z₀ ≠ 1`, so `riemannZeta` is analytic there despite being outside the
  critical strip;
- `riemannZeta_neg_two_mul_nat_add_one` proves the value is zero, but value
  zero alone says only that the order is nonzero;
- T4's equality to `1` excludes both `0` and `⊤`;
- affine transport is legitimate because the map `s ↦ 1 - s` has derivative
  `-1 ≠ 0`; the built wrapper handles this without any strip hypothesis.

The proof does not use Mathlib's totalized value at the pole `s = 1`, nor the
nonanalytic-junk branch of `analyticOrderAt`, nor a false global reflection
equality of zeta orders. The reflection occurs through the *functional
equation product*, whose cosine factor accounts precisely for the new zero.

## 5. Interaction with the multiplicity contract and finding A7

`MULTIPLICITY_CONTRACT.md` finding A7 correctly removed an unpinned statement
about `analyticOrderAt riemannZeta (-2) = 1` from that package's M4 note. Its
historical correction remains valid: M4 is an open-strip reflection-order
interface and neither needed nor proved trivial-zero simplicity.

Stage-one acceptance of this new contract does **not** supersede A7, because
no Lean theorem has yet been accepted. It only designs a separate package
intended to address the gap through a complete pinned derivation. If a later
promotion is kernel-green, its promotion record may state that the repository-
wide absence has been filled by the new package while leaving M4 and its dated
A7 record unchanged.

Do not edit or sharpen the historical M4 note in this task.

## 6. Claim boundary

If later kernel-checked, this package would establish exactly one local
zeta-specific fact: every negative-even trivial zero has local analytic order
one.

It does **not** state or imply:

- simplicity, multiplicity bounds, location or density of any nontrivial zero;
- simplicity of a xi zero or a relationship between xi and zeta multiplicity;
- an enumeration, ordering, truncation or count of zeros;
- a vertical-growth, entire-growth or order-one-growth estimate;
- a Hadamard or canonical product for zeta or xi;
- an explicit formula, Li coefficient, Nyman-Beurling object, cutoff choice or
  route selection;
- evidence for or against `_root_.RiemannHypothesis`.

The result is a small, genuine theorem about zeta, not an RH milestone.
`S1-GLOBAL-ZEROS` and `S1-GROWTH` remain OPEN. Every RH route remains PARKED.
No barrier is closed, advanced, partially closed, weakened or re-scoped by
stage-one acceptance or by a later proof of this theorem.

## 7. Death conditions

Reject the contract or return it to design if any of the following becomes
necessary:

1. add a hypothesis to T4, change `n : ℕ`, change the point, or weaken
   `= 1` to nonvanishing or finite order;
2. replace T1's neighbourhood `EventuallyEq` with a pointwise equality;
3. use the zeta functional equation where either of its exceptional-point
   hypotheses is not proved;
4. omit the `π / 2` chain factor in T2 or fail to prove the derivative
   nonzero;
5. infer any cofactor's order zero from nonvanishing without first proving
   analyticity at the same point;
6. use `analyticOrderAt`'s nonanalytic junk value `0` or its locally-zero
   value `⊤` as multiplicity evidence;
7. reopen a raw affine-composition proof and lose the built wrapper's
   beta-redex-safe normalization;
8. add a public helper that is only proof scaffolding, including a separate
   order theorem for the functional-equation right-hand side;
9. invoke a textbook, external or unpinned theorem instead of the complete
   pinned derivation;
10. change any of the four names, binders, hypotheses or conclusions after
    acceptance without returning to independent contract review;
11. claim progress on RH, select a route, or move a barrier row.

An elaboration failure in a proof body is not permission to alter the frozen
statement. Record the exact blocker; repair proof terms only, or return to
contract design if a signature really must change.

## 8. Two-stage gate and next authorized work

Stage one is this contract plus an independent acceptance record that checks
all four statements, the pin, the mathematical mechanism, name collisions,
junk branches and the claim boundary. Stage one carries no kernel verdict.

On accepted merge, the only authorized successor is a drafts-lane task:

- transcribe exactly these four signatures with complete proof-shaped bodies;
- independently compare all four declarations character-for-character with
  this contract;
- perform mathematical, pinned-API and dependency review;
- keep the file outside every Lake target and make no ledger or kernel claim.

Only after that task closes may a separate promotion task add a built module,
root import, ledger rows, generated registries, axiom audit and exact-head CI.
No acceptance or drafts-lane green check substitutes for the Lean kernel.

## 9. Acceptance checklist

An independent reviewer must record all of the following before returning
`ACCEPT`:

- exactly four public theorem signatures and zero definitions;
- all four names collision-free in pinned Mathlib and the repository;
- every binder, point expression and conclusion frozen exactly as in §2;
- T1 is genuinely local on `𝓝 (2 * (n : ℂ) + 3)`;
- T2 uses a composite derivative theorem and retains the `π / 2` factor;
- constant, cpow, Gamma and zeta cofactors are individually analytic and
  nonzero at the positive odd point;
- T3 uses local-order congruence and the additive product law without
  exporting proof scaffolding;
- T4 reuses the built affine-order wrapper and normalizes the point exactly;
- every `analyticOrderAt` junk branch is excluded explicitly;
- the A7 historical boundary remains unchanged;
- no statement relies on an external theorem absent from the pin;
- no route, barrier, draft, built module, import, ledger, registry or kernel
  claim is changed by this task.

Any failed item returns `REJECT/BLOCK`, not an acceptance with a weaker
capstone.
