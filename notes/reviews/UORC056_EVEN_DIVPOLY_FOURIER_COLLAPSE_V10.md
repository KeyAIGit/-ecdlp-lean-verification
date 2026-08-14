# UORC-056 even division-polynomial Fourier collapse V10

## Status

V10 closes the pure single-division-polynomial character route that V9 left
open on fields with `q=3 mod 4`.

The new observation is that the apparently high-degree even division
polynomial never needs to be treated as a high-conductor function on the marked
subgroup. The chain rule removes its square factor and conjugates the fixed
second division polynomial by a subgroup automorphism. The Fourier conductor
therefore stays equal to four, independently of the index.

The algebraic reduction, exact corpus scans and secp256k1 inequality are
machine checked. The hybrid character-sum bound is inherited from the
provisional V8 sheaf theorem, so independent specialist review and formalization
remain pending.

## 1. Setting

Let `E/F_q` be an elliptic curve over an odd finite field and let

```text
H=<G> subset E(F_q),     |H|=n,
```

where `n>=3` is odd. Let `chi` be the quadratic character. We ask whether there
exist a positive integer `m` and a global phase `epsilon in {+1,-1}` such that

```text
chi(psi_m([k]G))=epsilon*(-1)^k,
1<=k<n.
```

Allowing the global phase makes the no-go statement stronger than the
canonically normalized target.

If `gcd(m,n)>1`, then some nonzero point of `H` is an `m`-torsion zero of
`psi_m`, so an everywhere-defined exact sign evaluator is already impossible.
Hence only `gcd(m,n)=1` requires analysis.

## 2. Odd indices fail covariance

Division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q).
```

For odd `m`, the function is invariant under `Q -> -Q`, and therefore its
quadratic character is invariant. Canonical parity on an odd cycle is
anti-invariant:

```text
(-1)^(n-k)=-(-1)^k.
```

Thus every odd index is impossible over every odd field.

## 3. Every even index collapses to psi_2

Write

```text
m=2u.
```

The normalized division-polynomial chain rule is

```text
psi_(ab)=(psi_a o [b])*psi_b^(a^2).
```

Taking `a=2` gives

```text
psi_(2u)(Q)=psi_2([u]Q)*psi_u(Q)^4.
```

On the nonzero marked orbit, `psi_u(Q)` is nonzero because `gcd(u,n)=1`.
Taking the quadratic character kills the fourth power:

```text
chi(psi_(2u)(Q))=chi(psi_2([u]Q)).
```

This identity is the decisive reduction. It says that the character sequence
for an arbitrarily large even index is merely a multiplicative decimation of
the fixed sequence

```text
tau(k)=chi(psi_2([k]G)).
```

The large divisor of `psi_(2u)` is a pullback artifact. On `H`, multiplication
by `u` is a permutation and the character sees only `psi_2`.

## 4. Fourier peak forced by parity

Let

```text
r=(n-1)/2.
```

The exact near-half Fourier coefficient of canonical parity has magnitude

```text
abs(sum_{k=1}^{n-1} (-1)^k exp(-2*pi*i*r*k/n))
  = cot(pi/(2n)).
```

Suppose an even-index formula were exact. Substituting `j=u*k mod n` gives

```text
sum_{k=1}^{n-1} chi(psi_2([u*k]G)) exp(-2*pi*i*r*k/n)

= sum_{j=1}^{n-1} chi(psi_2([j]G))
    exp(-2*pi*i*r*u^(-1)*j/n).
```

Thus exact parity would force a subgroup Fourier coefficient of the fixed
trace function `chi(psi_2)` to have magnitude `cot(pi/(2n))`.

## 5. The fixed conductor is four

In odd characteristic,

```text
div(psi_2)
 = sum_{T in E[2] minus {O}} [T] - 3[O].
```

Over the algebraic closure there are three nonidentity 2-torsion points. Each
zero has odd order one, and the pole at `O` has odd order three. Therefore

```text
s(psi_2)=4.
```

The subgroup has odd order, so no nonzero point of `H` lies in this divisor.
There is no regularization error on the evaluated orbit.

Apply the V8 subgroup-character extension and annihilator averaging argument to
the quadratic Kummer sheaf of `psi_2`. The near-half character is faithful of
odd order, so its Lang local system cannot cancel the order-two Kummer system.
On the genus-one curve punctured at the four odd-support points,
Grothendieck-Ogg-Shafarevich gives

```text
dim H_c^1=4.
```

The trace formula and Deligne weights give, for every subgroup frequency,

```text
abs(sum_{j=1}^{n-1} chi(psi_2([j]G))*eta([j]G))
  <= 4*sqrt(q).
