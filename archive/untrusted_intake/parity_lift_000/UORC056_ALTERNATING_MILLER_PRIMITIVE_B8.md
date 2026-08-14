# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — ALTERNATING MILLER PRIMITIVE B8

Date: 2026-08-14

Status: **the giant oriented half-divisor admits an exact alternating Miller-product realization. Its product with the complementary parity factor, its involution norm, and its two-step translation ratio all reduce to ordinary logarithmic-length Miller data. The unresolved task is now the absolute integration of one fast public two-step cocycle, not construction of the full kernel polynomial.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with complete cost below `n^(1/2-epsilon)`.

Let `n=2M+1` and let `g_(R,G)` be the standard Miller line quotient with divisor

```text
div(g_(R,G))=(R)+(G)-(R+G)-(O).                 (B8.1)
```

## 2. Alternating Miller product

Define

```text
H_G(P)=product_(j=1)^M g_([(2j-1)]G,G)(P).       (B8.2)
```

Summing the line divisors gives

```text
boxed:
div(H_G)=-Delta_G+M(G)-M(O),                    (B8.3)
```

where `Delta_G` is the even-minus-odd oriented half-divisor from B4.

Let the ordinary Miller function satisfy

```text
div(f_(m,G))=m(G)-([m]G)-(m-1)(O).              (B8.4)
```

Then

```text
boxed:
div(f_(M,G)/H_G)
 =Delta_G-([M]G)+(O).                            (B8.5)
```

Thus `f_(M,G)/H_G` is an exact principalization of the oriented half-divisor with one public exceptional point `[M]G`. Away from `O` and `[M]G`, its local order is

```text
+1 for even canonical scalar,
-1 for odd canonical scalar.                    (B8.6)
```

The exceptional point is public and can be recognized directly; its parity is the public parity of `M`.

This is a second exact realization of the same marked root encoded by `Y_G`.

## 3. Complementary product and full Miller function

Define the complementary product

```text
J_G(P)=product_(j=1)^M g_([2j]G,G)(P).           (B8.7)
```

Its divisor is

```text
div(J_G)=Delta_G+(M+1)(G)-(M+1)(O).             (B8.8)
```

The two products partition all Miller edges, hence with the standard recurrence normalization

```text
boxed:
H_G(P)J_G(P)=f_(n,G)(P).                         (B8.9)
```

The full degree-`n` Miller function is fast, but `(B8.9)` does not choose which parity factor is `H_G`.

## 4. Compact involution norm

Pulling `H_G` back by negation gives

```text
div(H_G(-P))=Delta_G+M(-G)-M(O).                (B8.10)
```

The ordinary Miller ratio

```text
F_G(P)=f_(M+1,G)(P)/f_(M,-G)(P)                 (B8.11)
```

has divisor

```text
(M+1)(G)-M(-G)-(O).                              (B8.12)
```

Therefore

```text
J_G(P)=c_G H_G(-P)F_G(P)                         (B8.13)
```

for one nonzero public normalization constant `c_G`, and

```text
boxed:
H_G(P)H_G(-P)
 =c_G^(-1) f_(n,G)(P) f_(M,-G)(P)/f_(M+1,G)(P). (B8.14)
```

Every factor on the right is an ordinary Miller function with logarithmic-length addition chain. Thus the generator-blind norm of the alternating primitive is compactly evaluable. The missing information is exactly its signed factor.

## 5. Compact two-step translation cocycle

Because translation by `2G` preserves parity labels except at the canonical wrap, the divisor difference is supported on only four public points:

```text
boxed:
div(H_G(P+2G)/H_G(P))
 =(M+2)(-G)
 -(M+1)(-2G)
 -M(G)
 +(M-1)(O).                                      (B8.15)
```

The divisor has degree zero and group sum zero. It is therefore principal and can be evaluated by a generalized Miller addition chain whose scalar coefficients have `O(log n)` bits.

Consequently the alternating primitive satisfies a public first-order two-step cocycle

```text
H_G(P+2G)=c_2(P)H_G(P),                          (B8.16)
```

where `c_2(P)` is compact Miller data.

## 6. What this does and does not solve

The local transition `(B8.16)` is public and fast. But to obtain `H_G(Q)` from one anchor one must integrate it through the unknown number of two-step translations carrying the anchor to `Q=[k]G`.

Since `2` is invertible modulo odd `n`, the two-step orbit is the whole subgroup. The unknown path length is an affine function of the unknown scalar `k`.

Thus B8 gives a positive structural reduction:

```text
giant oriented Kummer factor
 -> alternating Miller potential H_G
 -> public O(log n) two-step edge cocycle
 -> one missing absolute anchor/global segment value.          (B8.17)
```

This is exactly the structured endpoint-segment problem assigned independently to track A. B8 does not claim that integrating this structured cocycle requires linear or square-root work; it supplies the concrete Miller cocycle on which a positive segment algorithm would operate.

## 7. Frozen exact replay

`uorc056_alternating_miller_primitive.py` uses the ten frozen cofactor-one prime orders from B2-B7 and verifies the divisor coefficient identities:

1. `(B8.3)` for every alternating edge;
2. principalization `(B8.5)`;
3. complementary divisor `(B8.8)`;
4. full product `(B8.9)` at the divisor level;
5. involution relation `(B8.13)` and norm `(B8.14)`;
6. four-point two-step cocycle divisor `(B8.15)`;
7. parity of every nonexceptional local order.

No unknown target is evaluated.

## 8. Formalization boundary

`Ecdlp/Proved/AlternatingMillerPrimitive.lean` kernel-checks the degree and scalar-class arithmetic of the principalization, norm correction, and two-step divisor. It does not formalize function fields, Miller algorithms, elliptic curves, secp256k1, parity recovery, or ECDLP.

## 9. Answer for this B-track stage

```text
Exact compact potential representation found?               yes, alternating Miller product
Is its full product with the complement fast?                yes, f_(n,G)
Is its involution norm fast?                                 yes, ordinary Miller ratio
Is its two-step edge fast?                                   yes, generalized Miller divisor
Is the absolute potential at arbitrary Q known?              no
Public parity / absolute EDS oracle                          absent
Sub-square-root ECDLP                                        absent
```

## 10. Strategic successor

B no longer needs another symmetric kernel representation. The immediate successor is

```text
UORC056-ALTERNATING-MILLER-SEGMENT-B9.
```

It will derive exact composition laws for products of the two-step cocycle over a segment, compare them with the endpoint-segment work in track A, and test whether the compact norm `(B8.14)` supplies a branch-sharing invariant that prevents binary path expansion.
