# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C33: oriented addition carry cocycle

Date: 2026-08-15

Status: **the exact lifted addition law has been derived and replayed. Its only
missing factor is the canonical modular carry cocycle. A diagonal carry after
one public halving is exactly parity, so a direct doubling-carry oracle is not a
weaker subproblem. Any normalized binary gauge that removes the carry is the
parity function itself. More generally, a multiplicative gauge differs from
parity by a group character; over the secp256k1 base field that character is
trivial, while over an extension every nontrivial character has full order
`n`. The full fixed-jump carry kernel has determinant of absolute value
`2^(n-1)` and full rank in every odd characteristic. Fixed-jump linear or
multiplicative integration is therefore linear size. No nonlocal dynamic carry
aggregator, parity oracle or sub-square-root ECDLP algorithm is constructed.**

Only public frozen curves, public prime orders and public secp256k1 constants
are used. No external unknown-scalar point, wallet, private key, scalar bits,
production target or target-dependent advice is accepted.

Deterministic replay digest:

```text
f99393a9f8dd0ff1a4f5cd865d93258ac33c13d3fe824fba2150f2b823ad3270
```

## 1. Exact target and public anchor

Let

```text
H=<G>, |H|=n,
Q=[k]G,
n odd,
sigma_G(Q)=(-1)^k.
```

The oriented root satisfies

```text
Y_G(x(Q))=sigma_G(Q)y(Q).
```

The generator anchor is public:

```text
Y_G(x(G))=-y(G).
```

C32 asks whether this one public orientation can be propagated nonlocally to an
arbitrary public query without learning the hidden canonical scalar.

C33 attacks the most direct candidate: augment ordinary elliptic addition with
a small orientation state and use an addition chain.

## 2. Exact carry normal form

For public subgroup points

```text
P=[a]G,
R=[b]G,
```

where `a,b` denote canonical representatives in `{0,...,n-1}`, define

```text
C_G(P,R)
  =sigma_G(P)sigma_G(R)sigma_G(P+R).              (C33.1)
```

Since each sign squares to one,

```text
boxed:
sigma_G(P+R)
  =C_G(P,R)sigma_G(P)sigma_G(R).                  (C33.2)
```

Write

```text
r=[a+b]_n,
a+b=r+qn,
q in {0,1}.
```

Because `n` is odd,

```text
C_G(P,R)
 =(-1)^(a+b+r)
 =(-1)^q.
```

Therefore

```text
boxed:
C_G(P,R)=+1  if a+b<n,
C_G(P,R)=-1  if a+b>=n.                           (C33.3)
```

The missing orientation factor in addition is exactly the canonical integer
carry at the wrap of the odd cyclic group.

## 3. Lifted oriented-root addition law

For nonzero `P,R,P+R`, ordinary coordinates give the denominator-free identity

```text
boxed:
Y_G(x(P+R)) y(P)y(R)
 =C_G(P,R)
  Y_G(x(P))Y_G(x(R))y(P+R).                       (C33.4)
```

Equivalently, on the regular domain,

```text
Y_G(x(P+R))
 =C_G(P,R)
  Y_G(x(P))Y_G(x(R))
  y(P+R)/(y(P)y(R)).                              (C33.5)
```

Everything except `C_G(P,R)` is available from the two oriented inputs and
public point coordinates. Thus ordinary addition does lift, but only after
supplying precisely the hidden carry.

The replay checks `(C33.4)` on

```text
5 frozen j=0 curves,
438 marked generators,
5,371,236 nondegenerate oriented additions,
0 failures.
```

## 4. The carry is a 2-cocycle

Associativity of addition gives

```text
boxed:
C(P,R)C(P+R,T)
 =C(R,T)C(P,R+T).                                 (C33.6)
```

This is not an approximate relation or a finite pattern. It follows by
expanding both sides into the four surviving signs after the repeated middle
signs square to one.

The exact scalar replay performs

```text
45,586 exhaustive cocycle checks
```

on the declared small odd orders.

The cocycle viewpoint identifies the problem correctly:

```text
ordinary point addition       public and fast,
orientation multiplication    public once signs are known,
integer-section carry          missing global datum.
```

## 5. Diagonal carry is parity-complete

Let

```text
h=2^(-1) mod n,
P=[h]Q.
```

This point is publicly computable from `Q`, and

```text
P+P=Q.
```

Therefore

```text
C_G(P,P)
 =sigma_G(P)^2 sigma_G(Q)
 =sigma_G(Q).
```

Hence

