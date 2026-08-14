# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B20: Pell singular cut equals the translated endpoint factor

Date: 2026-08-14

Status: **the singular divisor cut isolated by B19 is not a new orientation
object. Away from one fully public common-root pair, the plus polynomial-Pell
factor vanishes exactly on the canonical even half and the minus factor exactly
on the odd half. The homogeneous translated endpoint factor gives the same
classification and remains total at the public pair where both Pell conjugates
vanish. Thus Pell factor selection, Cayley-Riccati singularity detection, and
the translated endpoint idempotent are three representations of the same
parity cut.**

No external point, private key, wallet, unknown scalar, or production-sized DLP
target is accepted. The executable replay uses only the ten frozen B7A curves
and fixed public secp256k1 integers.

## 1. Input from B7A and B19

Let

```text
F_+(P)=A(x(P))+y(P)B(x(P)),
F_-(P)=A(x(P))-y(P)B(x(P)).                      (B20.1)
```

B7A gives, away from the fully public exceptional pair,

```text
r_G(Q)=-y(Q)B(x(Q))/A(x(Q))=(-1)^k,
Q=[k]G.                                           (B20.2)
```

B19 applies the Cayley transform to this selector and proves that every regular
nonzero local multiplier fixes the two selector branches separately. A parity
change can therefore occur only when a conjugate factor vanishes, blows up, or
the projective update is undefined.

B20 identifies that singular support exactly.

## 2. Which Pell conjugate vanishes

Write

```text
s=(-1)^k.
```

Equation `(B20.2)` is equivalent to

```text
y(Q)B(x(Q))=-s A(x(Q)).                          (B20.3)
```

Substitution into `(B20.1)` gives

```text
F_+(Q)=A(x(Q))(1-s),
F_-(Q)=A(x(Q))(1+s).                              (B20.4)
```

Therefore, whenever `A(x(Q))` is nonzero,

```text
s=+1  ->  F_+(Q)=0, F_-(Q)=2A(x(Q)) != 0,
s=-1  ->  F_-(Q)=0, F_+(Q)=2A(x(Q)) != 0.        (B20.5)
```

Thus the plus factor is the even-half zero factor and the minus factor is the
odd-half zero factor. The apparent Riccati nonlinearity has reduced to a
zero-membership test in one of the two conjugate divisors.

Over `F_p`, outside exceptions, either factor gives the exact idempotent
formula

```text
(-1)^k = 1-2 F_+(Q)^(p-1)
       = 2 F_-(Q)^(p-1)-1.                       (B20.6)
```

This does not make evaluation cheap. It only identifies the exact branch
functional.

## 3. The public common-root pair

Recall

```text
S_G=[-4^(-1)]G,
A_G=[4^(-1)]G.                                    (B20.7)
```

The factor `F_+` has zeros at the even half and at the anchor `A_G`. Its
conjugate `F_-` has zeros at the odd half and at `S_G`.

The two factors vanish simultaneously exactly when

```text
S_G has an even canonical scalar,
A_G has an odd canonical scalar.                  (B20.8)
```

For an odd prime order this occurs precisely in the residue classes

```text
n mod 8 in {1,3}.                                 (B20.9)
```

In those cases `A(X)` and `B(X)` have the common linear factor

```text
X-x(S_G)=X-x(A_G).                                (B20.10)
```

In the other residue classes the anchor lies in the same parity half as its
factor and creates a doubled zero rather than a common zero.

For secp256k1,

```text
n=1 mod 8,
S_G=[(n-1)/4]G has even scalar,
A_G=[(3n+1)/4]G has odd scalar.                   (B20.11)
```

Hence the Pell selector is `0/0` at exactly these two public points, and the
common polynomial gcd has exact degree one. This sharpens the `deg gcd<=1`
certificate used by the continued-fraction companion package.

## 4. Homogeneous translated endpoint factor

Put

```text
m=(n-1)/2,
T=[2^(-1)]G,
J_m={j:1<=j<=m, j=m mod 2},
eta_m=1 if m is even and 0 otherwise.             (B20.12)
```

Define

```text
P_G(U,V)
 =V^eta_m product_(j in J_m)(U-x([j]G)V).        (B20.13)
```

For the Kummer lift

```text
kappa(P)=(x(P):1) for P!=O,
kappa(O)=(1:0),                                   (B20.14)
```

the translated factor satisfies on every nonzero subgroup point

```text
boxed:
P_G(kappa(Q+T))=0 iff k is even.                  (B20.15)
```

