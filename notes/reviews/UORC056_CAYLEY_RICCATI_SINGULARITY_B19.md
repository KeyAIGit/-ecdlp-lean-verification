# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B19: Cayley-Riccati singularity boundary

Date: 2026-08-14

Status: **the natural nonlinear selector recurrence obtained from the two
polynomial-Pell conjugates is not a new compression mechanism. After a Cayley
change of coordinate it is ordinary multiplicative cocycle transport. Every
regular nonzero multiplier fixes both selector branches `+1` and `-1`
projectively. The canonical `+2` parity dynamics has one nonidentity wrap flip,
so any exact propagation law must pass through a zero, pole, or undefined
projective step. The remaining information is the singular cut itself.**

No external point, private key, wallet, unknown scalar, or production-sized DLP
target is accepted. The executable replay uses only abstract finite-field
algebra and frozen odd cycles.

## 1. Input from B17 and B18

The B17 principal factor is

```text
F_+(P)=A(x(P))+y(P)B(x(P)).
```

Its quadratic conjugate is

```text
F_-(P)=A(x(P))-y(P)B(x(P)).
```

Away from the public exceptional pair, the exact selector is

```text
r(P)=-y(P)B(x(P))/A(x(P)) in {+1,-1}.            (B19.1)
```

B18 proves that a marked seed plus black-box local-edge queries cannot propagate
the global value below linear worst-case cost. B19 tests the most natural
nonlinear escape: propagate the ratio of the two Pell conjugates by a
Möbius/Riccati recurrence.

## 2. Cayley coordinate of the Pell selector

Define the conjugate ratio

```text
z(P)=F_-(P)/F_+(P).                               (B19.2)
```

Using `yB=-rA`, one obtains

```text
F_-=A(1+r),
F_+=A(1-r),
```

and therefore

```text
boxed:
z=(1+r)/(1-r),
r=(z-1)/(z+1).                                   (B19.3)
```

Thus the Pell selector and the conjugate ratio are related by the ordinary
Cayley transform.

## 3. The Riccati update is diagonal multiplication

Let `T=[2]G`. Suppose, on a chart where all values are finite and nonzero,

```text
F_+(P+T)=h_+(P)F_+(P),
F_-(P+T)=h_-(P)F_-(P).                            (B19.4)
```

Then

```text
z(P+T)=c(P)z(P),
c(P)=h_-(P)/h_+(P).                               (B19.5)
```

Applying inverse Cayley gives

```text
boxed:
r(P+T)=
  ((c-1)+(c+1)r(P))
  /((c+1)+(c-1)r(P)).                            (B19.6)
```

Equation `(B19.6)` looks nonlinear, but `(B19.5)` shows that it is only a
projective coordinate change of multiplicative cocycle transport. It carries
no more information than the conjugate local ratio `c(P)`.

The Lean file proves the numerator and denominator identities without division,
so the statement remains valid projectively at poles.

## 4. Regular multipliers cannot flip parity

For `r=+1`, the projective numerator and denominator in `(B19.6)` are

```text
(2c,2c).                                         (B19.7)
```

For `r=-1`, they are

```text
(-2,2).                                          (B19.8)
```

Over a field of odd characteristic, every finite nonzero `c` therefore fixes
both branches:

```text
+1 -> +1,
-1 -> -1.                                        (B19.9)
```

A regular element of `PGL_2` cannot swap the two boundary points in this
diagonal family. A branch flip requires at least one of:

```text
c=0,
c=infinity,
F_+=0,
F_-=0,
an inverse-Cayley denominator equal to zero.      (B19.10)
```

In other words, the useful bit is concentrated at a divisor singularity, not in
the smooth Riccati dynamics.

## 5. The target subgroup lies on the projective boundary

B17 gives `r(Q)=(-1)^k` for every nonexceptional subgroup point. Hence every
such point satisfies exactly one of

```text
F_+(Q)=0,
F_-(Q)=0.                                        (B19.11)
```

Consequently `z(Q)` is always `0` or `infinity`, not an ordinary nonzero field
value. The regular outside-coset Hilbert-90 recurrence cannot simply be
specialized to the subgroup while retaining an invertible multiplier.

This explains why a one-point marked seed does not propagate through the
standard ratio recurrence: the desired output is precisely which conjugate
factor vanishes at the query.

## 6. Exact canonical wrap defect

For the public `+2` step on canonical nonzero scalar labels,

```text
k -> k+2 mod n,
n odd,
```

parity is preserved at every nonidentity transition except

```text
n-1 -> 1.                                        (B19.12)
```

That unique transition flips even to odd because reduction subtracts the odd
modulus `n`.

The smooth multiplier model `(B19.9)` cannot produce this flip. Therefore any
exact Pell-seed propagation mechanism must detect or encode the singular wrap
cut `(B19.12)`, or an equivalent divisor crossing.

This reconnects the nonlinear Pell route to the endpoint/carry bottleneck
without assuming a generic-group representation.

## 7. Frozen exact replay

The executable

```text
experiments/parity_lift_000/uorc056_cayley_riccati_singularity.py
```

uses prime fields

```text
5,7,11,13,17,19,23,29,31
```

and odd cycles

```text
7,11,13,17,19,23,31.
```

It verifies exactly:

1. the projective Cayley numerator and denominator identities;
2. the rational Möbius formula wherever all denominators are nonzero;
3. every nonzero multiplier fixes `+1` and `-1` separately;
4. no regular branch swap occurs;
5. the zero multiplier makes the `+1` projective pair degenerate;
6. every frozen `+2` cycle has exactly one nonidentity parity flip, at `n-1`.

Aggregate totals:

```text
field cases                                  9
cycle cases                                  7
projective identities                    3,345
regular rational updates                2,907
fixed-branch checks                       292
nonidentity cycle transitions             107
parity-preserving transitions             100
wrap flips                                   7
all exact checks                          true
```

No elliptic-curve discrete logarithm is computed.

## 8. Formalization boundary

`Ecdlp/Proved/CayleyRiccatiSingularityBoundary.lean` kernel-checks:

1. Cayley diagonal multiplication gives the Riccati numerator;
2. the same operation gives the Riccati denominator;
3. `+1` is projectively fixed;
4. `-1` is projectively fixed;
5. the two fixed projective pairs are nonzero for regular multipliers in odd
   characteristic.

Lean does not formalize the Pell factors, elliptic divisors, canonical cycle
wrap, secp256k1, parity recovery, or ECDLP. These connections are explicit
premises from B17 and elementary cycle arithmetic.

## 9. Decision

```text
Natural nonlinear Pell selector recurrence                yes
Independent of multiplicative cocycle transport?          no
Regular multiplier flips +1 and -1?                       no
Exact +2 parity dynamics has a wrap flip?                  yes
Where is the missing information?                         singular divisor cut
Does this give a compact cut evaluator?                    no
Public parity oracle                                      absent
Classical sub-square-root ECDLP                            absent
```

## 10. Remaining admitted mechanism

After B19, a positive Pell or Hilbert-90 route cannot be justified by calling
the update nonlinear. The standard Riccati nonlinearity is only Cayley-conjugate
to multiplication and is already covered by the local-cocycle obstruction.

The surviving mechanism must evaluate the singular divisor crossing nonlocally
from public coordinates, for example through a new resultant, CM reciprocity
identity, special function, or direct short arithmetic circuit. It must do so
without walking the cycle, materializing the Pell factor, or storing the cut.

That is exactly the unchanged `UNIFORM-ORIENTED-ROOT-CIRCUIT-056` target.
