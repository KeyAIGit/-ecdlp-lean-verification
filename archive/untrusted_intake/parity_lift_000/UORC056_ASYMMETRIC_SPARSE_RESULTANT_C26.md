# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C26: asymmetric sparse-resultant extraction and control boundary

Date: 2026-08-14

Status: **C25 leaves two fixed-label lanes, `a=b!=c` and pairwise asymmetric coefficients. C26 identifies the only nonzero pairwise-distinct projective S3 stabilizers, namely the primitive cube-root eigenlines `(1,omega,omega^2)` and `(1,omega^2,omega)`. On these lines the sparse determinant changes along a three-cycle by a known cube-root phase. Because that phase is a square in every odd finite field containing a primitive cube root, quadratic-character and zero/nonzero extraction collide at opposite scalar parity for every screened prime order greater than eleven. Exact determinant values are not equal, so exact-value extraction is not closed by this theorem. Independently, a six-set counting theorem proves that one S3/Mobius reparameterization cannot make the sparse-polynomial degree sublinear in the worst case: some exponent orbit has minimum canonical representative at least `floor((n-3)/6)+2`. For secp256k1 this lower bound has 254 bits. A discovery and held-out screen rejects every declared fixed-small exact-value, zero-status, bounded-character, and bounded-ratio extraction, but this finite screen is not a universal fixed-label no-go theorem. No sublinear public-Q control flow, Hilbert-90 branch bridge, parity oracle, or sub-square-root ECDLP algorithm is found.**

Only public prime orders, deterministic finite fields, fixed public coefficient families, committed C25 artifacts, and public secp256k1 constants are used. No external point, unknown scalar, wallet, private key, production target, hidden scalar input, or user-supplied branch value is accepted.

## 1. The two remaining lanes

C25 closes:

```text
all zero-coefficient strata,
b=c for every prime n>11,
a=c for every prime n>11,
a=b=c for every prime n>11,
all coefficient-permutation-invariant full-S3 extractions.
```

It leaves:

```text
A. fixed-label a=b!=c,
B. fixed-label a,b,c pairwise distinct.
```

The qualifier `fixed-label` matters. The S3 identities permute coefficients together with the exponent. A same-label collision requires either an actual stabilizer of the coefficient tuple, a projective stabilizer whose known scale is ignored by the extraction, or another identity not already contained in the S3 table.

## 2. Projective S3 stabilizer classification

Let a permutation `pi` act on a nonzero coefficient triple projectively:

```text
pi(a,b,c)=lambda(a,b,c).
```

Assume all three coordinates are nonzero and pairwise distinct.

For a transposition, one coordinate is fixed. Since that coordinate is nonzero, the projective scale must be `lambda=1`, which forces the transposed coordinates to be equal. Therefore no transposition can stabilize a nonzero pairwise-distinct line.

For a three-cycle:

```text
(b,c,a)=lambda(a,b,c).
```

Hence:

```text
b=lambda a,
c=lambda^2 a,
a=lambda^3 a.
```

Since `a` is nonzero:

```text
lambda^3=1.
```

The nontrivial solutions are exactly the two primitive cube-root eigenlines:

```text
(a,b,c) proportional to (1,omega,omega^2),
(a,b,c) proportional to (1,omega^2,omega).
```

C26 exhaustively verifies this classification on ten finite fields by enumerating every normalized nonzero pairwise-distinct projective triple. This is a finite check of the elementary symbolic classification, not a replacement for it.

## 3. Exact projective phase law

For the forward eigenline:

```text
(a,b,c)=(1,omega,omega^2),
(b,c,a)=omega(a,b,c).
```

The C25 covariance identity gives:

```text
D_(a,b,c)(k)
  =D_(b,c,a)(1/(1-k))
  =omega^n D_(a,b,c)(1/(1-k)).
```

Therefore:

```text
boxed:
D(1/(1-k))=omega^(-n)D(k).                      (C26.1)
```

For the reverse eigenline:

```text
(a,b,c)=(1,omega^2,omega),
(c,a,b)=omega(a,b,c),
```

and:

```text
boxed:
D((k-1)/k)=omega^(-n)D(k).                      (C26.2)
```

