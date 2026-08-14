# UORC-056 regularized Fourier-to-divisor barrier V8

## Status

This checkpoint closes the sheaf-theoretic proof obligation isolated in V7.
The proof is assembled from standard results on Lang character sheaves,
quadratic Kummer sheaves, Grothendieck-Ogg-Shafarevich, the trace formula and
Deligne weights. The arithmetic consequences are independently replayed by two
scripts. Independent specialist review and formalization remain pending, so
the result is treated as a provisional theorem rather than a published claim.

## 1. Statement

Let `E/F_q` be an elliptic curve over an odd finite field. No assumption that
the full group `E(F_q)` is cyclic is needed. Let

```text
H=<G> subset E(F_q),     |H|=n,
```

where `n>=3` is odd. Let `f in F_q(E)^*`, and define

```text
S_odd(f)={P in E(Fbar_q): ord_P(f) is odd},
s(f)=#S_odd(f).
```

Away from zeros and poles, put `lambda_f(P)=chi(f(P))`, where `chi` is the
quadratic character. At rational divisor points, allow any unit-modulus
regularized value. This includes the local-leading-coefficient convention used
by the divisor-aware V1-V5 screens.

Assume exact scalar parity on the nonidentity subgroup orbit:

```text
lambda_f([k]G)=(-1)^k,     1<=k<n.
```

Then

```text
cot(pi/(2n)) <= s(f)*sqrt(q)+s(f)+1,
```

and therefore

```text
s(f) >= (cot(pi/(2n))-1)/(sqrt(q)+1).
```

If `d=deg(f:E->P^1)`, then

```text
d >= ceil(s(f)/2).
```

When `n` is comparable to `q`, this gives

```text
s(f)=Omega(sqrt(n)),     d=Omega(sqrt(n)).
```

## 2. Exact parity Fourier peak

For `r=(n-1)/2` and `z=exp(-2*pi*i*r/n)`,

```text
sum_{k=1}^{n-1} (-1)^k z^k=(1-z)/(1+z),
```

so

```text
abs(sum_{k=1}^{n-1} (-1)^k z^k)=cot(pi/(2n)).
```

The conjugate near-half frequency gives the same magnitude. This part is
algebraic and independently replayed on the frozen corpus.

## 3. Reduction from a subgroup sum to complete elliptic sums

Write `A=E(F_q)` and `m=[A:H]`. Let `eta` be the faithful near-half character
of `H`. Every character of a subgroup of a finite abelian group extends to the
whole group, so choose `theta` on `A` with `theta|_H=eta`.

Let

```text
H^perp={psi in A^ : psi|_H=1}.
```

The exact indicator identity is

```text
1_H(P)=(1/m) sum_{psi in H^perp} psi(P).
```

Therefore, for any trace function `t(P)`,

```text
sum_{P in H} eta(P)t(P)
 = (1/m) sum_{psi in H^perp}
     sum_{P in A} theta(P)psi(P)t(P).
```

This removes the full-group assumption from V6 and V7. It is enough to bound
each complete sum on `E(F_q)`.

## 4. Lang and Kummer noncancellation

For every `psi in H^perp`, the character `theta*psi` still restricts to the
faithful odd-order character `eta` on `H`. The Lang isogeny

```text
Frob_q-1:E->E
```

produces a rank-one lisse local system `L_(theta psi)` whose geometric monodromy
order is divisible by `n`.

The quadratic Kummer local system `K_f` has geometric order at most two. Hence

```text
F_psi=L_(theta psi) tensor K_f
```

cannot be geometrically trivial: a local system whose restriction contains an
odd-order faithful character cannot be cancelled by an order-two factor.

This resolves the nontriviality concern in V7 without relying on a fragile
choice of arithmetic normalization.

## 5. Exact conductor constant

Let

```text
U=E-S_odd(f).
```

On `U`, the sheaf `F_psi` is rank one, lisse, tame and pure of weight zero. Its
only geometric punctures are the `s(f)` odd-valuation points. Since the genus
is one, Grothendieck-Ogg-Shafarevich gives

```text
chi_c(U_bar,F_psi)=-s(f).
```

Geometric nontriviality kills `H_c^0` and `H_c^2`, so

```text
dim H_c^1(U_bar,F_psi)=s(f).
```

