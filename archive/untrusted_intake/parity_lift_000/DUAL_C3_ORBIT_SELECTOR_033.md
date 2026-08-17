# DUAL-C3-ORBIT-SELECTOR-033

Date: 2026-08-12

Status: **exact Frobenius-orbit classification and scoped field-of-definition obstruction for the dual selector required by the normalized-period blackbox**.

No external point, private key, wallet, or production-sized discrete-log target is accepted. This package constructs no public carry, R3, parity, or ECDLP decoder.

## 1. Input from package 032

For a cyclic subgroup

```text
H=<G>,  |H|=n,
```

the normalized carry observable has the exact pairing form

```text
U_G(Q)=product_(j=0..2)
  (1-e_n([lambda^j]Q,T))/(1-e_n([lambda^j]G,T)),
```

provided an independent dual `n`-torsion point `T` is supplied and normalized by a faithful pairing phase.

Changing `T` by a nonzero scalar `a` replaces `U_G` by `U_a`. The unit subgroup

```text
C6={plus_or_minus 1, plus_or_minus lambda, plus_or_minus lambda^2}
```

does not change the normalized function, so the raw selector space is

```text
(F_n^*)/C6,
```

of size `(n-1)/6`.

## 2. Frobenius eigenspace decomposition

Let the curve be ordinary over `F_p`, and assume `n=#E(F_p)` is prime and `n` does not divide `p(p-1)`. Modulo `n`, the Frobenius characteristic polynomial factors as

```text
X^2-tX+p=(X-1)(X-p),
```

because `n=p+1-t`.

Thus `E[n]` has two distinct Frobenius eigendirections:

```text
H              : eigenvalue 1;
H_dual         : eigenvalue p mod n.
```

The public rational subgroup is `H`. A pairing-independent dual point lies in `H_dual` and satisfies

```text
Frob(T)=[p]T.
```

The rational GLV endomorphism preserves both eigendirections. Under the principal polarization, the order-three eigenvalue on the dual line is the inverse of the eigenvalue on `H`; this changes `lambda` to `lambda^2` but leaves the subgroup `C6` unchanged.

## 3. Exact field-of-definition obstruction

Let

```text
d=ord_n(p).
```

For a nonzero point `T in H_dual`,

```text
Frob^m(T)=T
iff
p^m=1 mod n.
```

Therefore the smallest extension over which a nonzero dual point can be rational has degree exactly `d`.

More generally, the unordered `C3` orbit of `T` is defined over degree equal to the least positive `m` with

```text
p^m in C3,
```

and the `plus_or_minus C3` orbit is defined over degree equal to the least positive `m` with

```text
p^m in C6.
```

Consequently, a standard algebraic procedure over a smaller field cannot output the required dual point or orbit. This is a field-of-definition statement, not a circuit lower bound against symbolic or implicit representations.

## 4. secp256k1 arithmetic

For secp256k1 the exact arithmetic certificate is

```text
d=ord_n(p)=(n-1)/6,
p^(d/2)=-1 mod n,
d=4 mod 6.
```

Since `3` does not divide `d`, the Frobenius subgroup contains no nontrivial element of `C3`. Since `d` is even and half-Frobenius is `-1`,

```text
< p > intersect C6={plus_or_minus 1}.
```

It follows that:

```text
nonzero dual point field degree      d       =(n-1)/6;
C3-orbit field degree                d       =(n-1)/6;
plus_or_minus C3-orbit field degree  d/2     =(n-1)/12.
```

The exact secp256k1 values are

```text
d=
19298681539552699237261830834781317975472927379845817397100860523586360249056,

d/2=
9649340769776349618630915417390658987736463689922908698550430261793180124528.
```

Thus even selecting one unordered dual `plus_or_minus C3` orbit by an ordinary explicit extension representation is still roughly a `2^252.4`-degree task.

## 5. Frobenius reduces the quotient to two large orbits, not one point

The quotient

