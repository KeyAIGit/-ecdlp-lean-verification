# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B15: cyclic elliptic factorial standard boundary

Date: 2026-08-14

Status: **the closest root-of-unity shadow of the alternating elliptic
factorial has a constant-size local q-difference equation, but both half-factor
polynomials are dense and the alternating exponent vector has every nonzero
Fourier frequency. The known q-holonomic and ordinary block-product algorithms
operate at quasi-linear square-root complexity and require the hidden term
index or an equivalent faithful dual phase. No fixed-epsilon sub-square-root
finite-field evaluator is obtained.**

No external point, private key, wallet, unknown scalar, or production-sized
discrete-log target is accepted. Executable checks use small frozen prime
orders only.

## 1. Central target is unchanged

The central task remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all preprocessing, advice, representation, memory, branch, and online
cost charged inside

```text
O(n^(1/2-epsilon)).
```

B12 writes the alternating Miller potential as a finite elliptic shifted
factorial. B14 proves that evaluating this factorial and evaluating endpoint
segments are the same global problem.

This package asks whether the standard root-of-unity/q-holonomic realization
compresses that object below the square-root boundary.

## 2. Exact toric shadow

Let `n=2M+1` be odd and prime, and let `q` be a primitive `n`-th root of unity.
Define

```text
O_n(X)=product_(j=0)^(M-1) (1-X q^(2j+1)),
E_n(X)=product_(j=1)^M     (1-X q^(2j)),
R_n(X)=O_n(X)/E_n(X).                              (B15.1)
```

The odd and even exponent sets partition the nonzero residues, hence

```text
boxed:
O_n(X)E_n(X)
 =product_(r=1)^(n-1)(1-Xq^r)
 =(1-X^n)/(1-X).                                  (B15.2)
```

This is the multiplicative-torus analogue of the elliptic complement product
and compact involution norm from B8-B12.

## 3. Constant-size local q-difference

Shifting `X -> q^2 X` drops one endpoint and inserts one endpoint in each half
product. Since `q^n=1`,

```text
boxed:
R_n(q^2 X)/R_n(X)
 =(1-X)(1-q^2 X)/(1-qX)^2.                       (B15.3)
```

Thus the toric model reproduces the exact phenomenon found in B8:

```text
global factorial       dense,
local two-step edge    constant size.
```

The existence of `(B15.3)` is not a global evaluator. Integrating it around an
unknown endpoint requires the same segment/Hilbert-90 operation as B14.

## 4. Both half polynomials are dense

Using the finite q-binomial theorem,

```text
O_n(X)
 =sum_(r=0)^M (-1)^r q^(r^2)
    [M choose r]_(q^2) X^r,                      (B15.4)

E_n(X)
 =sum_(r=0)^M (-1)^r q^(r(r+1))
    [M choose r]_(q^2) X^r.                      (B15.5)
```

For `0<=r<=M<n`, every numerator and denominator factor in the Gaussian
binomial coefficient has exponent strictly between `1` and `n-1` modulo `n`.
Therefore none vanishes at a primitive `n`-th root.

Consequently:

```text
boxed:
every coefficient of O_n and E_n is nonzero.     (B15.6)
```

An explicit coefficient representation has `M+1=Theta(n)` field elements.
This is a coefficient-density statement, not an unrestricted circuit lower
bound.

## 5. Full linearized Fourier support

Let the exponent vector on `Z/nZ` be

```text
epsilon_0=0,
epsilon_r=+1 for odd r,
epsilon_r=-1 for even r.                         (B15.7)
```

For a nontrivial `n`-th root `z`,

```text
sum_(r=1)^(n-1) epsilon_r z^r
 =z-z^2+...-z^(n-1)
 =(z-1)/(z+1).                                   (B15.8)
```

Because `n` is odd, no nontrivial `n`-th root equals `-1`. Hence the right
side is nonzero for every `z!=1`.

Therefore:

```text
boxed:
the alternating half-factor has every
nonzero additive frequency.                      (B15.9)
```

Any representation obtained by linearizing the logarithm or by a sparse
cyclotomic-character expansion is necessarily dense.

This does not exclude a nonlinear circuit.

## 6. Known q-holonomic frontier

Bostan and Yurkevich give q-analogues of Strassen/Chudnovsky algorithms that
compute q-factorials and general q-holonomic terms in arithmetic complexity
quasi-linear in `sqrt(N)`.

Applied at length

```text
N=M=(n-1)/2,
```

that algorithmic class reaches the square-root frontier, not

```text
O(n^(1/2-epsilon))
```

for fixed `epsilon>0`.

