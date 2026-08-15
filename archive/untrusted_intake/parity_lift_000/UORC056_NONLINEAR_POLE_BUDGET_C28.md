# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C28: nonlinear rational-state pole-budget boundary

Date: 2026-08-15

Status: **C28 builds an exact pole-budget compiler and proves that every
ordinary rational parity evaluator on the marked subgroup must have pole degree
at least `(n-1)/2`. The same lower bound follows independently from the
translation defect `Delta_f(P)=f(P+G)+f(P)`. Applied to the proposed CM state
`S_G(Q)=(A(x(Q)^3),B(x(Q)^3))`, the declared direct decoder cannot work when
both state coordinates have pole degree below the exact 253-bit threshold
recorded here. If `A` and `B` are ordinary polynomials in `T=x^3` of a common
degree `d`, then `d` must exceed an exact 250-bit threshold. These are strong
low-algebraic-complexity exclusions, not an unrestricted arithmetic-circuit
lower bound. Degree growth alone forces only about 255 binary arithmetic gates,
so a high-degree low-size nonlinear recurrence remains the precise surviving
question. No compact state, parity oracle, or sub-square-root ECDLP algorithm is
constructed.**

Only public secp256k1 constants, deterministic prime-field rational controls,
and symbolic pole budgets are used. No external point, private key, wallet,
unknown production scalar, scalar bits, or target-dependent advice is accepted.

Deterministic result digest:

```text
593cabc70da562d0f4ecdfce7483272fc7c693a8d6c71643217e3abd605361de
```

## 1. Why another complexity measure is needed

C27 closes three natural linear/operator states:

```text
base-field linear quotient states,
fixed sparse trace sketches,
coordinate-sparse Krylov sketches.
```

The surviving possibility is nonlinear. A nonlinear circuit can have a tiny
description but enormous algebraic degree, as repeated squaring demonstrates.
Therefore C28 separates two questions:

```text
Is the parity function algebraically small?
Is it computationally small despite enormous algebraic degree?
```

C28 answers the first negatively in an exact rational-function model. It does
not answer the second.

## 2. Rational parity requires half-order pole degree

Let `E` be a smooth projective curve over a field of characteristic not two,
let `H=<G>` have odd prime order `n`, and let `f` be a rational function regular
at all nonzero marked subgroup points. Assume

```text
f([k]G)=(-1)^k,
1<=k<n.
```

Both signs occur, so `f` is not the constant `+1` or `-1`. Hence

```text
h=f^2-1
```

is a nonzero rational function. It vanishes at all `n-1` marked points.
Therefore

```text
deg zeros(h) >= n-1.
```

For a nonzero rational function on a smooth projective curve, total zero degree
equals total pole degree. At each pole of `f`, the term `f^2` dominates the
constant `1`, so

```text
deg poles(h)=2 deg poles(f).
```

Consequently

```text
boxed:
deg poles(f) >= (n-1)/2.                          (C28.1)
```

For secp256k1:

```text
boxed:
deg poles(f)
>=
57896044618658097711785492504343953926418782139537452191302581570759080747168.
```

This is a 255-bit lower bound.

The theorem says that parity is not a low-degree rational observable. It does
not say that evaluating a high-degree rational observable requires a large
circuit.

## 3. Independent translation-defect theorem

Canonical parity changes sign on every non-wrap translation edge:

```text
f([k+1]G)+f([k]G)=0,
1<=k<=n-2.
```

Define

```text
Delta_f(P)=f(P+G)+f(P).
```

This rational function has at least `n-2` marked zeros.

It cannot vanish identically. If

```text
f(P+G)=-f(P)
```

held as a function identity, then iterating through the odd order `n` would give

```text
f(P+nG)=(-1)^n f(P)=-f(P).
```

But `P+nG=P`, so `f=-f`, and characteristic not two would force `f=0`, contrary
to the marked values.

Translation preserves pole degree and addition gives the safe bound

```text
deg poles(Delta_f) <= 2 deg poles(f).
```

Therefore

```text
n-2 <= 2 deg poles(f),
```

which, since `n` is odd, again gives

```text
boxed:
deg poles(f) >= (n-1)/2.                          (C28.2)
```

The two proofs use different information:

```text
C28.1 uses binary output values,
C28.2 uses the local alternating translation law.
```

## 4. Pole-budget compiler

C28 introduces a small executable grammar. For a nonzero rational function
`F`, let

```text
B(F)=deg poles(F).
```

The safe rules are

```text
B(constant)=0,
B(-F)=B(F),
B(F+G)<=B(F)+B(G),
B(FG)<=B(F)+B(G),
B(1/F)=B(F),
B(F^m)=m B(F).
```

These rules compile a rational straight-line expression into an upper bound on
its pole degree. The Python implementation also contains exact rational
functions over finite prime fields and verifies the rules after reduction by
polynomial gcd.

The deterministic control suite checks

```text
3 prime fields,
4 rational functions per field,
204 exact operation-budget inequalities,
0 failures.
```

Lean independently defines the expression grammar and kernel-checks its budget
function and the direct CM decoder compilation.

## 5. Applying the compiler to the `A/B` state

The proposed state is

```text
S_G(Q)=(A(T),B(T)),
T=x(Q)^3.
```