The phase is public and nonzero. It transports exact values around the order-three orbit but does not make them equal.

## 4. Opposite parity on the order-three orbit

C25 gives, for every prime `n>11`, a small `j<=12` such that:

```text
parity(j) != parity(j^(-1) mod n).
```

For the forward line set:

```text
k=j+1.
```

Then:

```text
1/(1-k)=-j^(-1) mod n.
```

Because `n` is odd, negating a nonzero canonical residue complements its parity. Adding one also complements parity. Thus the two complements preserve the original mismatch:

```text
parity(j+1) != parity(-j^(-1)).                 (C26.3)
```

For the reverse line use `k=j`:

```text
(k-1)/k=1-j^(-1),
```

and the same mismatch follows.

The executable screen verifies both orbit collisions on every retained prime order from 13 through 139.

## 5. Quadratic character and zero-status no-go

In any odd finite field containing a primitive cube root, the field order is one modulo six. If `g` is a primitive generator:

```text
omega=g^((q-1)/3).
```

Since `(q-1)/3` is even, `omega` is a square. Therefore:

```text
chi_2(omega)=1,
chi_2(omega^(-n))=1.
```

Applying the quadratic character to `(C26.1)` or `(C26.2)` gives:

```text
chi_2(D(g.k))=chi_2(D(k)).                      (C26.4)
```

The zero/nonzero predicate is also unchanged by multiplication by a nonzero phase.

Together with `(C26.3)`, this proves:

```text
quadratic-character extraction cannot decode parity,
zero/nonzero extraction cannot decode parity,
```

for the projective cubic eigenlines on every prime order covered by the C25 residue theorem.

The same abstract statement holds for any extraction satisfying:

```text
Extract(omega^(-n) z)=Extract(z).
```

Lean formalizes this scale-invariant collision theorem.

Exact-value extraction is different:

```text
D(g.k)=omega^(-n)D(k)
```

usually changes the exact field value. C26 does not claim that exact values are blocked by the projective phase alone.

## 6. Six-representative degree boundary

Suppose a numeric scalar `k` is already known. The six S3/Mobius identities allow one to choose the smallest canonical exponent among:

```text
k,
1/k,
1-k,
1/(1-k),
(k-1)/k,
k/(k-1).
```

Let the nondegenerate exponent domain have cardinality:

```text
n-2.
```

For a threshold `B`, each Mobius transform is a permutation of the domain. The preimage of the representatives below `B` therefore has cardinality at most:

```text
B-2.
```

Six such preimages can cover at most:

```text
6(B-2)
```

exponents. If:

```text
6(B-2)<n-2,
```

some scalar lies outside all six preimages, so every representative in its orbit is at least `B`.

Taking:

```text
B=floor((n-3)/6)+2
```

gives:

```text
boxed:
max_k min_(g in S3) canonical(g.k)
  >= floor((n-3)/6)+2
  =Omega(n).                                     (C26.5)
```

This is a worst-case representation boundary for the following declared grammar:

```text
choose one S3/Mobius representative,
materialize a+bz+cz^d,
use degree-d polynomial, companion, or explicit modular-reduction state.
```

It does not exclude a different lacunary resultant algorithm that never materializes degree-`d` state.

Lean formalizes the six-set cover counting theorem. Python enumerates the exact maximum orbit minimum on 32 prime orders and verifies that it always meets or exceeds `(C26.5)`.

## 7. secp256k1 degree transfer

For the secp256k1 subgroup order:

```text
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337,
```

formula `(C26.5)` gives:

```text
19298681539552699237261830834781317975472927379845817397100860523586360249057.
```

This is a 254-bit lower bound on the worst transformed degree in the one-step Mobius representation grammar.

Thus the six exact symmetries do not turn every numeric-`k` trinomial into a sub-square-root polynomial problem.

## 8. Numeric `k` versus public `Q`

A lacunary resultant routine may use:

```text
the integer k,
the degree k,
the Euclidean algorithm of (n,k),
the binary expansion of k,
the smallest Mobius representative.
```

That can be a legitimate numeric-`k` algorithm. It is not yet an ECDLP evaluator whose input is only:

```text
E,G,Q=[k]G.
```