The exact two-level tradeoff replayed in B14 gives the same boundary for
ordinary block products:

```text
baby width + giant count = Omega(sqrt(N)).        (B15.10)
```

This is a comparison with known algorithms and a lower bound for the declared
two-level block model, not a theorem that every q-holonomic algorithm is
optimal.

Primary reference:

```text
A. Bostan and S. Yurkevich,
Fast Computation of the N-th Term of a q-Holonomic Sequence and Applications,
arXiv:2012.08656.
```

## 7. The q input is not public in the elliptic problem

The toric routine assumes both:

```text
the primitive root q,
the term index m or q^m.
```

In the elliptic endpoint problem the step is the point `T=[2]G` and the
endpoint is

```text
Q=P+[m]T.
```

The numerical index `m` is hidden.

An analogue of `q^m` is a faithful dual character such as

```text
e_n(Q-P,T_dual)=zeta_n^m.
```

For secp256k1:

```text
gcd(n,p-1)=1,
ord_n(p)=(n-1)/6.
```

Thus the base field has no nontrivial `n`-th root of unity, while an explicit
dual phase has extension degree `(n-1)/6`, approximately `2^253.4`.

Supplying this phase, a dual point, or a root-of-unity state is forbidden
advice under the 056 all-in cost gate.

Therefore the known q-factorial algorithm cannot simply be imported as an
endpoint-only elliptic evaluator.

## 8. Prime-order FFT/subgroup boundary

Translation by `T` has prime order `n`. It has no nontrivial proper subgroup
chain.

FFT-like elliptic evaluation methods exploit smooth subgroup chains. The
prime-order orbit here offers no such recursive subgroup decomposition.
Artificial index blocking remains possible, but it returns to `(B15.10)` and
still requires the hidden endpoint index.

This is a structural mismatch with the standard FFT mechanism, not a universal
lower bound against all arithmetic circuits.

A relevant primary reference for elliptic-curve FFT constructions and their
use of large smooth-order subgroups is:

```text
E. Ben-Sasson, D. Carmon, S. Kopparty, D. Levit,
Elliptic Curve Fast Fourier Transform (ECFFT) Part I,
arXiv:2107.08473.
```

## 9. Root-of-unity cyclic-dilogarithm identities

Cyclic quantum dilogarithms and root-of-unity limits of elliptic gamma
functions provide exact finite-product identities, but their standard
realizations retain cyclic phase variables or finite states indexed by the
root-of-unity orbit.

The exact density and Fourier calculations above explain why simply rewriting
`R_n` as a cyclic dilogarithm does not by itself compress the oriented half
factor.

The package does not claim a theorem against every identity in that literature.
A positive result would have to descend to the base finite field, remain
generator-sensitive, and meet the full 056 cost gate without a dimension-`n`
cyclic state.

## 10. Frozen exact replay

`uorc056_cyclic_factorial_standard_boundary.py` uses primitive roots of the
small prime orders

```text
7,13,17,19,31
```

in compatible finite fields. It verifies exactly:

1. the full product identity `(B15.2)`;
2. density of both half polynomials;
3. the local q-difference identity `(B15.3)`;
4. the Fourier formula `(B15.8)`;
5. nonvanishing of every nonzero frequency;
6. the standard two-level square-root tradeoff.

No elliptic-curve target or unknown scalar is used.

## 11. Decision

```text
Constant-size local q-difference                         yes
Dense global half polynomials                            yes
Nonzero linearized Fourier support                       all n-1 frequencies
Known q-holonomic evaluation cost                        ~sqrt(n)
Meets fixed-epsilon sub-root gate                        no
Requires index m or faithful dual phase                  yes
Dual phase available cheaply in secp256k1 base field     no
Public cyclic elliptic factorial evaluator               absent
Public endpoint-only segment evaluator                   absent
Public parity oracle                                     absent
```

## 12. Closure boundary

Closed within the declared scope:

```text
explicit half-factor coefficients,
sparse cyclotomic/logarithmic expansions,
ordinary two-level baby-step/giant-step products,
direct import of indexed q-holonomic term algorithms,
standard smooth-subgroup FFT decomposition,
root-of-unity states supplied without charged dual data.
```

Still open:

```text
a genuinely nonlinear base-field identity,
a compressed distinguished Hilbert-90 lift outside explicit orbit bases,
a circuit evaluating only the required local limit on H,
an unrestricted uniform arithmetic circuit for Y_G(x(Q)).
```

The two user-facing routes are therefore closed as separate standard
mechanisms. What remains is one unrestricted global-integration circuit
problem under the unchanged central target.
