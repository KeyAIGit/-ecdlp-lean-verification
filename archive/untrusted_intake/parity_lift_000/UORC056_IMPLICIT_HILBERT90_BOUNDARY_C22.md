# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C22: implicit Hilbert-90 evaluation boundary

Date: 2026-08-14

Status: **C21 proves that every explicit Hilbert-90 half-divisor for the canonical norm-one twist has linear support and degree, even after fixed-field gauge normalization. C22 extends the negative result to a declared valuation-transparent multiplicative straight-line grammar. In that grammar, the anti-invariant divisor support of the output is contained in the union of the charged supports of its non-fixed leaves. Therefore product trees, multiplicative jump tables, subproduct trees, norm-factor lists, and Miller/division/net product circuits require linear total charged state. Continued fractions, Padé, half-gcd, explicit transposed modular composition, and norm factorization also retain linear representation or orientation cost. No implicit branch-odd evaluator, public jump law, transposed single-value evaluator, parity oracle, or sub-square-root ECDLP algorithm is found. Addition-enabled circuits that create new zeros, compressed resultants or determinants, and a genuinely new public branch-odd anchor remain outside the theorem.**

Only the public seven-curve corpus, six public generator replacements, and public secp256k1 constants are used. No external point with unknown scalar, wallet, private key, or production target is accepted.

## 1. Fixed input from C21

Work in

```text
L = F_p(y),
K0 = F_p(y^2),
tau(y) = -y.
```

C21 constructs the canonical branch-odd norm-one twist

```text
R(y) tau(R)(y) = 1,
R(y) = H(y) / H(-y),
R(infinity) = 1.
```

For every nonzero `tau`-pair `{q,-q}`, write the divisor coefficients of a candidate half-divisor `H` as

```text
u_q = ord_q(H),
v_q = ord_(-q)(H).
```

If the divisor coefficient of `R` at `q` is `s_q`, then

```text
u_q - v_q = s_q.                                (C22.1)
```

A fixed-field gauge `c(y^2)` adds the same coefficient to both entries of every pair and therefore preserves `(C22.1)`.

## 2. Exact half-divisor lower bound

If `s_q` is nonzero, at least one of `u_q,v_q` must be nonzero. Hence every nonzero pair in the anti-invariant divisor of `R` must occur in every Hilbert-90 representative.

Let

```text
P(R) = #{tau-pairs with s_q != 0},
L1(R) = sum_q |s_q|.
```

Then every explicit `H` satisfying `R=H/tau(H)` obeys

```text
boxed:
#pair-support(H) >= P(R),                        (C22.2)

deg_poles(H) >= ceil(L1(R)/2).                  (C22.3)
```

The first bound is invariant under every `K0` gauge. The second follows because distributing a difference `s_q` between the two points costs at least `|s_q|` total absolute divisor mass.

The public corpus reproduces the exact minima found in C21:

| p | n | R support | R poles | minimum H pair support | minimum H poles |
|---:|---:|---:|---:|---:|---:|
| 43 | 31 | 10 | 8 | 5 | 4 |
| 61 | 61 | 20 | 15 | 10 | 8 |
| 67 | 79 | 26 | 20 | 13 | 10 |
| 79 | 67 | 22 | 16 | 11 | 8 |
| 97 | 79 | 26 | 20 | 13 | 10 |
| 127 | 127 | 42 | 32 | 21 | 16 |
| 163 | 139 | 46 | 34 | 23 | 17 |

The same identities are checked for six public generator replacements.

## 3. Valuation-transparent multiplicative Hilbert-90 grammar

The declared grammar has the following leaves:

```text
public rational atoms with charged tau-pair support,
fixed-field gauges in F_p(y^2),
constant-offset translations,
GLV and tau pullbacks,
standard Miller, division-polynomial, and elliptic-net multiplicative leaves.
```

Allowed operations are:

```text
multiplication,
division,
integer powers,
tau pullback,
GLV pullback,
multiplication by fixed-field functions.
```

