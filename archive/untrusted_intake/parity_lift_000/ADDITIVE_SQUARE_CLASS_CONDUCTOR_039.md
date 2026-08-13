# ADDITIVE-SQUARE-CLASS-CONDUCTOR-039

Date: 2026-08-12

Status: **exact square-class innovation decomposition and explicit one-addition conductor blow-up; the proposed addition-count-only lower-bound route is rejected**.

Package number 038 was already reserved by the synchronized parent line for the quadratic-Weil orientation successor. This independent circuit-complexity pass is therefore numbered 039.

No external point, private key, wallet, or production-sized discrete-log target is accepted. No carry, hard-R3, parity, or ECDLP decoder is constructed.

## 1. Target of the pass

The surviving exact target is

```text
chi_p(F_G(Q)) = g_G(Q) = g_G(G)*sign(U_G(Q))
```

for every nonzero `Q in <G>`, with one uniform reusable circuit and total cost below the generic square-root baseline.

The preceding rational-character package proves that any geometrically non-power rational `F_G` reproducing carry has degree `Omega(sqrt(n))`. That degree theorem does not exclude a small circuit because repeated squaring creates exponential formal degree.

This pass asks whether the **odd divisor support** or the conductor of the quadratic Kummer cover

```text
Y^2 = F_G
```

can turn the degree obstruction into a lower bound on the number of addition/subtraction gates.

## 2. Square-class innovation theorem

Let

```text
K = F_p(E),  p odd,
Sq(K)=K^*/K^{*2}.
```

For nonzero functions, multiplication, inversion, squaring, odd powers, and Frobenius behave in square class as

```text
[FG]       = [F]+[G],
[F^(-1)]   = [F],
[F^2]      = 0,
[F^(2m+1)] = [F],
[F^p]      = [F].
```

At an addition gate, for `A != 0`,

```text
A+B = A*(1+B/A),
[A+B] = [A] + [1+B/A].                         (I1)
```

Therefore an arithmetic circuit with addition gates indexed by `i` has output square class in the `F_2` span of

```text
initial input square classes,
[1+R_i],  R_i=B_i/A_i,
```

where `R_i` is the ratio at the `i`-th addition gate.

This is an exact structural reduction. Additions are the only ordinary gates that introduce new square-class generators.

## 3. Conductor budget with degree-weighted additions

For `F in K^*`, define the geometric odd-support degree

```text
c_2(F)=sum_v (ord_v(F) mod 2)*deg(v).
```

It is the ramification-divisor degree of the quadratic extension `K(sqrt(F))/K` in odd characteristic. On an elliptic base curve, Riemann-Hurwitz gives

```text
g(K(sqrt(F))) = 1 + c_2(F)/2
```

when the extension is nontrivial.

Square-class multiplication takes symmetric difference of odd supports, hence

```text
c_2(FG) <= c_2(F)+c_2(G).
```

For a nonconstant rational map `R:E -> P^1`, every odd zero or pole of `1+R` lies over `-1` or infinity. Thus

```text
c_2(1+R) <= 2*deg(R).                            (I2)
```

Combining `(I1)` and `(I2)`, any circuit output satisfies the scoped budget

```text
c_2(F_out)
 <= sum_j c_2(input_j)
    + 2*sum_(addition gates i) deg(R_i).          (I3)
```

Consequently the right additive resource is not the **number** of additions. It is at least the degree-weighted innovation budget

```text
B_add(C)=sum_i deg(R_i).
```

A carry decoder subject to the earlier character-sum barrier must have a square-root-scale degree or conductor somewhere in this budget. However, circuit size does not control `B_add` strongly because squaring can make one `R_i` enormous at logarithmic gate cost.

## 4. Explicit one-addition counterfamily

Work over an algebraic closure of a field of odd characteristic on

```text
E: y^2=x^3+7.
```

For `m>=1`, put

```text
d=2^m,
h_m(T)=T^d-T,
F_m(Q)=h_m(x(Q))=x(Q)^(2^m)-x(Q).
```

The circuit is uniform and uses exactly

```text
m squarings,
1 subtraction,
0 fitted constants.
```

Assume `p` does not divide `d-1`. Then `h_m` is separable:

- at `T=0`, `h_m'(0)=-1`;
- at a nonzero root, `T^(d-1)=1`, hence `h_m'(T)=d-1 != 0`.

The map `x:E -> P^1` has degree two. Its three finite branch values are the roots of

```text
T^3+7.
```

Let

```text
b_m = deg gcd(T^(2^m)-T, T^3+7),
0 <= b_m <= 3.
```

Every root of `h_m` outside the three branch values lifts to two simple zeros of `F_m`. A branch-value root lifts to one zero of even order two and does not contribute to odd support. At the point at infinity, `F_m` has pole order `2d`, also even. Therefore

```text
c_2(F_m)=2*(2^m-b_m) >= 2*(2^m-3).             (C1)
```

The associated quadratic cover has genus

```text
g_m=1+2^m-b_m.                                 (C2)
```

Thus **one additive gate** creates exponentially large odd divisor support and exponentially large Kummer-cover genus.

