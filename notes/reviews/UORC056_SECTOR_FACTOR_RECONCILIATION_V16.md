# UORC-056 sector factor reconciliation V16

## Status

This package is stacked on V15 and keeps the central target unchanged:

\[
\frac{Y_G(x([k]G))}{y([k]G)}=(-1)^k.
\]

It does not construct a public parity evaluator, a sub-square-root ECDLP
algorithm, or an unrestricted arithmetic-circuit lower bound.

V16 has three purposes:

1. identify the V15 carry with the legacy direct-GLV carry line;
2. put the Kummer sector involution into an exact binary/four-branch factor
   and CRT normal form;
3. compute the exact secp256k1 sign-fiber cardinalities and the resulting
   direct field-valued rational degree barrier.

## Exact reconciliation with the legacy GLV line

For

\[
s_0=\sigma(Q),\qquad
s_1=\sigma(\alpha Q),\qquad
s_2=\sigma(\alpha^2 Q),
\]

V15 defines

\[
c=s_0s_1s_2,\qquad
J_G(x(Q))=s_1s_2.
\]

Let \(k_0,k_1,k_2\) be the canonical representatives of

\[
k,\quad \lambda k,\quad \lambda^2k
\]

in \(\{1,\ldots,n-1\}\). Since

\[
k_0+k_1+k_2=\gamma n,\qquad \gamma\in\{1,2\},
\]

the old carry is

\[
g_G(Q)=(-1)^\gamma.
\]

The parity product gives exactly

\[
\boxed{c=g_G(Q).}
\]

Thus V15 did not create a second carry observable. It recovered the existing
one in the threefold oriented-root decomposition.

With the established point-function/EDS bridge

\[
\sigma(P)=C_G(P)\rho_G(P),
\]

the orbit product becomes

\[
\boxed{
c=C3_G(Q)R3_G(Q)=g_G(Q).
}
\]

The sector is different from \(R3_G\). Its exact forms are

\[
\boxed{
J_G(x(Q))=\sigma(Q)g_G(Q),
}
\]

\[
\boxed{
J_G(x(Q))
=
C_G(\alpha Q)C_G(\alpha^2Q)
\rho_G(\alpha Q)\rho_G(\alpha^2Q),
}
\]

and

\[
\boxed{
J_G(x(Q))
=
\sigma(Q)C3_G(Q)R3_G(Q).
}
\]

Therefore \(J_G\) is the complementary two-rotation product. It is not the old
\(R3_G\), and it is not obtained from \(R3_G\) by one known public correction
alone.

## Binary factor and CRT normal form

On the half-kernel roots of

\[
K_H(X)=\prod_{j=1}^{(n-1)/2}(X-x([j]G)),
\]

the sector involution satisfies

\[
J_G(X)^2=1\pmod {K_H(X)}.
\]

Define the two sign factors

\[
K_{G,+}(X)
=
\prod_{J_G(x([j]G))=+1}
(X-x([j]G)),
\]

\[
K_{G,-}(X)
=
\prod_{J_G(x([j]G))=-1}
(X-x([j]G)).
\]

Then

\[
\boxed{K_H=K_{G,+}K_{G,-}.}
\]

The canonical idempotent for the positive sector is

\[
e_+
=
K_{G,-}
\left(K_{G,-}^{-1}\bmod K_{G,+}\right)
\bmod K_H,
\]

and the involution is

\[
\boxed{J_G=2e_+-1\pmod {K_H}.}
\]

The four V14 selector branches give a finer factorization:

\[
\boxed{
K_H=
K_{\mathrm{uniform}}
K_{\mathrm{minority}\,0}
K_{\mathrm{minority}\,1}
K_{\mathrm{minority}\,2}.
}
\]

The exact covariance laws are

\[
J_{-G}=J_G,
\]

\[
J_{\alpha G}(X)=J_G(\beta^2X)\pmod {K_H(X)}.
\]

These identities were replayed for every marked generator on every frozen
curve.

## Logarithmic floor-sum certificate

For odd \(n\), a unit \(a\bmod n\), and

\[
S(a;n)
=
\sum_{k=1}^{n-1}
(-1)^{k+(ak\bmod n)},
\]

put \(m=(n-1)/2\) and

\[
A_1=
\sum_{j=1}^{m}
\left\lfloor\frac{aj}{n}\right\rfloor,
\qquad
A_2=
\sum_{j=1}^{m}
\left\lfloor\frac{2aj}{n}\right\rfloor.
\]

Then

\[
\boxed{
S(a;n)=(n-1)-4A_2+8A_1.
}
\]

A short derivation is as follows. Let \(E\) be the number of even \(k\) for
which \(ak\bmod n\) is also even. Since multiplication by \(a\) permutes the
nonzero residues, the same-parity count is \(2E\), hence

\[
S=4E-(n-1).
\]

Writing \(k=2j\), the parity of \(2aj\bmod n\) is the parity of

