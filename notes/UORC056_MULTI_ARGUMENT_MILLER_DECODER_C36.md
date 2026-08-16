# UORC-056 C36: multi-argument Miller defect decoder boundary

Date: 2026-08-15

Status: exact positive-state / bounded-decoder-boundary package. No parity oracle or sub-square-root ECDLP algorithm is claimed.

## 1. Input from C35

C35 constructed the shifted Miller state

\[
M_S(P)=\frac{f_G(P+S)}{f_G(S)},
\qquad
\operatorname{div}(f_G)=n[G]-n[O],
\qquad
S^p=-S.
\]

It is public, marked-generator-sensitive, regular on the declared subgroup queries, and evaluable by a Miller straight-line program of length \(O(\log n)\).

C35 also proved that all anti-rational shifts are explicit \(n\)-th-power line gauges of one base Miller potential and that the norm-one projection collapses to a public centered Kummer coordinate. The remaining information therefore sits in the common full field potential and its nonlinear combinations.

## 2. Field-valued multiplicative defect

For any nonzero scalar state \(M\), define

\[
\boxed{
\Delta_M(P,R)
=
\frac{M(P+R)}{M(P)M(R)}.
}
\]

For the C35 state we write \(\Delta_S\).

This is the exact field analogue of the C33 carry, because

\[
C_G(P,R)
=
\frac{\sigma_G(P+R)}{\sigma_G(P)\sigma_G(R)}
\]

for \(\sigma_G\in\{\pm1\}\).

Every multiplicative defect satisfies the normalized cocycle identity

\[
\boxed{
\Delta(P,R)\Delta(P+R,T)
=
\Delta(R,T)\Delta(P,R+T).
}
\]

This is an algebraic identity, not a heuristic.

## 3. Shift-gauge normal form

C35 gives, on the regular domain,

\[
M_S(P)=c_S f_G(P)h_S(P)^{-n},
\]

where \(h_S=g_{G,-S}\) is a public addition-line function and \(c_S\ne0\) depends only on the selected normalization.

Substitution into the field defect gives

\[
\boxed{
\Delta_S(P,R)
=
c_S^{-1}
\frac{f_G(P+R)}{f_G(P)f_G(R)}
\left(
\frac{h_S(P)h_S(R)}{h_S(P+R)}
\right)^n.
}
\]

After normalizing one public reference pair, the common scalar disappears. Thus every shifted field defect is an explicit \(n\)-th-power coboundary gauge of one base Miller defect.

For secp256k1, the \(n\)-th-power map on \(\mathbb F_{p^2}^{\times}\) is an automorphism because

\[
\gcd(n,p^2-1)=1.
\]

Therefore the public line gauge is removable. Varying the twist shift does not create new independent defect channels.

## 4. The exact three-defect state

Retain the C34 geometry

\[
A=[2]Q,
\qquad
T=[-2^{-1}]Q,
\qquad
B=T-A.
\]

Define

\[
\boxed{
\mathbf D_S(Q)=
\bigl(
\Delta_S(Q,A),
\Delta_S(A,B),
\Delta_S(-T,-B)
\bigr).
}
\]

This uses exactly the three locations whose sign defects multiply to parity:

\[
\sigma_G(Q)
=
C_G(Q,A)C_G(A,B)C_G(-T,-B).
\]

The field state requires only a constant number of shifted Miller evaluations. Hence its arithmetic construction cost is \(O(\log n)\), excluding any decoder.

This sharpens the remaining question:

\[
\boxed{
\text{Can a compact public decoder map }\mathbf D_S(Q)\text{ to }(-1)^k?
}
\]

## 5. Exact collision classification

Every anti-rational shift on every frozen curve was tested.

```text
5 frozen curves
520 twist shifts
54,192 nonzero query tuples
```

For every one of the 520 shifts:

```text
number of distinct three-defect tuples = n-1
parity-mixed tuple collisions          = 0
```

Thus the tuple is actually injective on the full nonzero frozen subgroup, not merely parity-separating.

This is a positive information result:

