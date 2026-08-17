# GLOBAL-MONODROMY-SECTION-009

Date: 2026-08-12

Status: **exact global section found on the cyclotomic cover; public Q-only
evaluation not found**.

No external point, key, wallet, or production discrete-log instance is accepted.
The package changes no canonical Research Engine state and makes no
unconditional sub-square-root ECDLP claim.

## 1. Decision

The GLV carry has an exact global monodromy representation.

Let

```text
Q=[k]G,
k0=k,
k1=[lambda*k]_n,
k2=[lambda^2*k]_n,
k0+k1+k2=gamma*n,
gamma in {1,2}.
```

Let `zeta_n=exp(2*pi*i/n)` and define

```text
M_G(Q)=prod_{j=0}^2 (1-zeta_n^kj).
```

Then

```text
M_G(Q)=8*i*(-1)^gamma*prod_{j=0}^2 sin(pi*kj/n),
```

and every sine factor is positive because `0<kj<n`. Therefore

```text
g(Q)=(-1)^gamma=sign(Im M_G(Q)).
```

This answers the existence part positively: the desired absolute phase exists
on a canonical cyclotomic/universal cover once the additive character
`[k]G -> zeta_n^k` is available.

It does not yet give a public decoder from the ordinary point coordinates of
`Q`. Evaluation of `zeta_n^k` is exactly the missing dual-character problem.

## 2. Exact proof

For `0<a<n`,

```text
1-exp(2*pi*i*a/n)
  = -2*i*exp(pi*i*a/n)*sin(pi*a/n).
```

Multiplying the three identities gives

```text
M_G(Q)
  = (-2*i)^3
    * exp(pi*i*(k0+k1+k2)/n)
    * product_j sin(pi*kj/n)
  = 8*i*(-1)^gamma*product_j sin(pi*kj/n).
```

Consequences:

```text
conjugate(M_G(Q))=-M_G(Q),
M_G(phi Q)=M_G(Q),
M_G(-Q)=-M_G(Q).
```

Thus the phase has exactly the required symmetries:

```text
g(phi Q)=g(Q),
g(-Q)=-g(Q).
```

The numerical replay is not the proof. It checks implementation conventions,
root orientation, and all frozen scalar representatives. Across fifteen toy
prime-order GLV groups it performed `14,298` nonzero-scalar checks with zero
phase, purity, GLV-invariance, or anti-Kummer failures.

Artifacts:

- `experiments/parity_lift_000/global_monodromy_section_screen.py`;
- `experiments/parity_lift_000/global_monodromy_section_results.json`.

## 3. The missing public object

The phase becomes public if one can evaluate a nontrivial dual character

```text
chi_T([k]G)=zeta_n^k.
```

A Weil pairing would realize it:

```text
chi_T(Q)=e_n(Q,T),
e_n(G,T)=zeta_n,
```

provided `T` is an independent `n`-torsion point.

The existing GLV orbit cannot supply `T`. Since

```text
phi(Q)=[lambda]Q,
```

alternating bilinearity gives

```text
e_n(Q,phi(Q))=e_n(Q,Q)^lambda=1.
```

Therefore the order-three endomorphism produces no independent pairing
direction. This obstruction is kernel-checked abstractly as
`dependentPairing_trivial`.

## 4. Exact secp256k1 embedding-degree certificate

For the fixed secp256k1 constants,