\[
\left\lfloor\frac{2aj}{n}\right\rfloor.
\]

The indicator that this floor is even equals

\[
1
-
\left\lfloor\frac{2aj}{n}\right\rfloor
+
2\left\lfloor\frac{aj}{n}\right\rfloor.
\]

Summation gives the displayed formula.

Both floor sums are computed by the standard Euclidean floor-sum descent in
\(O(\log n)\) integer rounds. Exhaustive diagnostics covered every unit
multiplier for all odd moduli through 255:

```text
unit multipliers: 13,230
scalar terms:      2,240,852
failures:          0
```

This logarithmic computation counts the sign fibers. It does not evaluate the
sector bit at an unknown public point.

## Exact secp256k1 cardinalities

For the fixed secp256k1 order and GLV eigenvalue,

\[
S(\lambda;n)=208.
\]

The Euclidean certificates use 141 and 143 rounds for \(A_1\) and \(A_2\).

The half-kernel degree is

\[
d=\frac{n-1}{2}.
\]

Because the full correlation counts each Kummer point twice,

\[
N_+-N_-=\frac{208}{2}=104,
\qquad
N_++N_-=d.
\]

Therefore

\[
\boxed{
N_+
=
\frac{n-1+208}{4}
=
28948022309329048855892746252171976963209391069768726095651290785379540373636,
}
\]

\[
\boxed{
N_-
=
\frac{n-1-208}{4}
=
28948022309329048855892746252171976963209391069768726095651290785379540373532.
}
\]

For the four selector branches, C3 rotation makes the three minority factors
equal in degree. Their exact sizes are

\[
\boxed{
N_{\mathrm{uniform}}
=
14474011154664524427946373126085988481604695534884363047825645392689770186870,
}
\]

\[
\boxed{
N_{\mathrm{minority}\,i}
=
14474011154664524427946373126085988481604695534884363047825645392689770186766
\quad (i=0,1,2).
}
\]

Thus the uniform branch exceeds each minority branch by exactly 104.

## Direct rational degree barrier

Suppose an ordinary rational function

\[
R(X)=\frac{A(X)}{B(X)}
\]

is regular on every half-kernel root and directly returns the field values

\[
R(x([j]G))=J_G(x([j]G))\in\{+1,-1\}.
\]

Let

\[
D=\max(\deg A,\deg B).
\]

On every positive-sector root, \(A-B\) vanishes. On every negative-sector
root, \(A+B\) vanishes. Both polynomials are nonzero because both sign fibers
are nonempty. Hence

\[
D\ge N_+,\qquad D\ge N_-.
\]

Consequently

\[
\boxed{
D
\ge
28948022309329048855892746252171976963209391069768726095651290785379540373636.
}
\]

This is a 254-bit degree lower bound, essentially \(2^{254}\).

The statement is deliberately narrow. It is:

- a degree and explicit-representation lower bound;
- for an ordinary rational function returning the field values \(+1/-1\);
- under regularity on all half-kernel roots.

It is not:

- an arithmetic-circuit-size lower bound;
- a lower bound for a quadratic-character output \(\chi(f)\);
- a lower bound for modular composition, transposed evaluation, recurrence
  compression, p-adic evaluation, or another high-degree low-size
  representation.

## Frozen toy replay

The executable package checks:

```text
curves:                         5
marked generators/roots:      438
Kummer evaluations:        23,130
scalar reconciliations:    46,260
identity failures:              0
```

For every one of the 438 marked roots it verifies:

- equality of the oriented-root and scalar-interpolated sector polynomial;
- \(J_G^2=1\bmod K_H\);
- binary factorization \(K_H=K_{G,+}K_{G,-}\);
- CRT reconstruction \(J_G=2e_+-1\);
- four-branch root counts;
- \(J_{-G}=J_G\);
- GLV covariance under generator rotation;
- exact agreement between direct parity correlation and the floor-sum
  certificate.

On every frozen curve, the canonical polynomial representative of \(J_G\)
has degree exactly

\[
\deg K_H-1=\frac{n-3}{2}.
\]

This is exact finite evidence that no cancellation occurs in the canonical
dense representative on the corpus. It is not an asymptotic circuit lower
bound.

## Revised frontier

The carry channel is now fully reconciled with the legacy \(g_G/R3_G\) line.
The sector channel is now an exact generator-oriented factor-selection
problem with known cardinalities.

The remaining useful questions are:

1. Can the high-degree sector involution be evaluated by a genuinely short
   straight-line program, modular-composition representation, transposed
   method, or recurrence without materializing \(K_{G,+}\), \(K_{G,-}\), or
   \(J_G\)?
2. Can one shared circuit compute both \(g_G(Q)\) and \(J_G(x(Q))\) more
   cheaply than the dense representations?
3. Can additive mixing of distinct CM weights produce the nontrivial C3
   transformation law without importing hidden orientation advice?
4. Can a scoped lower bound be proved for one of those explicit
   representation categories?

The central UORC-056 evaluator remains open.