```text
(F_n^*)/C6
```

has size `d`. The Frobenius class `p*C6` has order `d/2`, because half-Frobenius equals `-1`, which is already trivial in the quotient. Therefore Frobenius has exactly two orbits on the dual selector quotient, each of size `d/2`.

Equivalently,

```text
< p > C6
```

has size `(n-1)/2`. Since the square subgroup is the unique index-two subgroup of `F_n^*`, one obtains

```text
< p > C6=(F_n^*)^2.
```

Hence the two Frobenius orbits correspond to square and nonsquare scalar classes on the dual torsor.

This is a useful reduction, but it does not select the distinguished class `a=1`. Inside the square orbit remain `d/2` different normalized functions

```text
U_a(k)=M_a(k)/M_a(1).
```

Frobenius sends `U_a` to `U_(p*a)` rather than fixing `U_a` pointwise.

## 6. Best fully symmetric collapse

Multiplying over every dual class loses all information, as package 032 proved. Multiplying only over one of the two Frobenius orbits yields at most the quadratic class of the scalar index:

```text
k square      -> the square orbit is permuted;
k nonsquare   -> square and nonsquare orbits are exchanged.
```

Thus a full Frobenius/CM-symmetric two-orbit resolvent can encode at most a scalar Legendre-class bit. It cannot equal GLV carry, because for secp256k1

```text
Legendre(-k)=Legendre(k),
g_G(-Q)=-g_G(Q).
```

A carry decoder therefore must orient a specific Galois conjugate inside a large Frobenius orbit, or introduce a separate public anti-invariant datum.

This observation does not rule out using a scalar Legendre oracle in a different hidden-shift reduction. No such sub-square-root classical reduction is established here.

## 7. Scoped answer

```text
Is the complementary Frobenius eigendirection canonical?          yes
Is a nonzero point on it rational over F_p?                        no
Minimum explicit point field degree on secp256k1                   (n-1)/6
Minimum explicit plus/minus-C3 orbit degree                        (n-1)/12
Does Frobenius reduce all orbit choices to one?                    no, to two large orbits
Does full Frobenius/CM symmetry recover carry?                     no
Does it expose at most a square/nonsquare scalar class?            yes
Public exact dual-orbit selector                                   absent
Public carry / hard-R3 decoder                                     absent
Unconditional classical sub-sqrt ECDLP algorithm                   absent
```

The standard CM/polarization route therefore has the following scoped obstruction:

> Public kernel and Frobenius data canonically identify the complementary eigendirection, but they do not canonically choose the faithful dual character needed by `U_G`. A specific dual `plus_or_minus C3` orbit has extension degree `(n-1)/12`, while Frobenius-symmetric aggregation loses the negation-odd carry orientation.

## 8. Next object

The successor is

```text
DUAL-ORBIT-QUADRATIC-RESOLVENT-034.
```

Its exact object is the two-orbit product

```text
L_G(Q)=product_(a in square dual orbit) U_a(k),
Q=[k]G.
```

Central questions:

1. derive the exact two values of `L_G(Q)` for square and nonsquare `k`;
2. determine whether `L_G` has a compact base-field/resultant expression;
3. determine whether an exact oracle for the scalar Legendre class under additive shifts `Q+[a]G` yields a classical `o(sqrt(n))` hidden-shift algorithm;
4. otherwise prove a scoped obstruction for standard symmetric norm/resultant representations.

This package is admitted because it follows from an exact Frobenius-orbit identity, not from a broad statistical search.

## 9. Formalization boundary

`Ecdlp/Proved/DualC3OrbitSelector.lean` formalizes the elementary field statement that a nontrivial scalar eigenaction cannot fix a nonzero vector and that an even decoder cannot equal a negation-odd target on both members of a pair.

The Frobenius eigenspace decomposition, secp256k1 multiplicative-order certificate, CM dual-eigenvalue identification, and extension-degree interpretation remain explicit mathematical premises outside the Lean core.