## 5. Exact secp256k1 specialization

For the fixed public secp256k1 prime `p`, modular polynomial exponentiation gives

```text
m=127,
gcd(T^(2^127)-T, T^3+7)=1,
b_127=0.
```

Also `p` does not divide `2^127-1`. Hence

```text
c_2(F_127)=2^128.
```

For the secp256k1 subgroup order `n`,

```text
floor(sqrt(n))=2^128-1.
```

Therefore

```text
c_2(F_127) > floor(sqrt(n))
```

with a circuit using only

```text
127 squarings + 1 subtraction = 128 arithmetic gates,
1 additive innovation.
```

`F_127` is not claimed to decode carry and can vanish on subgroup points. It is a counterexample to the proposed **proof method**: large conductor cannot imply many additions or super-polylogarithmic circuit size.

## 6. Consequence for the planned lower bound

The hoped-for implication

```text
large carry conductor -> many addition gates
```

is false without an additional restriction on the degrees or descriptions of the ratios entering the additions.

More generally, a size-`s` straight-line circuit from bounded-degree inputs can have degree and conductor exponential in `s`. A square-root-scale lower bound therefore yields at best

```text
s = Omega(log n),
```

which is compatible with the desired `poly(log n)` attack class and cannot close it.

The following proposed invariants are insufficient by themselves:

```text
formal rational-map degree,
odd divisor support,
Kummer-cover conductor,
Kummer-cover genus,
number of addition gates.
```

They remain useful only when combined with restrictions on the pre-addition maps, uniform constants, functional decomposition, monodromy, or orbit-label complexity.

## 7. Exact one-addition normal form

If a circuit starts from affine inputs `x,y` and field constants, uses arbitrary multiplication, inversion and squaring, and has exactly one addition gate, then before that gate its two operands are Laurent monomials. Factoring one operand shows that, modulo a final monomial square class, its only new class has the form

```text
[1+c*x^a*y^b].                                  (N1)
```

Subsequent multiplication, inversion and powering can only retain or remove this one innovation modulo squares.

Hence the first genuinely classifiable surviving grammar is not “all circuits with few additions.” It is the one-addition family

```text
F(Q)=M_0(Q)*(1+c*M_1(Q)),
M_i(Q)=x(Q)^a_i*y(Q)^b_i,
```

with exponents given by short addition chains and constants generated uniformly from `(p,n,E,G,phi)`.

The exact GLV and negation laws further divide this family into:

1. function-level invariant innovations, naturally depending on `x^3` and `y^2`;
2. anti-invariant innovations involving odd powers of `y`;
3. exceptional pointwise-character identities that are invariant only after applying `chi_p`.

The first branch includes the direct quotient shape already isolated in package 010, but now with huge addition-chain exponents rather than bounded rational degree.

## 8. Answer

```text
Can odd-support conductor be bounded by addition count alone?      no
Exact innovation generators of an A-addition circuit               at most A
Can one innovation have exponential conductor?                     yes
Explicit family                                                     x^(2^m)-x
Additions in the family                                             1
Total gates needed to exceed sqrt(n) conductor on secp256k1         128
Does this family decode carry?                                      no claim
Does conductor yield a super-polylog circuit lower bound?           no
Public carry / hard-R3 decoder                                      absent
Sub-square-root ECDLP algorithm                                     absent
```

## 9. Successor

The successor is

```text
ONE-ADDITION-SQUARE-CLASS-NORMAL-FORM-040.
```

Central question:

> Can any uniformly generated one-addition square class
>
> ```text
> [M_0(Q)*(1+c*M_1(Q))]
> ```
>
> with short exponent addition chains satisfy
>
> ```text
> chi_p(F(Q))=g_G(Q)
> ```
>
> on every nonzero secp256k1 subgroup point, while remaining total and reusable on every chosen multiple `[t]Q`?

The theorem-first obligations are:

1. formalize the exact one-addition normal form for the admitted coordinate grammar;
2. impose GLV invariance and negation anti-invariance before any search;
3. reduce exponents by the function-field and finite-field relations without confusing formal degree with square class;
4. derive character-sum or functional-decomposition obstructions that depend on the **short exponent description**, not merely degree;
5. if a surviving family remains, conduct an exact toy screen over predeclared exponent-addition-chain families;
6. reject any constants encoding labels, a dual orbit, an orientation table, or a faithful order-`n` phase;
7. attach the exact chosen-multiplier recovery and all-in cost audit to any positive identity.

No universal arithmetic-circuit lower bound is claimed. The result of this pass is the rejection of a specific lower-bound invariant and the isolation of the first exact nonlinear grammar worth classifying.

## 10. Formalization boundary

`Ecdlp/Proved/AdditiveSquareClassConductor.lean` formalizes:

```text
addition as a single square-class innovation;
iterated squaring as a power-of-two tower;
the exact one-subtraction family x^(2^m)-x.
```

It does not formalize elliptic curves, valuations, divisors, Riemann-Hurwitz, conductor, separability, secp256k1 polynomial gcds, circuit lower bounds, or carry correctness. Those are explicit mathematical arguments and fixed-public arithmetic replays in this package.
