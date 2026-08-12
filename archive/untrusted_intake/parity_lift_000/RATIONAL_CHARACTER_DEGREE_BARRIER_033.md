# RATIONAL-CHARACTER-DEGREE-BARRIER-033

Date: 2026-08-12

Status: **theorem-first square-root degree barrier for exact rational-character carry decoders; no universal arithmetic-circuit lower bound**.

No external point, private key, wallet, or production-sized discrete-log target is accepted. This package constructs no carry, hard-R3, parity, or ECDLP decoder.

## 1. Input from package 032

The surviving exact bit is the generator-relative GLV carry

```text
g_G([k]G)=(-1)^gamma(k),
```

where the canonical representatives of

```text
k, lambda*k, lambda^2*k
```

sum to either `n` or `2n`.

Equivalently,

```text
g_G(Q)=g_G(G)*sign(U_G(Q)),
```

for the normalized Gaussian-period orientation `U_G`.

Package 032 closes every explicit finite-field state with a fixed linear update under `Q -> Q+G` and sublinear total state. The next class is a direct nonlinear coordinate predicate, with no maintained translation state.

The first broad subclass is

```text
D_f(Q)=chi(f(Q)),
```

where `chi` is the quadratic character and `f` is a rational function on the elliptic curve.

## 2. Exact carry Fourier coefficient

Use the normalized scalar Fourier transform

```text
g_hat(j)=(1/n) * sum_(k mod n) g_G([k]G) * exp(-2*pi*i*j*k/n),
g_G(O)=0.
```

The exact carry transform derived in the earlier Fourier package is

```text
g_hat(j)
 = (i/n) * (
     cot(pi*[j]_n/n)
     + cot(pi*[lambda*j]_n/n)
     + cot(pi*[lambda^2*j]_n/n)
   )
```

up to the fixed sign convention for the Fourier exponent.

At `j=1`, the canonical residues satisfy

```text
1 + lambda + [lambda^2]_n = n.
```

Put

```text
A=pi/n,
B=pi*lambda/n,
C=pi*[lambda^2]_n/n.
```

Then `A+B+C=pi`, and

```text
cot(B)+cot(C)
 = sin(B+C)/(sin(B)sin(C))
 = sin(A)/(sin(B)sin(C))
 > 0.
```

Therefore

```text
n*abs(g_hat(1)) > cot(pi/n).                         (H1)
```

In particular, since `tan(x) <= 2*x` for `0 < x <= pi/4`, every odd `n >= 5` satisfies

```text
abs(g_hat(1)) > 1/(2*pi).                            (H2)
```

For secp256k1 the coefficient differs from `1/pi` only beyond the precision relevant here:

```text
abs(g_hat(1))
 = 0.3183098861837906715377675267450287240689...
```

This is the constant-heavy coefficient used by the chosen-multiplier recovery. Here it is used in the opposite direction: any exact public coordinate decoder must reproduce the same coefficient.

## 3. External character-sum input

Let `E/F_p` be an elliptic curve, let `H` be a subgroup, let `omega` be a group character, and let `eta` be a nonprincipal multiplicative character of the field.

Shparlinski and Stange, *Character Sums with Division Polynomials*, Lemmas 4 and 5, record the Kummer-covering estimate

```text
abs(sum_(P in H)^* omega(P) eta(f(P))) <= 2*d*sqrt(p),  (K)
```

for a rational function `f` of degree `d` satisfying the stated geometric non-power condition. The star excludes poles.

Primary source:

```text
Igor E. Shparlinski and Katherine E. Stange,
Character Sums with Division Polynomials,
Canadian Mathematical Bulletin 55 (2012), 850-857,
arXiv:0912.5246, Lemmas 4-5.
```

For the quadratic character, an exact nonconstant decoder cannot be represented by a geometrically trivial square class. The theorem below is stated for the geometrically non-power representative required by `(K)`. Proper-power or constant-square-class candidates must first be reduced or rejected separately.

## 4. Square-root degree theorem

Assume:

1. `E(F_p)=<G>` has odd prime order `n`;
2. `f in F_p(E)` has degree `d` and satisfies the hypotheses of `(K)`;
3. `f` has neither a zero nor a pole at any nonzero subgroup point;
4. for every `1 <= k < n`,

```text
chi(f([k]G))=g_G([k]G).                              (D)
```

Choose the group character

```text
omega([k]G)=exp(-2*pi*i*k/n).
```

The exact decoder identity `(D)` implies that the twisted character sum agrees with `n*g_hat(1)`, except for at most the contribution of the identity point. Hence

```text
n*abs(g_hat(1)) <= 2*d*sqrt(p)+1.                    (B1)
```