```text
boxed:
sigma_G(Q)
 =C_G([2^(-1)]Q,[2^(-1)]Q).                      (C33.7)
```

This is a constant-call equivalence:

```text
exact public doubling-carry evaluator
        <=>
exact public parity evaluator.
```

A proposed lifted doubling formula that assumes this carry has not simplified
the problem.

There is an equivalent terminal addition-chain form. Put

```text
m=(n-1)/2.
```

Then

```text
[2m]Q=-Q
```

and

```text
boxed:
sigma_G(Q)=-C_G([m]Q,[m]Q).                     (C33.8)
```

The usual binary chain for the public integer `n` ends by doubling `[m]Q` to
`-Q` and adding `Q` to reach the identity. Its entire unresolved orientation
therefore collapses to the diagonal carry in `(C33.8)`. The short scalar
addition chain has not generated a short orientation chain.

The all-generator replay verifies `(C33.7)` on all

```text
46,260 nonzero marked queries.
```

## 6. Carry-free gauge uniqueness

Suppose a normalized nonzero scalar state `U_G(P)` is intended to absorb the
carry, so its multiplicative update becomes carry-free. In standard
coboundary notation this means

```text
U(P)U(R)/U(P+R)
 =sigma(P)sigma(R)/sigma(P+R).                    (C33.9)
```

Then

```text
chi(P)=U(P)/sigma(P)
```

satisfies

```text
chi(P+R)=chi(P)chi(R).                            (C33.10)
```

Thus any two carry trivializations differ by a character of `H`.

### Binary state

For `U(P) in {+1,-1}`, the character in `(C33.10)` maps the odd-order group
into a group of order two. It is necessarily trivial. Therefore

```text
boxed:
U_G(P)=sigma_G(P).                                (C33.11)
```

The exact enumeration checks every normalized binary cochain on orders

```text
3,5,7,11,13.
```

In each case the unique solution is canonical parity.

### secp256k1 base field

For secp256k1,

```text
gcd(n,p-1)=1.
```

Therefore

```text
Hom(H,F_p^*)={1}.
```

Any `F_p^*`-valued scalar state that completely removes the carry is again
exactly `sigma_G` after normalization.

### Extension field

Over an extension field, a nontrivial character may exist. Since `n` is prime,
every nontrivial character has exact order `n`. The state then contains a
faithful dual phase rather than a bounded orientation bit.

This recovers the earlier theta and dual-character dichotomy from the addition
law itself:

```text
parity state              easy decoder, hard carry,
faithful character state  easy multiplication, full n-phase,
trivial state             no orientation information.
```

## 7. Generator-blind standard addition cannot supply the carry

For a nonzero point `P`, changing the marked generator from `G` to `-G` gives

```text
sigma_(-G)(P)=-sigma_G(P).
```

If

```text
P != O,
R != O,
P+R != O,
```

then all three signs flip, so

```text
boxed:
C_(-G)(P,R)=-C_G(P,R).                            (C33.12)
```

Ordinary point addition data do not change:

```text
P,
R,
P+R,
slopes,
line equations,
vertical lines,
curve coefficients.
```

Consequently no deterministic rational circuit built only from standard
generator-blind addition leaves can equal the carry on both marked generators.
A successful formula must consume a genuinely generator-sensitive resource,
such as the public anchor, and prove how that resource propagates to the pair.

At the exceptional opposite pair `P+R=O`, the carry is the constant `-1` and is
invariant under generator negation. This exception is treated explicitly and
does not weaken the generic obstruction.

## 8. Full rank of the fixed-jump carry kernel

Index the complete carry matrix by canonical residues:

```text
M_(a,b)=C(a,b),
0<=a,b<n.
```

Row `a` consists of `+1` until the threshold `b=n-a` and `-1` afterwards.
Starting from the bottom, replace each row `a>0` by

```text
row_a-row_(a-1).
```

Each new row has one nonzero entry, equal to `-2`, and the positions form an
anti-diagonal. Therefore

```text
boxed:
det(M)=(-1)^(n(n-1)/2) 2^(n-1).                  (C33.13)
```

The nonzero-only matrix, indexed by `1,...,n-1`, satisfies

```text
boxed:
|det(M_nonzero)|=2^(n-2).                         (C33.14)
```

Hence both matrices have full rank over every field of characteristic not two.
This includes the actual secp256k1 base field and has no C31A-style rank defect.

Consequences for the declared separated grammar:

```text
C(P,R)=sum_(i=1)^d f_i(P)g_i(R)
```

requires

```text
d>=n
```

on the complete group, or `d>=n-1` on nonzero inputs.

