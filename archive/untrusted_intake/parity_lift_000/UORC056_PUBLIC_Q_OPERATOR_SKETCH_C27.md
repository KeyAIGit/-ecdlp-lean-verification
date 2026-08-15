# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C27: public-Q linear-state, trace-sketch, and coordinate-sparse Krylov boundary

Date: 2026-08-15

Status: **the broad compact-state question is now separated into an exact
tautological layer and three nontrivial public-Q representation classes. An
arbitrary state `S_G(Q)` exists if and only if a parity evaluator exists, so
the unrestricted existence question cannot be simplified by renaming the
output. Inside the first natural operator classes, however, C27 gives strong
negative answers. Any nontrivial base-field linear quotient state for the
secp256k1 translation cycle has dimension at least
`ord_n(p)=(n-1)/6`, an exact 254-bit quantity. Any fixed sparse trace sketch
must charge at least `(n-1)/2` distinct relative-translation atoms, and any
coordinate-sparse bilinear/Krylov sketch must charge total cross-support at
least `(n-1)/2`. Both latter bounds are exact and tight in their expanded
models. No sublinear public-Q determinant, nonlinear implicit-spectrum state,
parity oracle, or sub-square-root ECDLP algorithm is constructed.**

Only public curve constants, public prime orders, deterministic synthetic
supports, and exact integer arithmetic are used. No external unknown-scalar
point, production target, wallet, private key, scalar bits, Euclidean quotient
sequence, dual-character table, or target-dependent advice is accepted.

The deterministic result digest is:

```text
909142870a65d643282f323b589a290cbf4e150f8bb7c06f6a07e5dbe6857315
```

## 1. What question is actually being answered?

The central target remains

```text
Q=[k]G,
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
```

with total charged cost

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
=O(n^(1/2-epsilon)).
```

If `S_G(Q)` is allowed to be an arbitrary mathematical object, then one may
set

```text
S_G(Q)=(-1)^k.
```

Therefore

```text
an efficiently constructible state with a cheap decoder
    <=>
an efficient parity evaluator.
```

The unrestricted existence question is exactly the original problem. The word
`state` creates no theorem by itself.

The useful question is representation-specific:

```text
Does parity factor through a stated compact public-Q mechanism?
```

C27 studies three such mechanisms generated from the public translation pair

```text
T_G,
T_Q=T_G^k.
```

They are:

1. a low-dimensional base-field linear quotient representation;
2. a fixed sparse family of traces of relative translations;
3. coordinate-sparse bilinear/Krylov projections.

## 2. Numeric-k and public-Q input contracts

The two contracts are not interchangeable.

Numeric contract:

```text
(n,k,a,b,c).
```

A numeric algorithm may inspect:

```text
k,
its bits,
continued-fraction quotients,
the degree k,
the smallest Mobius representative,
a Euclidean or subresultant control path.
```

Public-Q contract:

```text
(E,G,Q=[k]G,n,a,b,c).
```

The public-Q algorithm may use group and field operations on `E,G,Q`, but may
not receive the numeric representative `k`, its bits, a scalar-indexed table,
all characters, or an `n`-dimensional regular matrix as free input.

C27 credits only the second contract.

## 3. Base-field linear quotient states

Let

```text
K=F_p,
C_n=<t>,
rho:C_n -> GL_d(K).
```

Assume `n` is prime and `p` does not divide `n`.

The generator matrix `A=rho(t)` satisfies

```text
A^n=I.
```

Its minimal polynomial divides

```text
X^n-1=(X-1)Phi_n(X).
```

If the representation is nontrivial, then because `n` is prime the image of
`t` has order exactly `n`. Hence the minimal polynomial contains an
irreducible factor of the cyclotomic polynomial `Phi_n`.

Over `F_p`, every irreducible factor of `Phi_n` has degree

```text
ord_n(p),
```

the multiplicative order of `p` modulo `n`. Therefore:

```text
boxed:
d >= ord_n(p).                                      (C27.1)
```

If

```text
d < ord_n(p),
```

then the representation is trivial:

```text
rho(t)=I,
rho(Q)=rho(G)^k=I.
```

Every deterministic state that factors only through this quotient is
independent of `k`, so it cannot decode two opposite parity values.

This is not merely a faithful-representation lower bound. Since `n` is prime,
every nontrivial representation is faithful on the cyclic subgroup.

### Extension-field accounting

A one-dimensional eigencharacter can be written over an extension containing
a primitive `n`-th root. The smallest such extension has degree `ord_n(p)`.
Thus replacing a dimension-`d` base-field vector by one coordinate in
`F_(p^d)` does not reduce base-field storage.

The cost is moved from vector dimension to extension degree.

## 4. Exact secp256k1 order certificate

For secp256k1:

```text
p =
115792089237316195423570985008687907853269984665640564039457584007908834671663

n =
115792089237316195423570985008687907852837564279074904382605163141518161494337
```

C27 verifies exactly:

```text
ord_n(p)=(n-1)/6
=
19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

The exact factorization is

```text
(n-1)/6
=
2^5
*149
*631
*107361793816595537
*174723607534414371449
*341948486974166000522343609283189.
```