The direct public-Q realization avoids exposing `k` by using translation operators on the regular cyclic function space. Its current state dimension is exactly `n`.

C26 therefore records a scoped dichotomy:

```text
numeric-k sparse control is compact only when k is supplied,
public-Q regular control is available but has linear state.
```

No theorem here excludes a new compact public-Q control mechanism. None is constructed.

## 9. Fixed-small discovery and held-out screens

C26 declares two finite coefficient corpora before evaluation.

Lane A:

```text
30 triples (a,a,c),
a,c in {-3,-2,-1,1,2,3},
a!=c.
```

Lane B:

```text
24 ordered pairwise-distinct triples
from {-2,-1,1,2}.
```

Discovery orders:

```text
13,17,19,23,29,31,37,41.
```

Held-out orders:

```text
43,47,53,59,61,67,71,73,79,83,89,97.
```

For every coefficient triple the audit tests whether scalar parity factors through:

```text
the exact determinant value,
zero/nonzero,
multiplicative characters of orders 2,3,4,5,6,8,10,12.
```

A candidate is retained only if it avoids an opposite-parity collision on both discovery and held-out orders. No declared candidate survives.

The audit also tests the quadratic character of every ordered ratio from a fixed library of twelve coefficient variants. No ratio survives both splits.

These are finite falsification screens. They prove neither:

```text
that every integer coefficient family fails,
that exact values can never encode parity,
that every bounded ratio fails,
that every multiplicative character fails on secp256k1.
```

They do show that the simplest fixed-small positive patterns do not generalize even across modest held-out orders.

## 10. Formalization

The new Lean file:

```text
Ecdlp/Proved/Uorc056AsymmetricResultant.lean
```

formalizes:

```text
scale-invariant extraction collision blocks a parity decoder,
scale invariance along a three-cycle,
cardinality bound for a domain covered by six finite sets,
cardinality bound when each of six sets has size at most b,
contrapositive that six small sets cannot cover a larger domain.
```

The concrete determinant phase law, primitive cube-root square certificate, residue witness, projective stabilizer classification, and secp256k1 integer transfer remain deterministic executable certificates.

## 11. Cost status

No surviving construction satisfies:

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
=O(n^(1/2-epsilon)).
```

Current barriers:

| lane | status |
|---|---|
| projective cubic, quadratic character | exact opposite-parity collision |
| projective cubic, exact value | open |
| fixed-label `a=b!=c` | finite screens negative, universal theorem open |
| generic fixed-label asymmetric | finite screens negative, universal theorem open |
| one-step Mobius polynomial state | worst-case degree Omega(n) |
| numeric-k lacunary control | does not accept only public Q |
| public-Q regular representation | linear state |

## 12. Final flags

```text
projective_stabilizer_classification_verified=true
projective_cubic_phase_law_verified=true
projective_cubic_quadratic_character_blocked=true
projective_cubic_zero_status_blocked=true
projective_cubic_exact_value_blocked=false
one_step_Mobius_reparameterization_worst_case_linear=true
fixed_small_a_eq_b_exact_value_survivors=0
fixed_small_fully_asymmetric_exact_value_survivors=0
fixed_small_character_survivors=0
bounded_variant_ratio_survivors=0
fixed_small_screens_are_universal_proofs=false
a_eq_b_fixed_label_collision_proved=false
fully_asymmetric_fixed_label_collision_proved=false
sublinear_one_step_Mobius_resultant_representation_found=false
sublinear_numeric_k_resultant_algorithm_found=false
sublinear_public_Q_control_flow_found=false
exact_Hilbert90_branch_bridge_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

## 13. Successor

The successor is:

```text
PUBLIC-Q-LACUNARY-RESULTANT-CONTROL-076.
```

It must decide whether a sparse resultant can be evaluated from the public translation pair `(T_G,T_Q)` without either:

```text
recovering the numeric scalar k,
materializing the n-dimensional regular representation,
storing all subgroup characters,
receiving a degree-n polynomial or root table.
```

A parallel exact-value lane should analyze the cubic projective phase and the fixed-label `a=b!=c` family, because C26 blocks scale-invariant extraction but deliberately leaves exact values open.
