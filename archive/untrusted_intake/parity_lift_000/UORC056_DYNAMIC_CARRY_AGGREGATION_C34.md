# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C34: dynamic oriented carry aggregation

Date: 2026-08-15

Status: **C34 builds an exact addition-DAG compiler and proves that every
public addition DAG for an integer `m` produces the same scalar aggregate
`A_m(Q)=sigma_G(Q)^m sigma_G([m]Q)`, although the internal carry supports can
be different. For `m=n`, this aggregate is canonical parity. More strongly,
parity admits an exact product of three dynamic carry factors, and on every
declared order at least 13 the selected three factors are individually not
parity-complete under any public scalar rescaling. No pair of individually
noncomplete carries survives the declared exact small-order screen. However,
the three-carry formula does not yet yield a public field-valued evaluator: it
uses only scalar multiples of `Q`, so any ordinary coordinate, Miller, net,
line or division-polynomial realization without the generator anchor is
unchanged under `G -> -G`, while the target changes sign. Thus C34 obtains a
constant semantic compression but not a computational compression. No parity
oracle or sub-square-root ECDLP algorithm is constructed.**

Deterministic digest:

```text
db440926f75be39c63497e0f38124028b5158f0f25113674c666c901eab9b31d
```

## 1. Addition-DAG normal form

Start with one leaf of weight one, representing `Q`. At every public addition
gate combine weights `a` and `b`. Let the compiled carry product at weight `m`
be `P_m(Q)`. The gate rule is

```text
P_(a+b)=C_G([a]Q,[b]Q) P_a P_b.
```

Repeated sub-DAG factors are counted modulo two because carry values are signs.
Induction gives

```text
boxed:
P_m(Q)=A_m(Q)=sigma_G(Q)^m sigma_G([m]Q).          (C34.1)
```

Thus the scalar output depends only on `m`, not on the addition DAG. For
`m=n`, `[n]Q=O`, `sigma_G(O)=1`, and `n` is odd, hence

```text
boxed:
P_n(Q)=sigma_G(Q).                                 (C34.2)
```

Binary, balanced and linear DAGs have different internal carry supports on all
declared diagnostic orders, but their products agree on every scalar.

## 2. Constant three-carry factorization

Let

```text
T=[-1/2]Q,
A=[a]Q,
B=T-A.
```

Then

```text
A+B=T,
2T=-Q,
-T-B=Q+A.
```

Expanding the three carries and using `sigma(-P)=-sigma(P)` gives

```text
boxed:
sigma_G(Q)
 =C_G(Q,A)
  C_G(A,B)
  C_G(-T,-B).                                     (C34.3)
```

A fixed convenient choice is

```text
A=[2]Q,
T=[(n-1)/2]Q,
B=[(n-1)/2-2]Q.
```

For secp256k1 the public carry pairs are

```text
(1,2),
(2,(n-1)/2-2),
((n+1)/2,(n+1)/2+2).
```

The exact replay verifies this identity on all 46,260 frozen marked-query
cases.

## 3. The three factors are not the old diagonal oracle

A dynamic carry `C_G([a]Q,[b]Q)` is individually parity-complete when one
public scalar rescaling turns it into canonical parity. Three obvious families
are

```text
a=b,
b=-2a,
a=-2b.
```

The exhaustive screen on orders

```text
7,11,13,17,19,23,29,31
```

finds exactly these families and no others. This is a finite exact
classification on the declared orders, not an all-prime theorem.

For the three fixed factors in `(C34.3)`, every factor is individually
noncomplete on

```text
13,17,19,23,29,31,43,67,79,127,139.
```

No product of two individually noncomplete carries equals parity on the exact
screen through order 31. This is finite evidence, not a universal two-factor
lower bound.

## 4. Why semantic compression is not yet computation

Insert the C33 lifted-addition formula into the three factors in `(C34.3)`.
Every intermediate oriented-root value cancels in pairs, using

```text
Y_G(x(-P))=Y_G(x(P)),
Y_G(x(P))^2=y(P)^2.
```

The remaining ratio is

```text
y(Q)/Y_G(x(Q))=sigma_G(Q).                         (C34.4)
```

Thus the three factors isolate the target branch with constant semantic width,
but do not replace the final unknown oriented value by public data.

All points in `(C34.3)` are public scalar multiples of `Q`. Ordinary
coordinates, addition lines, fixed-index Miller functions, division
polynomials, elliptic-net values, resultants and determinants generated only
from those Q-dependent leaves are unchanged when the marked generator changes
from `G` to `-G`. But

```text
sigma_(-G)(Q)=-sigma_G(Q).
```

Therefore no Q-only rational field expression can realize the aggregate for
both markings. A positive realization must genuinely consume the public anchor

```text
Y_G(x(G))=-y(G)
```

or an equivalent generator-sensitive resource.

## 5. Replay and formalization

The package checks

```text
24 addition DAG instances,
450 chain-profile scalar checks,
8 orders with distinct internal supports,
11 three-carry orders,
576 direct three-carry scalar checks,
46,260 frozen marked-query checks,
8 exact single-carry classification screens,
8 exact two-carry screens,
0 two-carry survivors,
0 failures.
```

Lean kernel-checks the aggregate gate identity, three-carry sign cancellation,
chain equality from a common aggregate, the equal-public-data decoder
obstruction and fixed secp256k1 multiplier relations. Finite classifications
and Miller or net complexity statements are not labeled kernel-checked.

## 6. Decision

```text
addition DAG compiler                              built
chain-independent carry aggregate                  proved
terminal aggregate for [n]Q                        parity
constant three-carry semantic factorization        found
selected factors individually parity-complete      no on declared screens
two noncomplete factors sufficient                 no on declared screens
Q-only field realization                           blocked
anchor-dependent field realization                 not found
public parity evaluator                            absent
sub-square-root ECDLP                              absent
```

## 7. Successor

The successor is

```text
ANCHOR-MIXED-CARRY-RESULTANT-C35.
```

It must mix the public generator anchor with the three-carry geometry. The
first target is a field-valued object involving both `G` and the public
multiples of `Q` whose transformation under `G -> -G` matches `(C34.3)`.
Candidate classes are mixed Miller products, anchor-normalized elliptic-net
cells, recursive resultants with one oriented G-row, and Hilbert-90 transfer
matrices seeded at the public anchor.

Final flags:

```text
addition_dag_compiler_built=true
carry_product_chain_independence_proved=true
all_public_chains_reduce_to_canonical_aggregate=true
three_carry_semantic_compression_found=true
three_carry_factors_individually_noncomplete_on_declared_screens=true
two_noncomplete_carry_product_found_on_declared_screens=false
q_only_field_aggregate_blocked=true
public_anchor_consumed_by_three_carry_formula=false
anchor_dependent_field_aggregate_found=false
miller_carry_aggregate_found=false
elliptic_net_carry_aggregate_found=false
hilbert90_carry_aggregate_found=false
dynamic_carry_lower_bound_proved=false
all_point_public_Q_replay_passed=true
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
