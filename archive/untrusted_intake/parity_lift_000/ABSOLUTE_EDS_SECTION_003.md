# ABSOLUTE-EDS-SECTION-003

Date: 2026-08-11

Status: **isolated, non-executable theorem-first and toy-scaling package**.
This package targets no external point, key, wallet, or production discrete-log
instance. It changes no canonical Research Engine state, authorizes no attack
run, and makes no asymptotic-improvement claim.

## 1. Exact objective

Let `G` generate a prime-order subgroup of odd order `n`, and let

```text
Q = [k]G,     0 < k < n.
```

Write

```text
W_G(k) = psi_k(G),
rho_G(Q) = chi(W_G(k)),
```

where `chi` is the quadratic character.

The remaining parity program asks for a public function of `(G,Q)`, or of
`x(Q)` in the secp256k1 Kummer-invariant case, whose value determines
`rho_G(Q)` in total cost below the matched square-root baseline.

An **absolute EDS section** must satisfy all of the following:

1. it is evaluable from public data without first recovering `k`;
2. it fixes an absolute sign, not only pairwise ratios of residue signs;
3. it is not invariant under the quadratic elliptic-net gauge that leaves all
   standard relative-net identities unchanged;
4. it is not merely a bounded-degree isogeny or coordinate reparameterization;
5. it covers zeros, poles, exceptional points, normalization, and total cost;
6. its exact value gives `rho_G(Q)`, not only a correlation on one finite group.

`RELATIVE-RESIDUE-GAUGE-001` showed that fixed-rank net transport produces
relative labels but leaves one global `+/-1` gauge. The first high-value place
to look for an absolute normalization is therefore the local section of the
full order-`n` torsion divisor itself.

## 2. The order-n torsion jet

For odd `n`, the division polynomial `psi_n(x)` vanishes at every nonzero
`n`-torsion x-coordinate. Although its algebraic degree is approximately
`n^2/2`, its value and a fixed number of derivatives can be evaluated by the
division-polynomial recurrence in a number of field operations polynomial in
`log n`.

Let

```text
D_omega = 2*y*d/dx
```

be the vector field dual to the invariant differential `omega=dx/(2*y)`, and
define the first invariant torsion jet

```text
J_n(P) = D_omega psi_n(P).
```

When the field characteristic does not divide `n`, the `n`-division polynomial
is separable and `J_n(P)` is nonzero at every nonzero `n`-torsion point.

This is the first candidate in the parity line whose defining index grows with
the secret-group order while its evaluation circuit remains logarithmic in the
index. It is therefore not covered by the earlier fixed-index balance result.

## 3. Exact first-jet transport law

The standard multiplication identity is

```text
psi_(n*k)(P)
  = psi_n([k]P) * psi_k(P)^(n^2)
  = psi_k([n]P) * psi_n(P)^(k^2).
```

Differentiate the first expression at `P=G`. Pullback of the invariant
differential under multiplication by `k` contributes a factor `k`.

For the second expression use the standard local parameter

```text
t = -x/y
```

at the identity and the leading term

```text
psi_k = (-1)^(k-1) * k * t^(1-k^2) + higher terms.
```

The two local expansions give the exact identity

```text
J_n([k]G)
  = (-1)^(k-1)
    * n^(1-k^2)
    * J_n(G)^(k^2)
    * psi_k(G)^(-n^2).                       (J)
```

All factors are nonzero under the stated prime-to-characteristic assumptions.

Taking quadratic characters, define

```text
b_G = chi(J_n(G)),
a_G = chi(-n*J_n(G)).
```

Then (J) becomes

```text
chi(J_n([k]G))
  = b_G * a_G^(k-1) * rho_G(Q).              (JC)
```

Compatibility with the raw perfectly-periodic point function gives

```text
a_G = chi(phi_raw(G)).
```

The package checks both the full field identity (J) and the character identity
(JC) at every nonzero scalar on every non-anomalous frozen curve. It also checks
`a_G=chi(phi_raw(G))`.

### secp256k1 consequence

For secp256k1 the existing bridge has

```text
chi(phi_raw(G)) = -1,
chi(phi_raw(Q)) = (-1)^k * rho_G(Q).
```

Therefore

```text
chi(J_n(Q))
  = -b_G * chi(phi_raw(Q)).
```

The first absolute torsion jet is real, public, and fast, but it reconstructs
only the already-public combined EDS/parity factor. It does not separate
`rho_G(Q)` from scalar parity.

On toy instances where `chi(phi_raw(G))=+1`, the same jet can equal a constant
times `rho_G(Q)`. Those residue sequences are anti-invariant under
`Q -> -Q`; the invariant tangent derivative uses the public y-orientation and
does not yield an x-only secp256k1 decoder.

**Disposition:** the first torsion jet is an exact absolute section, but its
normalization collapses to the known public point-function bit.

## 4. Exact near-period collapse

The next natural growing-index sections are `psi_(n+1)` and `psi_(n-1)`
evaluated at `Q=[k]G`.

The multiplication law and the carry across the EDS period give

```text
chi(psi_(n+1)(Q))
  = chi(phi_raw(G))^k * rho_G(Q),

chi(psi_(n-1)(Q))
  = chi(-1) * chi(phi_raw(G))^k * rho_G(Q).
```

Thus both are known public multiples of `chi(phi_raw(Q))`. They do not provide
a second independent equation for the hidden residue.

The package verifies these two identities in `27,504` exact finite-field
character checks.

**Disposition:** the two closest growing-index sections collapse exactly.

## 5. Higher local sections tested

For each nonzero point, expand

```text
psi_n(x(Q)+T)
  = c_1(Q)T + c_2(Q)T^2 + c_3(Q)T^3 + c_4(Q)T^4 + ...
```