The executable certificate contains a complete recursive Lucas primality tree
for every prime in this factorization:

```text
45 certified prime nodes.
```

It then verifies

```text
p^d = 1 mod n
```

and, for every distinct prime divisor `q` of `d`,

```text
p^(d/q) != 1 mod n.
```

Therefore the order is exactly `d`, not only a divisor of it.

The degree satisfies

```text
2^253 < d < 2^254.
```

Consequently a nontrivial public-Q state represented as a base-field linear
quotient of the translation algebra is vastly larger than the square-root
gate.

### Frozen toy transfer

For the four semisimple frozen `(p,n)` pairs, the minimum nontrivial dimensions
are:

```text
(p,n)=(43,31):   30
(p,n)=(67,79):   13
(p,n)=(79,67):   66
(p,n)=(163,139): 69
```

The frozen pair `(127,127)` is excluded from this particular theorem because
the base-field characteristic divides the group order. It remains included in
the trace and Krylov combinatorial replay.

## 5. Sparse trace sketches

Consider fixed public channels

```text
M_i(k)
=
Tr(
  sum_((a,b) in A_i)
    c_(i,a,b) T_G^a T_Q^b
).
```

The supports and coefficients are fixed independently of the hidden scalar.
Every expanded monomial is charged.

Since

```text
T_Q=T_G^k,
```

one monomial becomes

```text
T_G^(a+bk).
```

In the order-`n` regular representation:

```text
boxed:
Tr(T_G^(a+bk))
=
n, if a+bk=0 mod n,
0, otherwise.                                      (C27.2)
```

For `b!=0`, this term differs from zero at at most one scalar:

```text
k=-a/b mod n.
```

Let `E` be the union of all nonzero exceptional residues supplied by every
atom in every channel.

Outside `E`, the complete transcript

```text
(M_1(k),...,M_r(k))
```

is constant. Coefficient cancellations can only reduce the exceptional set;
they cannot enlarge it.

## 6. Exact trace-atom lower bound

The nonzero canonical domain

```text
1,...,n-1
```

contains exactly

```text
(n-1)/2 even scalars,
(n-1)/2 odd scalars.
```

If

```text
|E| < (n-1)/2,
```

then `E` cannot contain either full parity fibre. Hence there exist an even
scalar and an odd scalar outside `E`.

Their transcripts are identical, while their parity values differ. No
deterministic decoder can be correct at both.

Therefore:

```text
boxed:
number of distinct charged exceptional ratios
>= (n-1)/2.                                        (C27.3)
```

Since each nonconstant sparse trace atom contributes at most one exceptional
ratio, the same lower bound applies to the number of expanded atoms.

For secp256k1:

```text
boxed:
trace atoms
>=
57896044618658097711785492504343953926418782139537452191302581570759080747168.
```

This is a 255-bit quantity.

### Tightness

The bound is exact in the expanded sparse-atom model.

Put one atom into a single channel for every odd scalar `r`:

```text
T_G^(-r) T_Q.
```

Then the trace is nonzero exactly when `k` is odd. This computes parity, but it
uses exactly `(n-1)/2` atoms.

Thus the theorem does not merely say that the proposed representation is
large. It identifies the optimal representation:

```text
the half-orbit orientation table itself.
```

A claimed short trace formula that expands to this channel has not compressed
the problem; it has hidden the forbidden table in its coefficients.

## 7. Coordinate-sparse Krylov and bilinear probes

Now allow fixed probes

```text
B_i(k)
=
u_i^T T_G^(a_i) T_Q^(b_i) v_i.
```

Let

```text
L_i=supp(u_i),
R_i=supp(v_i).
```

The probe can be nonzero only if

```text
a_i+b_i k = l-r mod n
```

for some

```text
l in L_i,
r in R_i.
```

For `b_i!=0`, each pair `(l,r)` determines at most one scalar. Therefore the
exceptional set of probe `i` has size at most

```text
|L_i| |R_i|.
```

Outside the union of all such sets, every nonconstant probe is zero and the
whole transcript is constant. The same parity-fibre argument gives:

```text
boxed:
sum_i |supp(u_i)| |supp(v_i)|
>= (n-1)/2.                                        (C27.4)
```

For secp256k1 this is again the exact 255-bit half-order quantity.

The bound is tight: take `v=e_0` and let `u` have support on all odd
coordinates. One query then distinguishes parity, but the vector stores the
entire odd half-orbit.

This closes coordinate-sparse Krylov/Wiedemann-style projections whose
support-generation and cross pairs are charged. It does not close a
structured dense vector generated by a genuinely compact nonlinear rule.

## 8. Newton-trace moment corollary

Consider the expanded traces

```text
Tr((aI+bT_G+cT_Q)^m),
1<=m<=d<n.
```

At level `m`, the nonconstant relative translations arise from exponent pairs

```text
j+k*l,
j>=0,
l>=1,
j+l<=m.
```

There are at most

```text
m(m+1)/2
```

such pairs. Across every moment through depth `d`, the expanded capacity is

```text
sum_(m=1)^d m(m+1)/2
=
d(d+1)(d+2)/6.
```

