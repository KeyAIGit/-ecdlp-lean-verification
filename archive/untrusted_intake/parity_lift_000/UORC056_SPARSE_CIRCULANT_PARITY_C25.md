# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C25: sparse-circulant parity classification

Date: 2026-08-14

Status: **The full six-element affine/Mobius action on the sparse circulant determinant is now explicit and replayed. Every coefficient stratum containing a zero is independent of the unknown exponent on the nondegenerate domain. For repeated coefficients, the `b=c`, `a=c`, and all-equal strata admit opposite-parity stabilizer collisions for every prime order greater than eleven. This is certified by a complete residue-class cover modulo 55440 with witnesses at most 12. The `a=b` stabilizer is different: it acts by `k -> 1-k`, whose canonical representative preserves parity for odd order, so that stratum is classified but not blocked by its stabilizer. For fully asymmetric coefficients, every extraction invariant under permutation of the coefficient labels is blocked by the full S3 orbit collision, while a fixed-label asymmetric extraction remains open. The only public realization currently known uses the order-n regular representation, an order-n root product, or an equivalent degree-n resultant. No sublinear public-Q realization, exact parity extraction, Hilbert-90 branch bridge, parity oracle, or sub-square-root ECDLP algorithm is found.**

Only public prime orders, fixed public finite fields, the frozen subgroup-order list, public secp256k1 constants, and the committed C5 source artifact are used. No external point, unknown scalar, wallet, private key, or production target is accepted.

Exact replay digest:

```text
d2d7e45be77b5502a286058a0a935ea751d472de84d5b876169a52df9e453586
```

## 1. Exact object

Let `n` be an odd prime, let `T` be the regular cyclic shift, and let `Q=[k]G`. The candidate family is

```text
D_(a,b,c)(k)
  = det(a I + b T + c T^k)
  = Res_z(z^n-1, a+bz+cz^k)
  = product_(zeta^n=1) (a+b zeta+c zeta^k).
```

The nondegenerate exponent domain is

```text
2 <= k < n.
```

Rejecting a decoder on this subset is enough to reject an all-scalar parity decoder. The cases `k=0,1` can be handled separately and cannot repair an opposite-parity collision inside the nondegenerate domain.

## 2. Full affine exponent action

An affine change of the exponent triple `{0,1,k}` chooses one exponent as the new zero, one as the new one, and sends the third to a cross-ratio transform. Because multiplication by an `n`-th root has total product one for odd `n`, and because every nonzero exponent multiplier permutes the roots of unity, the exact identities are

```text
D_(a,b,c)(k)
=D_(a,c,b)(1/k)
=D_(b,a,c)(1-k)
=D_(b,c,a)(1/(1-k))
=D_(c,a,b)((k-1)/k)
=D_(c,b,a)(k/(k-1)).
```

The corresponding table is:

| transform of `k` | coefficient order |
|---|---|
| `k` | `(a,b,c)` |
| `1/k` | `(a,c,b)` |
| `1-k` | `(b,a,c)` |
| `1/(1-k)` | `(b,c,a)` |
| `(k-1)/k` | `(c,a,b)` |
| `k/(k-1)` | `(c,b,a)` |

C25 verifies these identities over 32 prime orders, every admissible `k`, 17 fixed coefficient samples spanning all equality and zero strata, and exact finite fields containing the required roots of unity.

Total exact covariance checks:

```text
209916.
```

This is a finite replay of an algebraic identity, not the source of the identity itself.

## 3. Zero-coefficient strata

If one coefficient vanishes, the determinant is a two-term cyclic norm.

For `c=0`:

```text
D_(a,b,0)(k)=product_zeta(a+b zeta),
```

which does not depend on `k`.

For `b=0`, the map `zeta -> zeta^k` permutes the `n`-th roots, so

```text
D_(a,0,c)(k)=product_zeta(a+c zeta).
```

For `a=0` and `k` different from one:

```text
b zeta+c zeta^k
  = zeta (b+c zeta^(k-1)).
```

The product of all `n`-th roots is one for odd `n`, and `k-1` is invertible modulo prime `n`. Hence this stratum is also independent of `k`.

Therefore every zero-coefficient stratum is constant on the nondegenerate scalar domain and cannot decode parity. The replay performs

```text
12348
```

exact independence checks.

Lean formalizes the abstract consequence: a constant observable already collides at indices one and two, which have different parity.

## 4. Repeated coefficients and their stabilizers

There are three nontrivial transposition stabilizers.

### 4.1 `b=c`

Swapping the last two coefficients leaves the tuple fixed and gives

```text
D(k)=D(1/k).
```

Any `k` whose canonical inverse has opposite parity is an exact no-go witness.