Combining `(B1)` with `(H1)` gives

```text
d > (cot(pi/n)-1)/(2*sqrt(p)).                       (B2)
```

The uniform elementary version from `(H2)` is

```text
d > (n/(2*pi)-1)/(2*sqrt(p)).                        (B3)
```

For cofactor-one curves with `n=p+O(sqrt(p))`, this is

```text
d=Omega(sqrt(n)).                                    (B4)
```

Thus a single exact quadratic-character decoder cannot come from a rational function of degree `o(sqrt(n))`.

## 5. secp256k1 specialization

For the fixed public secp256k1 values

```text
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
```

the exact heavy-coefficient bound `(B2)` gives

```text
d > 54157620742477409023451113735280473968.01...
log2(d) > 125.3485038705...
```

The simpler uniform inequality `(B3)` still gives

```text
d > 27078810371238704511725556867640236984.00...
log2(d) > 124.3485038705...
```

Therefore every exact geometrically non-power rational-character carry decoder on secp256k1 has function degree on the order of the generic square-root scale.

### Quotient specialization

For the direct GLV quotient form

```text
f(Q)=y(Q)*R(x(Q)^3),
```

if `R` is a rational map of degree `r`, then

```text
deg(f) <= 6*r+3
```

before any cancellation. Hence `(B2)` forces approximately

```text
r > 9026270123746234837241852289213412327.50...
log2(r) > 122.7635413698...
```

for an exact decoder of this form.

This upgrades the bounded finite screen from package 010 to an asymptotic degree obstruction for the entire geometrically non-power rational-character class.

## 6. What is now closed

The result closes exact sub-square-root constructions whose public evaluation cost or explicit representation is at least linear in rational-map degree, including:

```text
bounded-degree rational coordinate predicates;
explicit divisor products of sub-sqrt support;
ordinary low-degree line-bundle sections followed by a quadratic character;
fixed-rank theta/net/sigma sections whose represented divisor degree is o(sqrt(n));
small rational quotient formulas far beyond the finite degree-four screen.
```

A candidate in these classes cannot equal the carry on every subgroup point.

## 7. What is not closed

Degree is not arithmetic-circuit size.

A straight-line circuit with repeated squaring and addition can have exponentially large algebraic degree while using only polynomially many gates. Consequently `(B2)` does **not** rule out:

```text
high-degree low-size arithmetic circuits;
iterated maps such as A_(i+1)=A_i^2+alpha_i*A_i+beta_i;
sparse huge-exponent functions evaluated by addition chains;
canonical p-adic or analytic functions with a base-field bit output;
nonlocal EDS identities not represented by one low-degree rational function;
noisy predictors with a separate robust recovery theorem.
```

The theorem proves a square-root **degree** barrier, not a universal nonlinear circuit lower bound.

## 8. Answer to package 033

```text
Can a low-degree rational-character coordinate function decode carry? no
Required rational-map degree on secp256k1                   > 2^125.34
Required quotient-map degree for R(x^3)                     > 2^122.76
Does this close explicit low-degree theta/net sections?       yes, in scope
Does this close high-degree low-circuit arithmetic formulas?  no
Public carry or hard-R3 decoder                               absent
Unconditional sub-sqrt ECDLP algorithm                        absent
```

## 9. Next exact object

The successor is

```text
SQUARE-CLASS-CIRCUIT-COMPLEXITY-034.
```

Central question:

> Can a uniformly generated arithmetic circuit of size `poly(log n)` produce a rational function `f_G(Q)` of degree at least the barrier in `(B2)` whose square class satisfies `chi(f_G(Q))=g_G(Q)` on every subgroup point, without encoding the carry partition in constants or advice?

The first theorem gates are:

1. track divisor parity rather than formal degree through `+`, `*`, inverse and Frobenius/squaring gates;
2. distinguish degree created by cheap repeated squaring from genuinely new odd divisor support;
3. prove a conductor/support growth bound in terms of addition gates and uniform constants;
4. test structured iterated-polynomial families only after an exact divisor-growth theorem is stated;
5. attach the full chosen-multiplier recovery and all-in cost model to any positive identity.

No broad random circuit or ML search is admitted without an exact structural grammar and a predeclared scaling theorem.

## 10. Formalization boundary

The accompanying Lean file kernel-checks only the real-arithmetic implication

```text
n*c <= 2*d*sqrt(p)+1
  ->
(n*c-1)/(2*sqrt(p)) <= d.
```

It does not formalize the elliptic Kummer-covering character-sum theorem, trigonometric carry coefficient, function-field degree, or the secp256k1 specialization. Those are explicit external/source-pinned premises and fixed-public numerical replays.