The exact replay verifies the determinant formula on diagnostic orders through
31 and full rank modulo every frozen base-field prime through order 139.

For secp256k1:

```text
complete carry rank = n
=115792089237316195423570985008687907852837564279074904382605163141518161494337,

nonzero carry rank = n-1
=115792089237316195423570985008687907852837564279074904382605163141518161494336.
```

This is a separated linear-state lower bound, not an unrestricted nonlinear
circuit lower bound. The integer threshold matrix has a simple nonlinear
comparison description when the scalar labels themselves are available. The
public-point problem does not provide those labels.

## 9. Fixed-jump integration is exactly linear size

For a fixed jump `b`, the function

```text
a -> C(a,b)
```

has one threshold at `a=n-b`.

Multiplying all nontrivial jump fibres gives

```text
boxed:
sigma(a)=product_(b=1)^(n-1) C(a,b).              (C33.15)
```

Indeed exactly `a` of the factors wrap.

Every factor is necessary. The ratio between the outputs at `a-1` and `a`
changes only in the column whose threshold is `a`. Since parity flips at every
adjacent canonical integer, omitting any nontrivial jump misses one required
flip.

The additive analogue is also exact:

```text
boxed:
sigma(a)=sum_(b=0)^(n-1) sigma(b)C(a,b).          (C33.16)
```

All `n` coefficients are nonzero, and uniqueness follows from the determinant
in `(C33.13)`.

Thus neither a fixed-jump product nor a fixed separated linear dictionary gives
a sub-root propagation algorithm.

## 10. Direct rational carry degree

Assume a rational function `F(P,R)` is regular on `H x H` and directly returns
`C_G(P,R)`. Restrict the second input to `R=G`.

Then

```text
F(P,G)=+1
```

at every subgroup point except `P=-G`, where it equals `-1`.

Therefore `F(P,G)-1` is nonzero and has at least `n-1` distinct zeros. Its pole
divisor is the same as the pole divisor of `F(P,G)`. Hence

```text
boxed:
deg poles_P F(P,G)>=n-1.                          (C33.17)
```

For secp256k1 this lower bound is exactly

```text
115792089237316195423570985008687907852837564279074904382605163141518161494336.
```

This closes ordinary low-degree local carry formulas. It does not close a
high-degree function generated by a short nonlinear program.

## 11. What the attack establishes

C33 gives the exact answer for a direct lifted addition chain:

```text
ordinary addition law found                         yes
missing orientation factor identified               exact carry cocycle
diagonal carry weaker than parity                    no
binary carry-free gauge beyond parity                none
base-field multiplicative gauge beyond parity        none
extension-field escape                               faithful order-n phase
standard generator-blind addition leaves sufficient no
fixed separated carry rank                           n
fixed-jump multiplicative factors required           n-1
low-degree direct rational carry                      excluded
```

The lifted addition-chain idea is therefore not discarded. It is narrowed to
one remaining possibility:

```text
a nonautonomous field-valued circuit that computes a product or aggregate of
several dynamic carry factors without evaluating any parity-complete carry in
isolation and without materializing a linear-size carry dictionary.
```

## 12. Successor

The successor is

```text
DYNAMIC-ORIENTED-CARRY-AGGREGATION-C34.
```

Its first target is the carry product attached to a public addition chain for
`[n]Q=O`. Recursively expanding the orientation equations expresses
`sigma_G(Q)` as a product of selected dynamic carries

```text
C_G([a_i]Q,[b_i]Q).
```

The package must determine whether this complete product telescopes to one
Miller, elliptic-net, division-polynomial, determinant, resultant or
Hilbert-90 value that is computable from `Q` without numeric `k`.

A positive result must provide the literal aggregate and complete cost. A
negative result must name an exact dynamic-carry grammar and prove a covariance,
divisor, rank, query or representation obstruction.

## 13. Final flags

```text
public_oriented_anchor_used=true
exact_lifted_addition_law_found=true
missing_factor_identified_as_carry_cocycle=true
doubling_carry_is_parity_complete=true
binary_carry_free_gauge_found_beyond_parity=false
base_field_multiplicative_carry_free_state_found=false
fixed_jump_linear_subroot_integration_found=false
fixed_jump_multiplicative_subroot_integration_found=false
generator_blind_standard_addition_formula_can_supply_carry=false
dynamic_carry_aggregation_found=false
nonlocal_propagation_law_found=false
numeric_scalar_control_used=false
all_point_public_Q_replay_passed=true
exact_oriented_root_extraction_found=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