Consequently

```text
boxed:
(-1)^k=1-2 P_G(kappa(Q+T))^(p-1).                (B20.16)
```

Unlike the Pell quotient, `(B20.16)` remains total at `S_G` and `A_G`. The
homogeneous factor contains the projective endpoint normalization that the
Cayley ratio loses when both conjugates vanish.

## 5. Exact equivalence of mechanism classes

Away from the public pair,

```text
P_G(kappa(Q+T))=0
iff F_+(Q)=0
iff k is even,                                    (B20.17)
```

and

```text
F_-(Q)=0
iff k is odd.                                     (B20.18)
```

At the common pair, both Pell factors vanish, while the endpoint factor still
distinguishes the even point from the odd point.

Therefore the following proposals are not independent routes:

```text
choose the distinguished Pell conjugate,
detect the Cayley-Riccati singular branch,
detect the translated endpoint quarter-kernel,
evaluate the canonical even-half divisor.         (B20.19)
```

They all require the same global generator-oriented cut. Passing from one
representation to another does not lower the charged complexity.

## 6. secp256k1 quarter form

Because secp256k1 has `n=4N+1`, equation `(B20.13)` becomes

```text
P_G(U,V)
 =V product_(r=1)^N (U-x([r](2G))V),
N=(n-1)/4.                                        (B20.20)
```

Thus the final live endpoint problem is still single-value evaluation of one
quarter-length elliptic product at

```text
(U:V)=kappa(Q+[2^(-1)]G).                         (B20.21)
```

The standard block evaluator costs soft `sqrt(n)`. E1 proves that no generic
collision implementation can improve that exponent. B17-CF proves that the
standard explicit Pell continued fraction is linear in degree. B19 and B20
show that ordinary local nonlinear propagation merely returns to the same
singular endpoint cut.

## 7. Frozen exact replay

The executable

```text
experiments/parity_lift_000/uorc056_pell_endpoint_singular_equivalence.py
```

reconstructs the ten B7A principal factors and verifies:

1. the common polynomial factor occurs exactly for `n mod 8 in {1,3}`;
2. its degree is one in those cases and zero otherwise;
3. outside the public pair, `F_+` vanishes exactly on even scalars;
4. outside the public pair, `F_-` vanishes exactly on odd scalars;
5. both Pell factors vanish exactly at the predicted public pair;
6. the homogeneous translated endpoint factor vanishes exactly on every even
   scalar, including the exceptional point;
7. all three Fermat idempotent formulas agree wherever defined.

Exact aggregate totals:

```text
cases                                      10
nonzero endpoint checks                 1,092
ordinary Pell checks                    1,086
public 0/0 pair checks                       6
common-factor cases                         3
total common polynomial degree              3
largest order                              313
all exact checks                          true
```

No unknown-target discrete logarithm is computed.

## 8. Formalization boundary

`Ecdlp/Proved/PellEndpointSingularEquivalenceBoundary.lean` kernel-checks:

1. the plus factor vanishes on the even selector relation;
2. the minus conjugate is then `2A`;
3. the minus factor vanishes on the odd selector relation;
4. the plus conjugate is then `2A`;
5. away from `A=0`, the two factors cannot vanish together in odd
   characteristic.

Lean does not formalize the elliptic divisor, the `n mod 8` classification,
the translated endpoint product, secp256k1, parity extraction, or ECDLP. These
connections are verified by exact finite arithmetic and the preceding B7A
identities.

## 9. Decision

```text
Pell plus-factor zero set                              canonical even half
Pell minus-factor zero set                             canonical odd half
Common Pell zero pair                                  public, iff n mod 8 in {1,3}
secp256k1 common gcd degree                            exactly 1
Translated endpoint factor handles public pair         yes
Cayley singular cut distinct from endpoint cut?         no
New sub-square-root mechanism obtained?                 no
Public parity oracle                                   absent
Classical sub-square-root ECDLP                         absent
```

## 10. Remaining constructive target

The representation ambiguity has now been removed. A positive result must
provide a genuinely faster application algorithm for the same endpoint object:

```text
V product_(r=1)^((n-1)/4)(U-x([r](2G))V)
```

at one public query point, with all preprocessing, advice, state, memory,
precision, and online work below `n^(1/2-epsilon)`.

Equivalent formulations through Pell factors or singular Riccati propagation
are acceptable only if they exhibit a new non-generic operation that changes
the exponent. Renaming the cut is no longer progress.
