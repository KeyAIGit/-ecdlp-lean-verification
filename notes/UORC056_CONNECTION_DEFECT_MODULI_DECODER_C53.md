# UORC-056 C53: connection defect and moduli-tangent decoder boundary

Date: 2026-08-19

Status: exact connection-defect classification, exact charged-neutral tangent normal form, arbitrary-decoder obstruction for the GLV quotient state, bounded nonlinear decoder replay on 16 curves, and a secp256k1 public-sample certificate. No cheap parity decoder, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. Target

Let

```text
E: y^2=x^3+7,
H=<G>, |H|=n,
Q=[k]G,
1<=k<n.
```

The target remains

```text
sigma_G(Q)=(-1)^k.
```

C52 produced a public first-order lift of every prime-to-characteristic torsion point and isolated the genuine `a`-moduli tangent. C53 asks whether a connection defect or a nonlinear decoder of that tangent state supplies the missing endpoint sign.

## 2. Exact connection-defect classification

Trivialize the vertical tangent by the invariant differential. A publicly specified connection along one base direction is then represented by a scalar function `c(P)`. For an integer multiplier `m`, define

```text
delta_m^c(P)=c([m]P)-m c(P).
```

### 2.1 Multiplier cocycle

For public integers `a,b`,

```text
delta_ab(P)=delta_a([b]P)+a delta_b(P).
```

This is an exact algebraic identity, not a statistical observation.

### 2.2 Gauge change

If the connection changes by a vertical gauge `f`, then

```text
delta_m^(c+f)(P)-delta_m^c(P)=f([m]P)-m f(P).
```

Thus the defect changes by a multiplier coboundary.

### 2.3 The trichotomy at the marked generator

At `P=G` and `Q=[k]G`:

```text
delta_k^c(G)=c(Q)-k c(G).
```

There are only three relevant cases.

1. A multiplication-compatible or functorial connection has `delta=0`.
2. If the gauge is anchor-normalized by `c(G)=0`, then

   ```text
   delta_k^c(G)=c(Q).
   ```

   The connection wrapper adds no information beyond the direct public state.
3. If `c(G)!=0` and an exact defect oracle is public, then

   ```text
   k=(c(Q)-delta_k^c(G))/c(G).
   ```

   The oracle reveals the multiplier in the base field. For secp256k1, `0<k<n<p`, so it reveals the full canonical integer scalar, not merely parity.

Therefore an exact connection defect is not an intermediate parity mechanism. It is zero, a renamed public point function, or a full-scalar channel.

## 3. The moduli tangent quotient cannot decode parity

For the genuine `a`-direction write

```text
T=x^3,
R=x dotx_a,
S=x^2 doty_a/y.
```

C52 proved

```text
2(T+7)S=T(3R+1).
```

C53 verifies the exact symmetries

```text
(T,R,S)(-Q)=(T,R,S)(Q),
(T,R,S)(phi Q)=(T,R,S)(Q).
```

Because `n` is odd, `Q=[k]G` and `-Q=[n-k]G` have opposite parity. Hence the same public state occurs with both target signs.

```text
No function, regardless of algebraic degree or nonlinearity, can decode parity from (T,R,S) alone.
```

The three GLV positions do not create a larger state. They are exactly the same quotient value.

## 4. Charged-neutral factorization

The two most informative anchor-normalized tangent states are

```text
OA(Q)=omega_a(Q)/omega_a(G),
OB(Q)=omega_b(Q)/omega_b(G).
```

The `b`-direction is pure scaling:

```text
omega_b(P)=x(P)/(6b y(P)).
```

Therefore

```text
OB(Q)=x(Q)y(G)/(x(G)y(Q)).
```

Also

```text
omega_a(P)=R(P)/(2x(P)y(P)).
```

Multiplying the two normalized states gives

```text
OA(Q)OB(Q)
 = (R(Q)/R(G)) * (y(G)^2/y(Q)^2)
 = (R(Q)/R(G)) * ((T(G)+7)/(T(Q)+7)).
```

The right side is invariant under `Q -> -Q` and `G -> -G`.

This yields the exact normal form

```text
charged tangent pair
 = ordinary endpoint coordinate charge
   times a sign-neutral moduli factor.
```

The deformation supplies new neutral information, but it does not create a new absolute endpoint charge. The only sign-changing factor is already present in the public coordinate ratio `x/y`.

## 5. Bounded nonlinear decoder search

### 5.1 Corpus

The replay uses:

```text
4 frozen curves,
8 C52 held-out curves,
4 new C53 held-out curves.
```

The four new rows are

```text
(p,n)=(1051,1093),
(p,n)=(1237,1279),
(p,n)=(1249,1303),
(p,n)=(1669,1663).
```

