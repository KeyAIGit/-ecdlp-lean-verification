# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C21: quadratic Hilbert-90 norm-one twist

Date: 2026-08-14

Status: **C20's norm-one twist has exact Hilbert-90 representatives, but every representative has linear divisor and charged representation in the explicit factor-list, dense-coefficient, Padé, continued-fraction, half-gcd, subproduct-tree, explicit modular-composition, and norm-factor-choice grammars. `K0=F_p(y^2)` gauge changes constants but not the exponent. Once the correct Hilbert-90 class is constructed, the remaining global sign is canonically selected without advice by `R(infinity)=1`; this rule does not construct the class. No public `O(n^(1/2-epsilon))` evaluator, parity oracle, or sub-square-root ECDLP algorithm is found.**

Only the public seven-curve corpus, six public generator replacements, and public secp256k1 constants are used.

## 1. Exact formulation

Work in

```text
L=F_p(y), K0=F_p(y^2), tau(y)=-y.
```

C20 gives

```text
M=N_phi(Z),
C0=(y-y([a-1]G))/((y-y(G))(y-y([a]G))(y-y([m]G))),
R=M/C0,
R*tau(R)=1.
```

Hilbert 90 gives

```text
boxed: R=H/tau(H).
```

All solutions are `H -> c(y^2)H`, with `c in K0^*`.

## 2. Minimum half-divisor theorem

Write

```text
div(R)=sum_i s_i([alpha_i]-[-alpha_i]).
```

If the two coefficients of `div(H)` over a nonzero `tau`-pair are `u_i,v_i`, then

```text
u_i-v_i=s_i.
```

Hence `|u_i|+|v_i|>=|s_i|`, and at least one point in every nonzero pair occurs in `div(H)`. Therefore

```text
boxed:
deg_poles(H)>=ceil(deg_poles(R)/2),
#supp div(H)>=number of nonzero tau-pairs.
```

An exact dynamic program constructs minimum witnesses. Results:

| p | n | deg R | support R | poles R | tau pairs | min poles H | min support H |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 43 | 31 | 8 | 10 | 8 | 5 | 4 | 5 |
| 61 | 61 | 15 | 20 | 15 | 10 | 8 | 11 |
| 67 | 79 | 20 | 26 | 20 | 13 | 10 | 13 |
| 79 | 67 | 16 | 22 | 16 | 11 | 8 | 11 |
| 97 | 79 | 20 | 26 | 20 | 13 | 10 | 13 |
| 127 | 127 | 32 | 42 | 32 | 21 | 16 | 21 |
| 163 | 139 | 34 | 46 | 34 | 23 | 17 | 23 |

The pole lower bound is attained on every base curve and public generator replacement.

## 3. `K0` gauge boundary

Multiplication by `c(y^2)` adds the same coefficient to both members of every pair and preserves `u_i-v_i=s_i`. It cannot remove the half-divisor support or pole-degree lower bounds. On the corpus it can reduce one canonical dense degree by about a factor two, but the result remains linear in `n`.

This is a divisor/representation theorem, not an unrestricted arithmetic-circuit lower bound.

## 4. Canonical orientation

Every exact reduced form in the corpus satisfies

```text
R(y)=N(y)/D(y),
D=monic(tau(N)),
R(infinity)=1.
```

With `d=deg N`, set

```text
H_can=N     when d is even,
H_can=yN    when d is odd.
```

Then `H_can` is monic of even order at infinity and

```text
boxed: H_can/tau(H_can)=R.
```

Thus, after the correct Hilbert-90 class is known, no extra sign bit is needed. The competing branch `-R` has value `-1` at infinity. This is a public canonicalization rule, but it needs `N` or an equivalent description of the hard class and therefore is not a compact construction of `H`.

## 5. Algorithmic audit

* Continued fractions have linear total quotient degree.
* Padé reconstruction receives and returns `Theta(deg H)` data.
* Half-gcd accelerates arithmetic on known linear-size polynomial objects but does not shrink them.
* A subproduct tree needs at least one charged leaf per nonzero `tau`-pair.
* Explicit transposed modular composition still uses a degree-`Theta(n)` module/state.
* Norm-equation factorization exposes one binary pair choice for every nonzero `tau`-pair; infinity normalization removes only the final global sign.

No route passes the complete cost gate without a new implicit recurrence or straight-line program.

## 6. Alternative compact factors

Every other factor of the same public norm is

```text
C1=C0*U, U*tau(U)=1, R1=R/U.
```

For pole degree `B=deg_poles(U)`,

```text
boxed: deg_poles(R/U)>=deg_poles(R)-B.
```

A factor can fully cancel at most `B` unit pair contributions and remove at most two support points per canceled pair. Thus bounded- or `o(n)`-degree public factors cannot turn a linear twist into `O(n^(1/2-epsilon))` complexity.

A predeclared screen used products of at most three public atoms `(y-c)/(y+c)` from `{1,a-1,a,m}+{-1,0,1}`. Each atom removed at most one pole degree and one pair in the best cases. The small `p=43` instance drops numerically below `sqrt(n)` after three atoms; this is a finite-size effect and does not contradict the asymptotic theorem.

## 7. secp256k1 transfer

Conservative exact bounds are

```text
R quotient pole degree >=
28948022309329048855892746252171976963209391069768726095651290785379540373624

R quotient support >=
38597363079105398474523661669562635950945854759691634794201721047172720498104

every H pole degree >=
14474011154664524427946373126085988481604695534884363047825645392689770186812

every H support >=
19298681539552699237261830834781317975472927379845817397100860523586360249052.
```

The `H` degree lower bound has 253 bits and its support lower bound has 254 bits.

## 8. Lean and parity status

`Ecdlp/Proved/Uorc056NegationPaired.lean` formalizes the C20 algebraic core: pair identities, root recovery, Dickson recurrence, global-sign covariance, Hilbert-90 coboundaries, fixed-field gauge invariance, and the branch-even obstruction. The nine-point divisor and odd-prism support theorems remain executable rather than fully formalized.

The exact parity-oracle-to-full-scalar reduction is already formalized in `Ecdlp.Proved.ScalarParity`. It is not activated because no compact public `H` has passed the complete cost gate.

## 9. Final flags

```text
exact_norm_one_twist_constructed=true
minimal_half_divisor_linear=true
K0_gauge_sublinear_compression_found=false
canonical_orientation_after_H_class=true
canonical_H_class_from_compact_data=false
explicit_algorithmic_route_subsqrt_found=false
bounded_degree_factor_asymptotic_collapse_found=false
scoped_Hilbert90_representation_lower_bound_proved=true
compact_public_H_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

## 10. Successor

The surviving target is

```text
IMPLICIT-HILBERT90-STRAIGHT-LINE-EVALUATION-072.
```

It must evaluate the canonically normalized value at one public query point without materializing an `Omega(n)` divisor, coefficient vector, factor list, or modular-composition state.