At divisor level these operations only add, subtract, scale, or permute pair-difference vectors. They do not create support outside the union of the supports already present in the charged non-fixed leaves.

If leaves have pair-difference vectors `g_j` and output vector `s`, then

```text
s = sum_j e_j g_j
```

for public integers `e_j`, after the relevant permutations. Therefore

```text
boxed:
supp(s) subset union_j supp(g_j).                (C22.4)
```

Consequently:

```text
boxed:
sum_j charged_pair_support(g_j) >= P(R).         (C22.5)
```

This proves an `Omega(n)` total support or state lower bound for the declared grammar.

### Covered constructions

The theorem covers:

```text
explicit half-divisor products,
subproduct trees,
multiplicative block or jump tables,
continued-fraction factor products once quotients are materialized,
norm-factor lists,
Miller/division/net product circuits,
black-box block products when block construction support is charged.
```

Balanced trees can reduce depth, but not the charged support union.

### Uncovered constructions

The theorem does not cover:

```text
addition-enabled circuits that create new zeros,
unrestricted resultants or determinants with compressed internal state,
a genuinely new public branch-odd anchor,
an implicit high-degree leaf with independently proved sub-square-root construction.
```

No unrestricted arithmetic-circuit lower bound is claimed.

## 4. Explicit algorithmic routes

### Continued fractions

A rational function of degree `D` has continued-fraction partial quotients whose total degree is `Theta(D)`. Materializing the convergents, their quotient list, or an equivalent factor product therefore has linear charged representation size. Fast evaluation after that representation is built does not remove preprocessing and representation cost.

### Padé reconstruction

Degree-`D` Padé recovery requires `Theta(D)` coefficients, moments, or equivalent linear constraints and outputs `Theta(D)` coefficient data. The route is blocked for explicit reconstruction.

### Half-gcd

Half-gcd can reduce arithmetic time for Euclidean operations on dense degree-`D` polynomials. It does not reduce the input, output, or persistent state below `Theta(D)`.

### Subproduct trees

Each nonzero `tau`-pair must be represented by at least one charged leaf contribution. Product-tree depth may be logarithmic, while total leaf support remains `Omega(n)` by `(C22.5)`.

### Transposed modular composition

Transposition changes the direction of a linear computation but preserves the dimension of the degree-`Theta(n)` module unless a separate compressed oracle is constructed. An explicit transposed module therefore carries linear state.

### Norm-equation factorization

The compact norm determines a quadratic torsor. Choosing a factor on every nonzero `tau`-pair is exactly the half-divisor selection problem. A factorization routine that outputs these choices has linear representation or orientation cost.

### Logarithmic derivatives, residues, and norm derivatives

The quantities

```text
R'/R,
div(R),
residues,
derivatives of R tau(R)
```

are invariant under `R -> -R`. They cannot select the canonical branch unless combined with an independently justified branch-odd anchor.

## 5. Alternative compact factors

Every alternative norm factor has the form

```text
C1 = C0 U,
U tau(U) = 1,
R1 = R/U.
```

If `B=deg_poles(U)`, multiplication or division by `U` can change the point support of `R` at no more than `2B` points. Therefore reducing the twist support below `sqrt(n)` requires

```text
B >= (supp(R)-sqrt(n))/2.                        (C22.6)
```

For secp256k1 the exact lower bound is

```text
19298681539552699237261830834781317975302786196385348165369173219870476143325.
```

It has 254 bits. Hence no bounded-degree, polylogarithmic-degree, or `o(n)`-degree alternative public factor can make the explicit twist sub-square-root.

## 6. Canonical orientation

The normalization

```text
R(infinity)=1
```

is exact and public after the rational class of `R` is known. It fixes the remaining constant sign of an already constructed candidate.

It is not a construction of that class. No public logarithmic-depth jump law was found that propagates the value at infinity to an arbitrary subgroup query without storing or evaluating linear endpoint data.