Therefore an expanded moment dictionary capable of covering parity must
satisfy

```text
d(d+1)(d+2)/6 >= (n-1)/2.
```

For secp256k1 the exact minimum depth is

```text
70296448064902889502766530,
```

an 86-bit integer.

This is only an expanded-monomial corollary. It is not an impossibility theorem
against an implicit nonlinear recurrence that computes high moments without
materializing their relative translations.

## 9. What has now been answered?

The broad question was:

```text
Does there exist a compact public state S_G(Q)
from which parity is cheaply decoded?
```

The exact answer now has four layers.

### Unrestricted state

```text
Equivalent to the original parity-evaluator problem.
Not resolved by renaming the output.
```

### Base-field linear quotient state

```text
No below dimension ord_n(p).
For secp256k1 the minimum nontrivial dimension is (n-1)/6.
```

### Fixed sparse trace state

```text
No below (n-1)/2 expanded relative-translation atoms.
The bound is exact.
```

### Coordinate-sparse Krylov state

```text
No below total cross-support (n-1)/2.
The bound is exact.
```

Thus a compact state, if it exists, must be genuinely nonlinear and must
generate branch-sensitive information without expanding a linear character,
trace, or coordinate-support table.

## 10. Relationship to C23-C26

C23 proves that arbitrary rational arithmetic, determinants, and resultants
cannot manufacture branch sensitivity when every leaf is sign-blind.

C24 classifies the surviving branch-sensitive leaf classes.

C25-C26 analyze sparse determinant/resultant symmetry and show that ordinary
numeric-`k` reparameterization does not produce public-Q control.

C27 adds the missing operator-side statement:

```text
a smaller base-field linear quotient is still enormous,
sparse trace access is a half-orbit table,
coordinate-sparse Krylov access is a half-orbit difference table.
```

Therefore the public-Q determinant frontier is not advanced by replacing the
regular matrix with one of these standard linear sketches.

## 11. Claim boundary

C27 closes only:

```text
base-field linear quotient representations below ord_n(p),
fixed sparse traces of relative-translation monomials,
coordinate-sparse bilinear/Krylov probes,
expanded Newton-moment dictionaries below the stated capacity.
```

It does not close:

```text
all black-box determinant algorithms,
structured dense vectors with a new compact generator,
nonlinear implicit-spectrum arithmetic circuits,
modular composition,
bounded-dimensional nonlinear rational dynamics,
theta, p-adic, elliptic-unit, or Hilbert-90 branch states,
unrestricted arithmetic circuits.
```

No unrestricted determinant, resultant, parity, ECDLP, or circuit lower bound
is claimed.

## 12. Formalization and replay

The Python package verifies:

```text
45-node recursive Lucas primality certificate,
exact secp256k1 multiplicative order,
all proper-divisor modular witnesses,
four semisimple toy representation degrees,
five frozen orders 31,79,67,127,139 for trace/Krylov,
1,999 exhaustive exceptional subsets on orders 5,7,11,13,
876 direct regular-shift trace identities,
five tight trace decoders,
five tight coordinate-sparse probe decoders,
nine unit tests,
zero failures.
```

The exact exhaustive-subset total is

```text
5+22+386+1586=1999.
```

Lean kernel-checks:

```text
equal-observable decoder obstruction,
constant-outside-exceptional obstruction,
fibre-cardinality to cost transfer,
the exact secp half-fibre arithmetic,
the exact (n-1)/6 arithmetic,
the exact factorization product,
253/254-bit linear-degree interval,
254/255-bit trace-bound interval,
minimality of the expanded moment depth.
```

Lean deliberately does not claim to formalize the complete finite-field
representation theorem or the Lucas primality proof.

## 13. Final flags

```text
sublinear_numeric_k_lacunary_algorithm_found=false
numeric_k_control_eliminated=false
sublinear_public_Q_operator_representation_found=false
sublinear_base_field_linear_quotient_found=false
sublinear_sparse_trace_sketch_found=false
sublinear_coordinate_sparse_krylov_found=false
sublinear_black_box_determinant_found=false
projective_cubic_exact_phase_decoder_found=false
a_eq_b_exact_value_formula_found=false
all_point_public_Q_replay_passed=false
exact_parity_extraction_found=false
exact_Hilbert90_branch_bridge_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

## 14. Successor

The next package is:

```text
NONLINEAR-PUBLIC-Q-ALGEBRAIC-STATE-077.
```

It must no longer propose:

```text
a smaller linear representation,
a sparse trace dictionary,
coordinate-sparse Krylov vectors,
a sign-blind determinant,
a numeric-k control path.
```

Its object is a bounded-dimensional nonlinear state

```text
S(Q) in F_p^d,
d=O(1) or polylog(n),
```

with:

```text
a public branch-sensitive leaf,
a uniform rational or algebraic update/evaluation law,
no hidden scalar index or dual phase,
all-point generator covariance,
a complete pole/zero/branch audit,
a complete cost ledger.
```

A negative result must specify the algebraic-state grammar and prove a degree,
divisor, orbit, or query lower bound. A positive result must provide an exact
public-Q parity or Hilbert-90 branch decoder.