and retain every coefficient character that is nonzero on the complete orbit.
The bounded candidate family contains:

```text
chi(c_j(Q)),                    1 <= j <= 4,
chi(psi_(n-a)(Q)),              1 <= a <= 4,
chi(psi_(n+a)(Q)),              1 <= a <= 4,
chi(x(Q)),
```

together with every distinct product of at most four retained candidates.
A public global sign is allowed.

The fixed protocol uses:

```text
15 frozen j=0 toy subgroups on y^2=x^3+7,
orders 19 through 4021,
up to 60 Kummer-invariant generators per case,
200 matched random Kummer-label controls per case.
```

The anomalous case `p=n=547` is excluded from the jet claim because the
order-`p` division polynomial is inseparable in characteristic `p`.

### Exact and statistical results

```text
non-anomalous cases screened:                 14
exact first-jet field checks:             13,752
exact near-period +/-1 checks:             27,504
exact higher-section decoders found:            0
cases above matched 95% null envelope:          0
maximum empirical null percentile:           0.42
```

Largest cases:

| subgroup order | observed best | matched null median | matched null 95% |
|---:|---:|---:|---:|
| 4021 | 0.53980 | 0.54129 | 0.54826 |
| 3469 | 0.53114 | 0.54556 | 0.55248 |
| 1249 | 0.55609 | 0.57532 | 0.58654 |
| 1093 | 0.55311 | 0.57875 | 0.59158 |
| 967  | 0.54037 | 0.58385 | 0.59834 |

The broad candidate selection itself creates apparent correlations above one
half. In every case the real residue target performs no better than the
matched random-label search using the identical candidate and generator pool.
There is no positive scaling signal in the first four torsion jets or the
near-period radius-four family.

Artifacts:

- `experiments/parity_lift_000/absolute_eds_section_screen.py`;
- `experiments/parity_lift_000/absolute_eds_section_results.json`.

## 6. What this closes

The package now separates three kinds of section.

### Relative net section

```text
public pairwise residue ratios
```

These leave one global sign gauge, as proved in
`RELATIVE-RESIDUE-GAUGE-001`.

### Fixed isogeny or root-cover section

```text
public coordinate on an isogenous copy of the same prime-order group
```

The canonical Eisenstein cubic root was shown in
`EISENSTEIN-COVER-ISOGENY-002` to be exactly an inverse 3-isogeny
reparameterization.

### Full torsion-divisor local section

```text
local jet of psi_n at Q
```

This class is genuinely order-dependent and efficiently evaluable. Its first
jet has now been solved exactly and collapses to the known point-function bit.
The first four higher x-jets and nearby order-dependent sections show no
positive cross-order signal.

This is not a universal no-go for every function derived from `psi_n`. It is a
closure of the first local-jet layer and a bounded negative for the next three
jets plus the nearest period sections.

## 7. p-adic sigma boundary

A Mazur-Tate or related p-adic sigma function is an attractive source of an
absolute normalization because it is defined by a differential equation and a
chosen invariant differential rather than by arbitrary net scaling.

The immediate obstruction is domain rather than existence:

1. the formal logarithm and formal sigma naturally live in the formal
   neighbourhood of the identity;
2. the secp256k1 subgroup has order prime to `p` and its nonzero points are not
   in the formal kernel;
3. multiplying such a point by its order sends it to the identity but does not
   give an invertible path back through the formal group;
4. extending sigma globally requires choices of lift, divisor, or analytic
   continuation, where the same absolute gauge can reappear.

No p-adic impossibility theorem is claimed here. A viable proposal must give an
explicit global evaluation map for arbitrary rational `Q`, an exact precision
bound, a branch-independent binary output, and total cost below square root.
A formal-group power series alone does not satisfy those requirements.

## 8. Current answer

The package found an important positive structural object but a negative
cryptanalytic result:

```text
fast absolute order-n section exists:             yes
first torsion jet understood exactly:             yes
first jet isolates rho_G:                         no
near-period n+/-1 sections isolate rho_G:          no
higher local jets show positive scaling:           no
sub-square-root EDS-residue decoder:                absent
```

The central question remains open, but the next bottleneck is no longer
“find any absolute normalization.” Such a normalization exists. The bottleneck
is:

> Find an absolute section whose transformation law contains an odd,
> non-public residue factor after all local torsion, period-carry, isogeny, and
> quadratic-gauge normalizations are removed.

The highest-value successor is provisionally named

```text
NONLOCAL-ODD-ANCHOR-004.
```

It should admit only mechanisms that are not determined by a fixed local jet,
a bounded isogeny pullback, or a pairwise net graph. Candidate classes are a
nonlocal relation with an odd number of absolute residue factors, a global
theta monodromy section, or a p-adic sigma continuation with a complete public
evaluation and precision theorem.

## 9. Completion metric

These percentages measure completion of this package, not distance to solving
ECDLP.

| obligation | completion |
|---|---:|
| define an admissible absolute EDS section | 100% |
| derive the exact first-torsion-jet law | about 95% |
| exhaustive frozen replay of the first-jet law | 100% |
| derive and replay the `n+/-1` collapse | 100% |
| bounded higher-jet and near-period scaling screen | 100% |
| source-pinned formal proof of the local leading-term derivation | about 50% |
| p-adic global-evaluation construction | 0% |
| actual sub-square-root residue decoder | no positive evidence |

## Primary mathematical anchors

- Standard division-polynomial multiplication identities and local leading
  terms at the identity.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*, for the perfectly periodic point function and residue bridge.
- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*, for quadratic net
  equivalence and transformation laws.
- Barry Mazur and John Tate's p-adic sigma construction, together with later
  universal p-adic sigma treatments, for the remaining analytic section class.