### 4.2 `a=c`

Swapping the first and third coefficients gives

```text
D(k)=D(k/(k-1)).
```

Writing `k=j+1`, one has

```text
k/(k-1)=1+j^(-1).
```

Thus a parity mismatch between `j` and `j^(-1)` gives a parity mismatch between `j+1` and `(j+1)/j`.

### 4.3 `a=b`

Swapping the first two coefficients gives

```text
D(k)=D(1-k).
```

For `1<k<n`, the canonical representative is

```text
n+1-k.
```

Since `n+1` is even,

```text
parity(n+1-k)=parity(k).
```

Therefore this stabilizer preserves the target parity and does not itself reject the `a=b` family.

This is a genuine difference among the three repeated-coefficient strata. C25 does not overstate the symmetry argument by declaring every repeated tuple impossible.

### 4.4 All coefficients equal

The all-equal tuple has the full S3 stabilizer. In particular it inherits the inversion collision and is blocked whenever inversion has an opposite-parity orbit pair.

## 5. Complete residue certificate for inversion parity

The earlier C5 report used the explicit secp256k1 witness `k=2`, valid because the secp256k1 order is one modulo four. C25 extends this to every prime order greater than eleven.

Use the witness set

```text
J={2,3,4,5,7,8,9,10,11,12}.
```

For a fixed `j`, let `x` be the least positive inverse of `j` modulo odd `n`. Then

```text
j x = 1+t n,
1 <= t < j.
```

The value of `t` is determined by `n mod j`, and the parity of `x` is determined by `n mod 2j`. Therefore the parity relation between `j` and `j^(-1)` depends only on the residue of `n` modulo a common multiple of all `2j`.

C25 uses

```text
M=55440.
```

This is divisible by `2j` for every `j` in the witness set. The executable certificate enumerates all

```text
phi(55440)=11520
```

invertible residue classes. Every class has at least one witness `j` for which

```text
parity(j) != parity(j^(-1) mod n).
```

It also checks parity stability on two representatives separated by `M` for every residue and every candidate witness, for a total of

```text
115200
```

stability checks.

Every prime `n>11` is coprime to `55440`, so the residue cover applies. The first-witness frequencies over the 11520 unit classes are:

```text
j=2:  5760
j=3:  2880
j=4:  1440
j=5:   720
j=7:   360
j=8:   180
j=9:    60
j=10:   60
j=11:   30
j=12:   30
```

Small prime orders are retained explicitly:

```text
n=5:  witness 2 -> 3,
n=7:  no inversion parity mismatch,
n=11: witness 3 -> 4.
```

Thus `n=7` is a real finite exception to this stabilizer theorem. It is not silently discarded. In fact some tiny all-equal examples can separate parity at order seven; this does not create an asymptotic family or a secp256k1 evaluator.

## 6. Consequence for repeated coefficient strata

For every prime order greater than eleven:

```text
b=c      is blocked by inversion,
a=c      is blocked by k/(k-1),
a=b=c    is blocked by the full S3 stabilizer.
```

The replay checks the actual determinant equality at the certified witness on every screened order where a witness exists. It records

```text
186
```

opposite-parity repeated-stratum determinant collisions.

The remaining repeated family is exactly

```text
a=b!=c.
```

Its forced stabilizer preserves parity. It requires a different argument or a positive evaluator.

## 7. Fully asymmetric coefficients

A fully asymmetric coefficient triple has trivial label stabilizer. Therefore the equality

```text
D_(a,b,c)(k)=D_(a,c,b)(1/k)
```

does not by itself collide two values of the same fixed-label observable.

However, suppose an extraction uses the six coefficient permutations and is invariant under relabeling, for example:

```text
the multiset of six determinant values,
a symmetric polynomial of those values,
their product, sum, trace, norm, or unordered character profile.
```

The full S3 action only permutes this six-value tuple. Hence the symmetric extraction has the same value on `k` and `1/k`. The residue certificate supplies opposite parity for every prime `n>11`.

C25 verifies

```text
93
```

such coefficient-symmetric orbit collisions on the finite screens.

Therefore:

```text
coefficient-symmetric extraction is blocked,
fixed-label fully asymmetric extraction remains open.
```

A label-sensitive extraction must explain why the public coefficient labeling is canonically tied to the desired Hilbert-90 branch rather than being an arbitrary external convention.

## 8. Finite exact-value and character diagnostics

For each screened coefficient sample, C25 also asks whether the exact determinant value or its quadratic character happens to separate parity on that one finite field and order.

These are diagnostics only. Tiny orders can exhibit accidental exact separation. Conversely, failure on the finite screen is not an unrestricted impossibility theorem.