Rules based only on the compact norm, monicity, denominator normalization, least residue, a canonical finite-field square root, or branch-even derivatives make the same decision for `R` and `-R`. Proving alignment with the endpoint gauge would itself be the missing orientation theorem.

## 7. Public-order recurrence diagnostic

For evidence only, the anti-invariant pair vector was ordered by ascending public `y` representative and passed through exact Berlekamp-Massey over `F_p`.

The observed complexities were:

```text
(p,n,L) =
(43,31,11),
(61,61,15),
(67,79,17),
(79,67,20),
(97,79,24),
(127,127,32),
(163,139,41).
```

These values are nonconstant and grow across the corpus. This is a diagnostic, not a theorem, because the chosen public ordering is not generator invariant and finite recurrence failure cannot exclude another nonlinear representation.

## 8. secp256k1 transfer

The exact C21 lower bounds are:

```text
R point support >=
38597363079105398474523661669562635950945854759691634794201721047172720498104

R pole degree >=
28948022309329048855892746252171976963209391069768726095651290785379540373624

H tau-pair support >=
19298681539552699237261830834781317975472927379845817397100860523586360249052

H pole degree >=
14474011154664524427946373126085988481604695534884363047825645392689770186812
```

For multiplicative leaves whose charged support is capped by `c`, the minimum number of leaves is at least `ceil(P(R)/c)`. For caps `1,2,4,8,16`, the exact lower bounds are respectively:

```text
19298681539552699237261830834781317975472927379845817397100860523586360249052
9649340769776349618630915417390658987736463689922908698550430261793180124526
4824670384888174809315457708695329493868231844961454349275215130896590062263
2412335192444087404657728854347664746934115922480727174637607565448295031132
1206167596222043702328864427173832373467057961240363587318803782724147515566
```

## 9. Formalization

The repaired C20 Lean file formalizes:

```text
paired quadratic identities,
Dickson recurrence,
global sign covariance,
Hilbert-90 coboundary norm one,
fixed-field gauge invariance,
branch-even versus anti-fixed obstruction.
```

The new C21 Lean file formalizes:

```text
pair-difference gauge invariance,
additivity and inversion,
nonzero pair difference implies representative support,
half-divisor support inclusion,
finite cardinal support lower bound,
fixed-field gauge cannot reduce the required pair count.
```

The geometric identification of the abstract pair vectors with the concrete endpoint-gauge divisor remains in deterministic finite-field replay.

## 10. Cost-gate conclusion

No public `H` or implicit evaluator satisfying

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
= O(n^(1/2-epsilon))
```

was found.

The following classes are now blocked with explicit scope:

```text
all explicit half-divisor representations,
fixed-field gauge compression,
continued fractions and Padé with charged representation,
half-gcd over explicit degree-Theta(n) objects,
subproduct and multiplicative jump trees,
explicit transposed modular-composition modules,
norm-factor lists and bounded-degree alternative factors,
valuation-transparent multiplicative Hilbert-90 SLPs,
branch-even derivative, residue, and canonical-root rules.
```

The surviving opening is narrower:

```text
an addition-enabled implicit circuit,
a compressed resultant or determinant,
a genuinely new branch-odd public anchor,
or a public nonlocal jump law whose complete state is o(sqrt(n)).
```

## 11. Flags

```text
exact_norm_one_twist_constructed=true
minimal_half_divisor_linear=true
fixed_field_gauge_compression_blocked=true
explicit_continued_fraction_route_blocked=true
explicit_Pade_route_blocked=true
explicit_half_gcd_route_blocked=true
subproduct_tree_route_blocked=true
explicit_transposed_module_route_blocked=true
bounded_degree_alternative_factor_route_blocked=true
canonical_orientation_without_advice=false
implicit_multiplicative_grammar_lower_bound_proved=true
addition_enabled_implicit_circuit_open=true
compact_public_H_found=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

Replay digest:

```text
3277bed10cc96ae7b0648ca8bdf1c2086d1dddfff060d41fa6311a7393a76d1f
```