```text
d=ord_n(p)=(n-1)/6
 =19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

Its exact factorization is

```text
2^5
*149
*631
*107361793816595537
*174723607534414371449
*341948486974166000522343609283189.
```

The replay verifies that every displayed factor is prime,

```text
p^d=1 mod n,
```

and

```text
p^(d/r) != 1 mod n
```

for every prime divisor `r` of `d`. Hence the order is minimal.

Numerically,

```text
log2(d)=253.41503749927884,
log2(sqrt(n))=128.
```

An explicit extension-field representation requiring one base-field
coefficient per basis element is therefore about `2^125.4` times larger than
the square-root operation scale. The ordinary pairing route is not a candidate
for a sub-square-root secp256k1 algorithm.

This is stronger than saying that secp256k1 is not pairing-friendly. It records
the exact extension degree required by `mu_n` for this curve.

## 5. Frobenius descent loses the bit

The certificate also verifies

```text
p^(d/2)=-1 mod n.
```

Thus half-Frobenius acts on an `n`-th root of unity as complex conjugation:

```text
(zeta_n^k)^(p^(d/2))=zeta_n^(-k).
```

For the monodromy phase,

```text
M_G(Q)^(p^(d/2))=M_G(-Q)=-M_G(Q).
```

Consequently:

- traces of odd powers cancel;
- a full norm pairs `M` with `-M` and depends only on a square;
- even powers discard the sign;
- any descent retaining the sign must choose one of the two anti-conjugate
  branches.

Such a branch is precisely the missing orientation. Trace, norm, and ordinary
Frobenius-invariant polynomial combinations do not supply a carry decoder.

## 6. Standard theta-level route

Let `L` be a positive-degree line bundle on an elliptic curve and suppose
translation by the order-`n` point `G` acts on one fixed theta space
`H^0(E,L)`. In the standard algebraic theta-group setting this requires

```text
t_G^*L isomorphic to L,
```

so `G` lies in the theta-group kernel. For a degree-`d_L` line bundle on an
elliptic curve, an element of order `n` in this kernel forces

```text
n divides d_L.
```

Riemann-Roch gives

```text
dim H^0(E,L)=d_L >= n.
```

Therefore the direct proposal

```text
represent translation by G as a small theta matrix and read its binary phase
```

cannot have bounded or polylogarithmic dimension. The conditional arithmetic
lower bound `standardThetaDegree_atLeastOrder` is kernel-checked in Lean. The
geometric admission premise is explicitly outside the Lean formalization.

This does not rule out every nonlinear, compressed, or nonstandard theta
construction. It rules out the ordinary fixed theta-space realization of the
cyclotomic character.

## 7. p-adic route

The formal elliptic logarithm is defined on the formal neighbourhood of the
identity. Prime-to-`p` torsion points reducing to nonidentity points are outside
that formal group, and the global p-adic group logarithm annihilates torsion.

A p-adic realization that retains `zeta_n^k` must instead adjoin `mu_n`. Because
`n` is prime to `p`, this is an unramified cyclotomic extension of the same
degree

```text
ord_n(p)=d.
```

Thus the direct p-adic monodromy realization inherits the same explicit-degree
barrier as the finite-field pairing route. A new compressed continuation with a
public branch and a precision theorem remains outside this decision.

## 8. Ordered-coordinate escape screen

The cyclotomic decoder uses an Archimedean sign, so the closest public
finite-field analogue is not a quadratic character but an order on canonical
integer representatives.

The screen tested

```text
centered_sign(y(Q)),
centered_sign(y(Q)*(x(Q)^3+a)), a in F_p.
```

These functions are outside `C_quad`, GLV-invariant, and anti-Kummer, so they
have exactly the required symmetries for a carry decoder.

Protocol:

```text
15 frozen j=0 prime-order toy subgroups,
orders 19 through 4021,
200 matched random anti-Kummer/C3-invariant controls per case.
```

Results:

```text
exact decoders:                         2
exact decoder at order >=271:           0
cases strictly above matched 95% null:  1
```

The exact decoders occur only at orders `19` and `31`. The single strict
95-percent excursion occurs at order `3469`, has empirical percentile `0.965`,
and does not replicate at order `4021`, where the observed best accuracy is
below the matched null median. Across fifteen tests this is compatible with an
ordinary one-in-twenty excursion.

The fitted family also requires scanning `p` shifts and therefore is not itself
a sub-square-root construction. It supplies no scaling evidence.

Artifacts:

- `experiments/parity_lift_000/ordered_coordinate_carry_screen.py`;
- `experiments/parity_lift_000/ordered_coordinate_carry_results.json`.

## 9. Formalization boundary

`Ecdlp/Proved/GlobalMonodromyCarry.lean` kernel-checks:

```text
cyclotomicHalfAngleCarryParity
complementaryCarry_difference_odd
oddOrderBinaryPhase_trivial
dependentPairing_trivial
antiConjugatePairNorm_signInvariant
antiConjugateTracePair_zero
standardThetaDegree_atLeastOrder
secp256k1EmbeddingDegree_times_six
secp256k1EmbeddingDegree_gt_twoPow253
```

Lean does not formalize:

- positivity of the real sine factors;
- cyclotomic fields or the exact multiplicative-order certificate;
- Weil/Tate pairings;
- theta groups and Riemann-Roch;
- p-adic sigma continuation.

Those claims are separately replayed, derived, or explicitly scoped.

## 10. Exact answer

```text
exact global carry phase on universal/cyclotomic cover:  found
public evaluation from ordinary Q coordinates:           not found
explicit pairing realization below sqrt(n):              ruled out for secp256k1
GLV self-pairing escape:                                  impossible
Frobenius trace/norm sign descent:                        loses the bit
standard fixed theta-space escape:                       dimension at least n
formal-logarithm escape:                                  blocked on prime-to-p torsion
simple ordered-coordinate carry decoder:                  no scaling evidence
public R3 decoder:                                        absent
unconditional sub-square-root ECDLP algorithm:            absent
```

The result is a real narrowing, not a solution claim. The question is no longer
whether a global phase exists. It does. The remaining problem is whether the
dual character can be compressed and evaluated from `Q` without materializing
an extension or theta representation of exponential dimension.

## 11. Constructive successor

The next package is

```text
DUAL-CHARACTER-COMPRESSION-010.
```

Admission requires a construction that computes either

```text
zeta_n^k up to the exact information needed by sign(Im M_G(Q)),
```

or directly computes `g(Q)`, while meeting all of:

1. input only `G,Q` and fixed public curve data;
2. no discrete logarithm in `E[n]` or `mu_n` hidden inside normalization;
3. no explicit object of degree or dimension `Omega(sqrt(n))`;
4. exact branch semantics under `Q -> -Q` and `Q -> phi(Q)`;
5. total online and offline cost below the Pollard square-root baseline;
6. reproducible scaling evidence before any secp256k1 claim.

Any candidate failing one condition is a reformulation, not a decoder.

## Primary anchors

- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*: sigma
  quasi-periodicity, net-polynomial transformation, quadratic scale
  equivalence, and unique normalization.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*: perfectly periodic point functions, EDS residue, adjacent residue
  propagation, and parity-to-ECDLP reduction.
- Repository packages `GLV-NORMALIZATION-RIGIDITY-008`,
  `GLV-CARRY-SEPARATION-005`, and `NONLOCAL-ODD-ANCHOR-004`.