```

Consequently, a necessary condition for any pure division-polynomial parity
formula is

```text
cot(pi/(2n)) <= 4*sqrt(q).
```

This condition is independent of `m`.

## 6. secp256k1 is closed for every index

The machine certificate uses

```text
cot(pi/(2n)) > (98*n^2-121)/(154*n)
```

and verifies the exact integer inequality

```text
(98*n^2-121)^2 > 16*(154*n)^2*p.
```

For the public secp256k1 parameters,

```text
cot(pi/(2n))/(4*sqrt(p))
  approximately 5.415762074247741e37,
```

with base-two logarithm

```text
125.348503870528.
```

Therefore, for every positive integer `m`,

```text
chi(psi_m(Q))
```

cannot equal canonical parity on all nonzero secp256k1 subgroup points, even
after allowing one global sign phase.

This completely closes the pure single-division-polynomial character route.

## 7. Frozen-corpus result

The certified Fourier inequality closes 17 of the 18 frozen curves. The only
small exception is

```text
p=43, n=31,
```

where the inequality is too weak:

```text
cot(pi/(2n)) approximately 19.7183,
4*sqrt(p) approximately 26.2298.
```

For that curve, V10 exhausts every invertible multiplier class `u mod n` and
allows both global phases. There is no exact candidate. The best class is

```text
u=8,
24/30 matches.
```

The same complete multiplier scan is run on all 18 curves and finds no exact
candidate anywhere.

The chain identity is independently replayed on the five discovery curves for
53,754 point-index pairs.

## 8. Relation to V9

V9 represented the surviving even-index case as

```text
chi(psi_m([k]G))=rho_(m*k),
rho_j=chi(psi_j(G)).
```

V10 uses `m=2u` and the chain rule once more:

```text
rho_(2u*k)=chi(psi_2([u*k]G)).
```

Hence the apparent EDS decimation is not a genuinely high-index EDS mechanism
for a single division polynomial. It is a permutation of one fixed low-
conductor Kummer trace function.

The V9 support-to-cost counterexample remains valid as a statement about
rational functions and straight-line programs. What disappears is its status
as a possible exact parity evaluator.

## 9. What V10 closes

- every odd-index pure division-polynomial character by negation covariance;
- every even-index pure division-polynomial character when
  `cot(pi/(2n))>4*sqrt(q)`;
- every positive index on secp256k1;
- every positive index on all 18 frozen curves, using the complete small-curve
  scan for the one case outside the asymptotic inequality;
- the V9 open `q=3 mod 4` pure EDS-decimation branch.

## 10. What remains open

V10 does not close:

1. products of several independently pulled division-polynomial characters;
2. a recursively shared construction whose final output does not collapse to
   one `chi(psi_m)`;
3. direct field-valued evaluation of `Y_G(x(Q))/y(Q)`;
4. theta, elliptic-unit or compact oriented-root formulas;
5. adaptive branching and non-character output models.

The next rational-character question is whether a product of a sub-root number
of low-conductor pullbacks can exploit cancellations or shared evaluation to
beat the V8 support requirement. The more distinct remaining branch is direct
field-valued evaluation of `Y_G`, where no outer quadratic character is taken.

## 11. Primary references

- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in
  Number Theory 12 (2026), Article 53. The paper states the divisor,
  recurrence, `O(log n)` computation and chain rule for normalized division
  polynomials.
- J. H. Silverman, *p-adic properties of division polynomials and elliptic
  divisibility sequences*, Mathematische Annalen 332 (2005), 443-471. The
  paper gives the normalized chain rule and finite-field periodicity.
- P. Deligne, *La conjecture de Weil II*, Publications Mathematiques de
  l'IHES 52 (1980), 137-252.
- SGA 5, *Cohomologie l-adique et fonctions L*.

## Claim boundary

V10 is a scoped no-go theorem for one pure quadratic character of one classical
division polynomial, with an optional global phase. Its Fourier bound inherits
the provisional V8 sheaf framework. It does not prove a lower bound for all
arithmetic circuits and does not recover any unknown scalar.
