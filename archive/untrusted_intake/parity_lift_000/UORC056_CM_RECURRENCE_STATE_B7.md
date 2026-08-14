# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — CM RECURRENCE STATE B7

Date: 2026-08-14

Status: **the compact CM quotient can transport the underlying order-`n` line-bundle class, but a pullback state is constant on the rational kernel unless one chooses a nontrivial kernel linearization. Every nontrivial one-dimensional linearization is a full order-`n` dual character, and canonical parity has nonzero coefficient at every dual frequency. Standard bounded-state linear CM recurrences therefore do not yield the oriented root.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all-in cost `O(n^(1/2-epsilon))`.

Package B4 identified the parity-oriented degree-zero line bundle

```text
L_G=O_E(Delta_G),
[L_G]=[M]G,
n=2M+1,                                             (B7.1)
```

whose class has exact order `n`. Packages B3 and B6 show respectively that the compact map is kernel-invariant and that the ordinary translation inverse for parity is dense.

## 2. Underlying descent is not the missing orientation

Let

```text
alpha:E -> E'
```

be the compact degree-`n` CM/Frobenius isogeny with kernel `H=<G>`. Pullback on `Pic^0` is the dual isogeny. The class `[M]G` may be transported through this isogeny after choosing a preimage line-bundle class.

But any section pulled back from the quotient satisfies

```text
s(P+T)=s(P),
T in H.                                               (B7.2)
```

It is constant along the kernel orbit and cannot distinguish `Q=[k]G` from any other nonzero kernel point. Compact transport of the underlying line bundle therefore does not provide the marked branch.

## 3. Kernel linearization is the actual missing datum

To obtain a nonconstant scalar state on the kernel one must choose an `H`-linearization. On a one-dimensional state this gives a character

```text
chi_a([k]G)=zeta_n^(a k).                            (B7.3)
```

For prime order `n`:

```text
a=0       -> trivial constant state,
a!=0      -> character of exact order n.             (B7.4)
```

There is no nontrivial `{+1,-1}`-valued character because `n` is odd. Supplying a nontrivial linearization therefore supplies a full dual phase, not one parity bit.

This is the same missing datum seen from the line-bundle descent side rather than the pairing/theta side.

## 4. CM action only permutes the full dual spectrum

The public GLV/CM automorphism acts on scalar labels by a known unit `lambda`. On dual characters it sends

```text
chi_a -> chi_(a lambda).                            (B7.5)
```

Thus a compact combination of `alpha`, its conjugate, Frobenius, and GLV can permute or group dual frequencies. It does not select the absent nontrivial linearization from the public cyclic line alone.

A state invariant under the complete kernel remains constant. A state in one nontrivial eigenline contains the full order-`n` phase.

## 5. Parity requires every dual frequency in the standard linear model

Let `omega` be a primitive `n`-th root and

```text
a(k)=(-1)^k,
0<=k<n.
```

Its Fourier coefficient at frequency `j` is

```text
hat_a(j)=sum_(k=0)^(n-1) (-1)^k omega^(-jk)
        =2/(1+omega^(-j)).                         (B7.6)
```

The denominator never vanishes because an odd-order root of unity cannot equal `-1`. Hence

```text
boxed:
hat_a(j)!=0 for every j mod n.                    (B7.7)
```

Therefore an exact standard linear recurrence/eigenstate representation of parity uses all `n` character directions. A fixed number of CM eigencharacters cannot reproduce `Y_G(x(Q))/y(Q)`.

This restates B6 in the CM spectral basis: changing basis does not reduce exact support.

## 6. Cost consequence

The standard options are:

```text
trivial linearization                    constant on H,
one nontrivial linearization             full zeta_n^(ak) phase,
r bounded linearizations                 r Fourier frequencies,
exact parity                             all n frequencies.
```

For secp256k1, a concrete nontrivial dual point or phase also lives in the previously certified extension of degree `(n-1)/6`. Neither explicit state nor exact full-spectrum representation satisfies the sub-square-root cost gate.

This is a representation-class result. It does not exclude a nonlinear recurrence whose compressed state is not a finite collection of character eigenlines.

## 7. Frozen exact replay

`uorc056_cm_recurrence_state.py` uses the ten frozen prime orders from B4-B6. For every order it constructs an auxiliary finite field containing a primitive `n`-th root and verifies exactly:

1. every nonzero character exponent has exact order `n`;
2. no nontrivial character is binary-valued;
3. all `n` Fourier coefficients of canonical parity are nonzero;
4. the closed formula `2/(1+omega^(-j))` matches the direct transform;
5. GLV-style multiplication by any public unit permutes the frequency set.

No unknown curve point is evaluated.

## 8. Formalization boundary

`Ecdlp/Proved/CmRecurrenceStateBoundary.lean` kernel-checks the absence of a nontrivial sign character on an odd cycle and the canonical wrap contradiction. It does not formalize line-bundle descent, theta groups, CM isogenies, Fourier transforms, secp256k1, parity recovery, or ECDLP.

## 9. Answer for this B-track class

```text
Can the compact quotient transport the underlying line bundle? yes
Is a quotient-pullback state nonconstant on H?                 no
What creates nonconstant kernel states?                        a chosen H-character
Nontrivial one-dimensional character order                     n
Nontrivial bit-valued character                                none
Exact parity Fourier support                                   n
Does bounded-state linear CM recurrence select Y_G?            no
Public parity / absolute EDS oracle                            absent
Sub-square-root ECDLP                                          absent
```

## 10. Strategic successor

The only remaining recurrence escape is nonlinear. The next B package is

```text
UORC056-NONLINEAR-CM-STATE-B8.
```

It will classify finite-dimensional rational state recurrences under public translation/CM actions. A candidate must show how a bounded state generates the unique wrap cut without carrying the scalar, a full dual character, or a state whose representation grows with `n`.