No candidate is promoted from this diagnostic. Promotion requires one uniform coefficient family, an all-order theorem, public-Q realization, generator covariance, and a complete cost ledger.

## 9. Public-Q realization and cost

The determinant is basis-free as an operator on the regular function space of the cyclic subgroup. Given public `G` and `Q`, one can in principle construct translations `T_G` and `T_Q` without first writing the scalar `k`. The direct realization nevertheless has:

```text
function-space dimension n,
permutation basis of size n,
root-product length n,
resultant degree n,
Sylvester or companion state of linear dimension.
```

Thus a public-Q realization is known only with linear charged representation or state.

A sparse resultant algorithm receiving the integer `k` is not yet a public-Q evaluator, because `k` is precisely the unknown scalar. To pass the gate, its control flow must be driven directly by public group operations or a compact operator representation without recovering `k` and without materializing the regular representation.

Current status:

```text
linear_regular_representation_public_Q_realization_known=true
sublinear_public_Q_operator_realization_found=false
sublinear_sparse_resultant_representation_found=false
```

This is a scoped representation result, not an unrestricted determinant lower bound.

## 10. secp256k1 transfer

The secp256k1 subgroup order is

```text
115792089237316195423570985008687907852837564279074904382605163141518161494337
```

and satisfies

```text
n mod 4 = 1.
```

The first residue witness is `j=2`. Its inverse is

```text
57896044618658097711785492504343953926418782139537452191302581570759080747169.
```

The first shifted `k/(k-1)` witness is `k=3`, with image

```text
57896044618658097711785492504343953926418782139537452191302581570759080747170.
```

Therefore on secp256k1:

```text
b=c      is rejected,
a=c      is rejected,
a=b=c    is rejected,
all zero-coefficient strata are rejected,
coefficient-symmetric full-S3 extraction is rejected.
```

Still open:

```text
a=b!=c with fixed labels,
fully asymmetric fixed-label coefficients.
```

The explicit regular representation and root product both require exactly `n` states or terms at the current level of description.

## 11. Lean formalization

The new file

```text
Ecdlp/Proved/Uorc056SparseCirculant.lean
```

formalizes:

```text
canonical parity preservation under k -> 1-k,
opposite parity of 2 and (n+1)/2 when n=1 mod 4,
opposite parity of 3 and (n+3)/2 when n=1 mod 4,
a generic opposite-parity observable collision theorem,
specialized inversion and k/(k-1) collision no-go theorems,
constant-observable parity impossibility,
full-orbit symmetric-extraction collision implication.
```

The full residue cover and determinant identities remain exact executable certificates. Lean does not claim an unrestricted resultant lower bound or a concrete elliptic-curve branch bridge.

## 12. Exact replay coverage

The screen contains 32 prime orders from 5 through 139 and includes all frozen public subgroup orders:

```text
31,61,67,79,127,139.
```

Exact aggregate counts:

```text
S3 covariance checks:                         209916
one-minus parity checks:                       34986
zero-coefficient independence checks:          12348
repeated opposite-parity collisions:             186
coefficient-symmetric extraction collisions:       93
unit residue classes:                          11520
inverse-parity stability checks:              115200
```

The C5 source artifact is digest-bound:

```text
sha256=fc846581a511e4256d9e36507d6c13156d314890234c807b01a5346319af11a4
bytes=2284
```

## 13. Final flags

```text
full_S3_Mobius_action_verified=true
all_zero_coefficient_strata_blocked=true
all_repeated_coefficient_strata_classified=true
b_eq_c_blocked_for_all_primes_gt_11=true
a_eq_c_blocked_for_all_primes_gt_11=true
all_equal_blocked_for_all_primes_gt_11=true
a_eq_b_stabilizer_parity_preserving=true
a_eq_b_repeated_stratum_fully_blocked=false
coefficient_symmetric_extraction_blocked_for_all_primes_gt_11=true
fully_asymmetric_parity_collision_proved=false
finite_exception_n7_retained=true
sublinear_sparse_resultant_representation_found=false
linear_regular_representation_public_Q_realization_known=true
sublinear_public_Q_operator_realization_found=false
exact_parity_extraction_found=false
exact_Hilbert90_branch_bridge_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

## 14. Successor

The surviving target is

```text
ASYMMETRIC-SPARSE-RESULTANT-EVALUATION-075.
```

It has two lanes:

```text
A. fixed-label a=b!=c,
B. fixed-label fully asymmetric (a,b,c).
```

The next package must decide whether either lane has a uniform parity or Hilbert-90 branch law and, independently, whether its one-value determinant can be realized from public `Q` with sub-square-root total state. A numeric algorithm controlled by the hidden integer `k` does not satisfy the public-Q requirement.