Each fixture independently checks:

```text
#E(F_p)=n prime,
ord(G)=n,
beta^3=1 with beta!=1,
lambda^2+lambda+1=0 mod n,
[lambda]G=(beta x(G),y(G)).
```

### 5.2 Scalar states

The replay tests charged or partially charged scalar states including

```text
V,
OA,
D,
P,
UV,
V^3,
U^2V.
```

Every proposed GLV-invariant charged monomial has mixed-parity collisions on the declared corpus. A raw decoder from such a scalar is therefore impossible.

### 5.3 Polynomial decoders of charged pairs

The principal pairs are

```text
(U,V),
(OA,OB).
```

For each curve, C53 solves exact finite-field linear systems for every polynomial decoder of total degree up to the declared bound.

On the smallest curve, the first decoder appears only when ordinary interpolation reaches full row rank:

```text
p=43, n=31:
first degree for (U,V)   =7,
first degree for (OA,OB)=7.
```

Further examples:

```text
p=67,  n=79:  degrees 12 and 11,
p=79,  n=67:  degrees 11 and 11,
p=163, n=139: degrees 16 and 15.
```

No lower-degree structural exception appears. On larger curves no decoder is found within the bounded search.

These are finite representation results, not unrestricted arithmetic-circuit lower bounds.

### 5.4 Character grammar

Across all 16 curves the uniform structural grammar contains 777 declared nonlinear character atoms. Only 3 are everywhere nonzero. Their arbitrary-product span has rank 3 and does not contain parity.

A complete `p=43` nonlinear screen checks 569,800 projective atoms:

```text
bilinear forms in (U,V),
quadratic forms in (U,V),
bilinear forms in (OA,OB),
quadratic forms in (OA,OB),
univariate cubic forms in V, P and UV.
```

Results:

```text
338,986 valid nonzero atoms,
0 exact single survivors.
```

The arbitrary-product span on this one small curve can interpolate parity and is explicitly classified as finite overfit, not a uniform identity.

## 6. Exact replay totals

```text
16 curves
9,726 nonzero torsion rows
9,726 nonzero-anchor defect recovery checks
9,726 anchor-zero direct-state checks
9,726 gauge-coboundary checks
29,178 multiplier-cocycle checks
29,178 quotient-invariance checks
19,452 charged-neutral factorization checks
569,800 complete p=43 nonlinear atoms
0 exact complete-screen survivors
0 arithmetic errors
```

## 7. secp256k1 certificate

For 14 public scalar samples C53 verifies:

```text
14 full-scalar recoveries from an explicitly supplied exact defect,
14 charged-neutral factorizations,
14 GLV tangent covariance checks.
```

This does not provide the defect from public `E,G,Q`. It confirms the classification: once a nonzero-anchor exact defect is granted, the whole scalar is already present.

## 8. Decision

```text
Functorial connection defect                         zero
Anchor-zero connection defect                       direct public state
Nonzero-anchor exact defect                         full multiplier channel
Independent connection-based parity mechanism       absent
Arbitrary decoder from (T,R,S)                      impossible
New charged-neutral factorization                    found
Uniform bounded nonlinear decoder                    absent
Cheap parity decoder                                 absent
Parity oracle                                        absent
Sub-square-root ECDLP                                absent
```

C53 ends in outcome 2 of its contract: a scoped no-go theorem for the declared connection grammar, together with bounded nonlinear decoder closure for the public moduli-tangent states.

## 9. Successor

The next package is

```text
CHARGED-MODULI-TANGENT-TRANSFER-C54.
```

Its target is the surviving charged pair after the exact neutral quotient is removed. It must study:

```text
addition and doubling transfer laws,
GLV orbit factors,
short resultants or recursive orbit products,
minimal state dimension,
endpoint charge beyond the ordinary x/y ratio.
```

A candidate is rejected if it merely repackages the public coordinate charge, uses a scalar-labelled defect, or materializes an order-`n` table.

## 10. Claim boundary

C53 does not claim:

1. an unrestricted lower bound for all nonlinear functions of `(OA,OB)`;
2. an unrestricted arithmetic-circuit lower bound;
3. a parity oracle;
4. a sub-square-root ECDLP algorithm.

It provides an exact connection-defect classification, an exact charged-neutral normal form, an arbitrary-decoder obstruction for the GLV quotient state, deterministic held-out replay, a bounded nonlinear search, and a Lean-formalized algebraic core pending kernel verification.

## 11. Literature anchors

The unique lifting principle used for prime-to-characteristic torsion is the standard formally etale lifting property. The Stacks Project, Theorem 41.16.1, characterizes etale morphisms by unique lifting through square-zero thickenings, and Lemma 58.8.3 gives invariance of finite etale covers under thickenings.