\[
\boxed{
\mathbf D_S(Q)\text{ contains enough information to recover parity on every frozen screen.}
}

It is not a positive algorithm. An arbitrary lookup decoder for an injective \((n-1)\)-point code requires linear-scale advice or representation unless additional structure is found.

Single defects are weaker. Depending on the curve and shift, one field defect can have collisions that mix its corresponding carry sign. The joint tuple removes all such collisions in the frozen corpus.

## 6. All-shift bounded-degree decoder screen

Two exact decoder grammars were tested on every one of the 520 shifts.

### Polynomial grammar

All polynomials in three variables of total degree at most three:

\[
P(D_1,D_2,D_3).
\]

The monomial count is

\[
\binom{3+3}{3}=20.
\]

For every shift, the 20-column evaluation matrix has full rank 20, and parity is not in its column span.

Result:

\[
\boxed{0\text{ polynomial decoders of total degree }\le3.}
\]

### Rational grammar

All candidate rational functions

\[
\frac{A(D_1,D_2,D_3)}{B(D_1,D_2,D_3)}
\]

where both \(A\) and \(B\) have total degree at most two.

Writing the sample equations as

\[
A(D(k))-\sigma(k)B(D(k))=0
\]

gives a homogeneous 20-column system, because each side has ten monomials. For every shift the matrix has full rank 20.

Result:

\[
\boxed{
0\text{ nonzero rational relations of numerator/denominator degree }\le2.
}
\]

This excludes the entire declared grammar, including every affine and quadratic fractional decoder in the three field coordinates.

## 7. Canonical-shift interpolation thresholds

For one deterministic canonical shift per frozen curve, C36 continued the exact rank computation until the first polynomial interpolation decoder appears.

### Two defect coordinates

The first polynomial decoder degrees are

```text
n=31   degree 7
n=79   degree 11
n=67   degree 10
n=127  degree 15
n=139  degree 16
```

These are exactly the first degrees for which

\[
\binom{d+2}{2}\ge n-1.
\]

### Three defect coordinates

The first polynomial decoder degrees are

```text
n=31   degree 4
n=79   degree 6
n=67   degree 6
n=127  degree 8
n=139  degree 8
```

Again these are exactly the first degrees for which

\[
\binom{d+3}{3}\ge n-1.
\]

Before that dimension threshold, every evaluation matrix has full column rank and parity is outside its span.

For rational interpolation, the first nonzero homogeneous relations appear at the corresponding generic dimension thresholds:

```text
                 two coordinates   three coordinates
n=31                     5                  3
n=79                     8                  5
n=67                     7                  4
n=127                   10                  6
n=139                   11                  6
```

These are precisely the first degrees at which twice the monomial count exceeds the number of samples. A nonzero homogeneous relation at that threshold is not automatically a valid everywhere-defined rational decoder, but the absence of any earlier relation is exact.

The observed rank profile is therefore maximally generic until plain interpolation dimension forces relations.

## 8. What this means

C35 answered one earlier question positively:

```text
Does a compact generator-sensitive field state exist?
Yes.
```

C36 answers the next question more sharply:

```text
Does the natural three-defect state expose parity through an early
low-degree algebraic decoder?
No, in the entire declared frozen grammar.
```

The tuple behaves like an injective encoding of the unknown scalar rather than a compressed parity statistic. Adding coordinates reduces the generic interpolation degree only through the ordinary combinatorial growth of the monomial basis. No special early parity relation appears.

This does not prove that every nonlinear decoder is expensive. It closes only the exact polynomial and rational grammars stated above.

## 9. Successor

The next package is

```text
CUBICAL-MILLER-DEFECT-ELIMINATION-C37
```

Its job is not to add more raw Miller coordinates. The current tuple already contains essentially the whole frozen scalar.

C37 should instead search for an identity that eliminates the scalar code before interpolation, using one of:

1. the cubical or biextension identities of the Miller defect cocycle;
2. a determinant or resultant whose cancellations use all three C34 pairs simultaneously;
3. an anchor-normalized elliptic-net cell not reducible to the C35 shift gauge;
4. a proof that every bounded-size cubical elimination reduces to a previously closed character or interpolation grammar.

## Decision flags

```text
compact_public_three_defect_state_found=true
joint_state_injective_on_every_frozen_shift=true
arbitrary_lookup_decoder_exists_on_frozen_curves=true
lookup_decoder_is_cost_acceptable=false
polynomial_total_degree_le_3_decoder_found=false
rational_total_degree_le_2_decoder_found=false
canonical_early_interpolation_structure_found=false
parity_oracle_found=false
sub_sqrt_evaluator_found=false
sub_sqrt_ecdlp_found=false
```