The known decoder is

```text
f(Q)
=
(2A^2+2AxB-x^2B^2)/(2yA).
```

Write

```text
a=B(A),
b=B(B),
B(x)=2,
B(y)=3.
```

The compiler gives

```text
B(numerator)<=3a+3b+6,
B(denominator)=a+3,
```

and therefore

```text
boxed:
B(f)<=4a+3b+9.                                    (C28.3)
```

If both state coordinates have pole budget at most `delta`, then

```text
B(f)<=7 delta+9.
```

Combining with C28.1 gives the exact necessary condition

```text
7 delta+9 >= (n-1)/2.
```

For secp256k1 the smallest possible integer is

```text
boxed:
delta >=
8270863516951156815969356072049136275202683162791064598757511652965582963880.
```

This is a 253-bit quantity. The preceding integer fails the inequality and the
recorded integer succeeds.

Thus a pair of low-pole-degree rational coordinates cannot be the desired
compact state under this decoder.

## 6. Ordinary polynomials in `T=x^3`

The function `x` has pole degree two at infinity, so

```text
B(T)=B(x^3)=6.
```

If `A(T)` and `B(T)` are ordinary polynomials of degree at most `d`, then

```text
a<=6d,
b<=6d.
```

Equation C28.3 gives

```text
B(f)<=42d+9.
```

Hence

```text
42d+9 >= (n-1)/2.
```

For secp256k1:

```text
boxed:
d >=
1378477252825192802661559345341522712533780527131844099792918608827597160647.
```

This is a 250-bit degree threshold. It closes ordinary low-degree `A/B`
polynomial states but not high-degree polynomials represented by short
composition chains.

## 7. Why the theorem does not finish the problem

Suppose a circuit begins with total pole budget `B0`. Every binary addition or
multiplication can at most add two existing budgets. Along `s` binary gates,

```text
B(output)<=2^s B0.
```

Therefore degree alone yields only

```text
s >= ceil(log_2(((n-1)/2)/B0)).
```

For secp256k1 the exact minimum gate counts produced by this crude compiler are

```text
B0=1:   255
B0=5:   253
B0=7:   253
B0=10:  252
B0=100: 249
B0=256: 247.
```

These are logarithmic in `n`. A 253-gate circuit would be extraordinarily
small compared with `sqrt(n)`. Therefore no honest argument may conclude from
the 255-bit pole degree that the evaluator is computationally hard.

This is the key scientific answer of C28:

```text
low-degree compact state is impossible,
high-degree low-size compact state is still logically possible.
```

## 8. Finite exact controls

For scalar-index controls over prime fields, C28 interpolates the alternating
values on orders

```text
5,7,11,13,31.
```

For every case it verifies

```text
f^2-1 is nonzero,
f^2-1 vanishes at all n-1 marked scalars,
f has pole degree at least (n-1)/2,
Delta_f is nonzero,
Delta_f vanishes at all n-2 non-wrap edges,
zero counts do not exceed the exact rational degree.
```

These finite controls illustrate the algebraic mechanism. They are not a proof
of the projective-curve divisor theorem, which is stated separately.

## 9. Closed and surviving classes

Closed by C28:

```text
ordinary rational parity functions below half-order pole degree,
bounded-pole rational states whose decoder compiles below the half-order,
the direct A/B state below the exact 253-bit coordinate threshold,
ordinary polynomial-in-T A/B states below the exact 250-bit degree threshold.
```

Still open:

```text
high-degree low-size arithmetic circuits,
implicit modular composition,
nonlocal joint A/B recurrences,
structured algebraic correspondences without a small pole budget,
theta, p-adic, elliptic-unit, or Hilbert-90 branch-sensitive states,
unrestricted arithmetic circuits.
```

## 10. Formalization boundary

Lean kernel-checks

```text
the pole-expression grammar,
the budget of every grammar constructor,
the exact A/B decoder budget 4a+3b+9,
the equal-coordinate bound 7delta+9,
the integer zero-count transfers,
all fixed secp256k1 threshold and bit-length arithmetic.
```

Lean does not yet formalize

```text
divisors on the specific elliptic curve,
equality of zero and pole degree,
marked subgroup root transfer,
the translation pullback divisor identity.
```

Those are not presented as kernel-checked.

## 11. Final answer and successor

C27 and C28 together eliminate the most natural compact states based on

```text
small linear representations,
sparse traces,
sparse Krylov probes,
low-degree rational observables,
low-pole-degree A/B coordinates.
```

The one remaining central mechanism is now sharply defined:

```text
HIGH-DEGREE-LOW-SIZE-BRANCH-STATE-078.
```

A positive object must be a uniform nonlocal nonlinear circuit whose degree or
pole budget grows exponentially, while its public branch-sensitive seed,
coefficient generation, memory, field extensions, and online evaluation remain
sub-square-root.

Final flags:

```text
pole_budget_tool_built=true
translation_defect_bound_proved=true
low_degree_algebraic_state_blocked=true
joint_A_B_recurrence_found=false
modular_composition_state_found=false
high_degree_low_size_state_blocked=false
bounded_dimensional_nonlinear_state_found=false
public_branch_sensitive_seed_found=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
