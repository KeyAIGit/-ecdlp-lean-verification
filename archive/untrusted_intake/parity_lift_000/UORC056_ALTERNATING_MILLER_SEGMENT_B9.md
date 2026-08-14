# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — ALTERNATING MILLER SEGMENT B9

Date: 2026-08-14

Status: **the alternating Miller primitive has an exact endpoint-segment cocycle and associative composition law, but the explicit segment divisor grows linearly with canonical path length. The compact involution norm relates a segment to its reflected partner but does not determine either value. This identifies the exact interface with track A rather than producing a second independent B-track evaluator.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

Package B8 constructs the alternating Miller potential `H_G` and the public two-step edge

```text
c_2(P)=H_G(P+2G)/H_G(P).                           (B9.1)
```

## 2. Exact segment product

For a known nonnegative integer `m`, define

```text
C_m(P)=product_(t=0)^(m-1) c_2(P+2tG).            (B9.2)
```

The product telescopes:

```text
boxed:
C_m(P)=H_G(P+2mG)/H_G(P).                         (B9.3)
```

It satisfies the associative composition law

```text
boxed:
C_(a+b)(P)=C_a(P) C_b(P+2aG).                    (B9.4)
```

Thus a positive endpoint algorithm needs only evaluate `C_m` from the public endpoints, without walking the `m` local edges.

## 3. Explicit divisor support grows with the path

Let `D_H=div(H_G)`. Then

```text
div(C_m)=tau_(-2m)(D_H)-D_H.                     (B9.5)
```

For `1<=m<=M=(n-1)/2`, exact cancellation leaves

```text
boxed:
#supp(div(C_m))=min(2m+2,n).                     (B9.6)
```

The two exceptional high-multiplicity endpoints come from the public correction in `D_H`; the remaining coefficients alternate `+2,-2` across the crossed canonical cut.

Therefore an explicit generalized-Miller divisor list, root list, or product tree for `C_m` has linear size in the shorter canonical segment and reaches size `Theta(n)` near the midpoint.

This is a representation result, not a lower bound against an endpoint-only special-function formula.

## 4. The compact norm gives only a reflected quotient

Let

```text
N(P)=H_G(P)H_G(-P),                              (B9.7)
```

which B8 expresses through ordinary logarithmic-length Miller functions.

For the reflected segment

```text
C_m(-P-2mG)=H_G(-P)/H_G(-P-2mG),                (B9.8)
```

we have

```text
boxed:
C_m(P)/C_m(-P-2mG)=N(P+2mG)/N(P).               (B9.9)
```

The right side is compactly evaluable. But `(B9.9)` is one equation for two reflected segment values. It does not select `C_m(P)`.

The missing factor is again a branch/endpoint primitive, not the generator-blind norm.

## 5. Why ordinary binary splitting is not yet compact

Equation `(B9.4)` permits binary recursion when `m` is known, but a value-only implementation has recurrence

```text
T(a+b)=T(a)+T(b)+public overhead.                 (B9.10)
```

Without a reusable symbolic segment state, balanced splitting still expands to all local leaves.

For the actual input `Q=[k]G`, the integer `m` carrying an anchor to `Q` through steps of `2G` is itself an affine function of `k`. Choosing its canonical midpoint or correction branch is the circularity isolated by the endpoint-segment track.

B9 therefore does not duplicate track A's generic query and checkpoint theorems. It supplies the exact structured Miller cocycle to which a positive A-track primitive must apply.

## 6. Frozen exact replay

`uorc056_alternating_miller_segment.py` uses the ten frozen orders from B8. It verifies:

1. telescoping segment divisors for every `1<=m<=M`;
2. support formula `(B9.6)`;
3. every composition identity `(B9.4)` with `a,b>=1` and `a+b<=M`;
4. reflected norm identity `(B9.9)` at the divisor level;
5. full-cycle closure.

No unknown point or scalar is evaluated.

## 7. Formalization boundary

`Ecdlp/Proved/AlternatingMillerSegment.lean` kernel-checks the abstract telescoping and composition identities for a multiplicative cocycle. It does not formalize Miller functions, divisors, elliptic curves, secp256k1, parity recovery, or ECDLP.

## 8. Answer for this B-track stage

```text
Public fast local edge exists?                              yes
Exact segment composition exists?                          yes
Explicit segment-divisor support                           min(2m+2,n)
Compact norm of segment pair exists?                       yes
Does norm determine one segment value?                     no
Endpoint-only sub-square-root primitive                    not found
Public parity / absolute EDS oracle                        absent
Sub-square-root ECDLP                                      absent
```

## 9. B-track disposition

The kernel-factor route is now cleanly divided:

```text
symmetric kernel and compact-map evaluation          closed,
explicit index/resultant representations             square-root frontier,
linear/transposed CM states                          dense/full-character,
fast alternating Miller local cocycle                obtained,
global endpoint primitive                           handed to track A.
```

The next B-only question must use structure not already present in the local cocycle model. The remaining candidate is a direct nonlinear CM identity evaluating `H_G(Q)` or `Y_G(x(Q))` from `(G,Q)` without representing a path. No such identity is currently known.
