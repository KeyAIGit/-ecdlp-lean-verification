# Square-class circuit frontier

Date: 2026-08-12

Status: **structural reduction after the linear-state and rational-degree barriers; no general arithmetic-circuit lower bound and no decoder**.

## 1. Exact target

The carry target remains

```text
g_G(Q)=g_G(G)*sign(U_G(Q)),
```

or any publicly equivalent exact output `R3_G(Q)` or
`h_G(x(Q)^3)`.

A direct quadratic-character coordinate decoder would have the form

```text
chi_p(F_G(Q))=g_G(Q).
```

Package `RATIONAL-CHARACTER-DEGREE-BARRIER-036-SUPPLEMENT` proves that any
geometrically non-power rational `F_G` satisfying this identity on every
nonzero subgroup point has degree at the square-root scale. This still leaves
open high-degree functions represented by small straight-line circuits.

## 2. Work in the square-class group

Let

```text
K=F_p(E),
Sq(K)=K^*/K^{*2}.
```

The quadratic character of a nonzero value depends only on the class of the
function in `Sq(K)`.

For square classes, the inexpensive multiplicative gates behave as follows:

```text
[F*G]   =[F]+[G],
[1/F]   =[F],
[F^2]   =0,
[F^(2m)]=0,
[F^(2m+1)]=[F].
```

Since `p` is odd,

```text
[F^p]=[F].
```

Thus repeated squaring, Frobenius, inversion and multiplication can increase
formal algebraic degree enormously without creating comparably new quadratic
information.

The only ordinary arithmetic gate that creates a genuinely new square class
is addition or subtraction.  If `F` and `G` are nonzero, then

```text
[F+G]=[F]+[1+G/F].
```

Accordingly, every circuit can be audited by the sequence of new classes

```text
[1+R_1],...,[1+R_A]
```

created at its `A` additive gates, together with the initial coordinate and
constant classes.

This is the correct complexity measure for a quadratic-character decoder. Raw
polynomial degree alone overcounts squaring, while gate count alone ignores the
odd divisor support introduced by each `1+R_i`.

## 3. Why the degree theorem is not yet a circuit theorem

The iteration

```text
F_0=z,
F_(i+1)=F_i^2+c_i
```

has degree `2^i` after only `i` additions and squarings.  Therefore the
secp256k1 lower bound

```text
deg F > 2^125.348
```

forces only about 126 degree-doubling stages in this unrestricted grammar.
That is still polynomial in the bit length and cannot be rejected merely from
formal degree.

A true negative result must control the odd divisor support or conductor of the
square class after additions, not just the unreduced degree of the expression.

## 4. Interaction with the elliptic Gauss projector

The synchronized parent line constructs

```text
S_3(P)=sum_(a=1..n-1) chi_n(a)x([a]P)^3,
S_3([k]G)=chi_n(k)S_3(G).
```

This is an exact scalar-Legendre projector of direct cost `Theta(n)`.  Its
oriented factors have degree `(n-1)/12`, while the universal quadratic
invariant is only the generator-blind square `S_3(G)^2`.

A compact Eisenstein-CM formula would have to choose the oriented square root,
not merely compute the square.  In square-class language, it must introduce a
generator-sensitive additive/divisor class not already present in the
unoriented invariant.

The scalar-Legendre bit is not the carry bit.  Even a compact projector needs a
separate classical sub-square-root recovery theorem before it can be promoted
to an ECDLP result.

## 5. Admissible circuit grammar

A candidate family is admitted only when it specifies:

```text
inputs:       affine/projective coordinates of E,G,Q and public CM constants;
operations:   +,-,*,inverse,Frobenius and explicitly costed extensions;
constants:    uniformly generated from (p,n,E,G,phi), not fitted labels;
output:       an exact nonzero base-field value or exact branch-certified value;
size:         all gates, constants, advice, preprocessing and precision counted;
correctness:  chi(output)=g_G(Q) for every Q in <G>\{O};
reuse:        the same circuit evaluates every chosen multiple [t]Q.
```

A coefficient list or model storing an `Omega(sqrt(n))` fraction of the
orientation partition is rejected even if online evaluation is small.

## 6. First theorem-sized question

The next exact problem is:

> For a uniform circuit with `A` addition/subtraction gates, can one bound the
> conductor or odd divisor support of its output square class in terms of `A`,
> the initial coordinate divisors and uniformly generated constants strongly
> enough to show that the GLV carry requires `A=Omega(sqrt(n))` or another
> super-polylogarithmic resource?

Equivalent constructive version:

> Is there an exact identity using only `poly(log n)` additive square-class
> innovations whose final character equals `g_G(Q)` on the full subgroup?

## 7. Immediate rejection tests

A proposed circuit is rejected if:

1. its output differs from a known public observable only by a square;
2. all apparent complexity comes from squaring/Frobenius with no new additive
   divisor classes;
3. the constants encode the carry partition, a faithful order-`n` character,
   the selected dual `C3` orbit, or an oriented factor of linear size;
4. it computes only `S_3^2`, a norm, trace or other generator-blind invariant;
5. correctness is empirical rather than an exact identity;
6. total preprocessing or advice reaches the generic square-root baseline.

## 8. Current answer

```text
Low-degree rational-character decoder                     excluded
Explicit translation-linear state                         excluded
Standard bounded-rank theta pairing without dual selector excluded
Exact scalar-Legendre orbit projector                      exists at Theta(n)
High-degree low-size square-class circuit                  open
Canonical p-adic/analytic orientation circuit              open
Public carry or hard-R3 decoder                            absent
Classical sub-square-root ECDLP algorithm                  absent
```

The surviving problem is therefore not arbitrary nonlinear computation. It is
whether a small number of genuinely new additive square classes can reproduce
the generator-oriented carry cut.