The Grothendieck trace formula and Deligne's weight bound yield the sharp
normalization

```text
abs(sum_{P in E(F_q)}
    theta(P)psi(P) Tr(K_f)_P)
 <= s(f)*sqrt(q).
```

Averaging over `H^perp` preserves the same bound for the subgroup sum. Thus the
constant called `C_sh` in V7 is exactly one under these conventions.

## 6. Divisor-aware regularization

At an odd-valuation rational point, the middle-extension Kummer trace is zero,
whereas a divisor-aware evaluator may return a sign derived from a selected
local leading coefficient. Each such replacement changes the sum by at most
one. There are at most `s(f)` rational odd-support points.

The parity Fourier sum omits the identity `O`, while the complete sum contains
at most one identity contribution of magnitude one. Therefore

```text
cot(pi/(2n)) <= s(f)*sqrt(q)+s(f)+1.
```

Even-order zeros and poles do not require an error term. Locally
`f=t^(2a)u`, so the Kummer sheaf extends lisse and its trace is the quadratic
character of the unit `u(P)`, which is exactly the intrinsic regularized value.

## 7. Collapse of products of atoms

A product or quotient of quadratic-character atoms collapses to one rational
function:

```text
prod_i chi(f_i(P))^(epsilon_i)
 = chi(prod_i f_i(P)^(epsilon_i)).
```

The same remains true under exact local regularization. Local orders add and
local unit coefficients multiply. If the aggregate order is even, parameter
changes contribute a square; if it is odd, the point is charged in
`S_odd(f)`.

Consequently this theorem subsumes bounded affine, pulled-line,
reducible-conic, globally balanced and small-Miller character products. The
previous V1-V5 negatives are finite witnesses of the general obstruction.

## 8. Certified secp256k1 consequence

For secp256k1, the public SEC2 parameters have cofactor one. The machine proof
uses

```text
cot(pi/(2n)) > (98*n^2-121)/(154*n)
```

and exact integer square comparisons for the radical denominator. It certifies

```text
s(f) >= 216543324404233567658511113820216134562,

deg(f) >= 108271662202116783829255556910108067281.
```

The support lower bound has binary size 127. This excludes any exact
regularized rational-character evaluator whose odd divisor support is below
square-root scale.

## 9. What is now closed

The theorem closes, under the stated standard sheaf inputs:

- any single quadratic character of a rational function;
- any finite product or quotient of such atoms;
- exact local-leading-coefficient regularization at zeros and poles;
- arbitrary odd cyclic marked subgroups, not only cofactor-one curves;
- every family with `s(f)=o(n/sqrt(q))`.

## 10. What remains open

This is not yet a straight-line-program lower bound. A compact expression can
define a rational function of enormous degree and square-root-scale divisor
support. The central surviving routes are therefore:

1. high-degree but low-size pullbacks and addition-chain circuits;
2. long Miller or EDS recurrences whose syntax is logarithmic in an index;
3. theta, elliptic-unit or special-function representations;
4. direct field-valued evaluation of `Y_G(x(Q))/y(Q)` without reduction to one
   multiplicative character;
5. adaptive branching or non-character outputs.

The next problem is no longer to search more bounded divisor dictionaries. It
is to connect square-root divisor complexity to all-in representation and
evaluation cost for succinct high-degree programs.

## 11. References

- P. Deligne, *La conjecture de Weil II*, Publications Mathematiques de
  l'IHES 52 (1980), 137-252.
- C. Cunningham and D. Roe, *From the function-sheaf dictionary to
  quasicharacters of p-adic tori*, Journal of the Institute of Mathematics of
  Jussieu 17 (2018), 1-37.
- M. Perret, *Multiplicative character sums and Kummer coverings*, Acta
  Arithmetica 59 (1991), 279-290.
- SGA 5, *Cohomologie l-adique et fonctions L*.
- Standards for Efficient Cryptography Group, *SEC 2: Recommended Elliptic
  Curve Domain Parameters*, Version 2.0 (2010).

## Claim boundary

This is a provisional theorem-level research result, not a peer-reviewed or
formally verified theorem. It lower-bounds odd divisor support and rational-map
degree. It does not lower-bound arbitrary circuit size, solve ECDLP, or recover
any unknown scalar.
