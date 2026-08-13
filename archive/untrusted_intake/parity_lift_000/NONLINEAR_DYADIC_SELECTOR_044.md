# NONLINEAR-DYADIC-SELECTOR-044

Date: 2026-08-12

Status: **exact degree-state tradeoff and full Fourier-support obstruction for rational and translation-linear dyadic selectors; genuinely nonlinear short high-degree circuits remain open**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 043

For

```text
Q=[k]G,
k=2^d q+r,
0<=r<2^d,
```

package 043 proved that `d` public group halvings leave exactly the hidden residue

```text
r=k mod 2^d.
```

An explicit branch representation requires `2^d` distinct affine corrections. The only possible escape is a nonlinear compressed selector.

Put

```text
m=2^d<n.
```

The present package studies two broad exact representations of the selector `k -> k mod m`:

1. one rational function with `m` distinct output labels;
2. one bounded-dimensional translation-linear or transfer-matrix state.

## 2. Rational-selector degree tradeoff

Suppose a nonconstant rational function `f` on the elliptic curve has distinct constants

```text
c_0,...,c_(m-1)
```

and satisfies

```text
f([k]G)=c_(k mod m)
```

for every nonzero subgroup point.

Then the rational function

```text
P(f)=product_(r=0)^(m-1) (f-c_r)
```

vanishes on all `n-1` nonzero subgroup points. If `D=deg(f)`, its zero divisor has degree at most `mD`. Therefore

```text
mD >= n-1,                                      (N1)
D >= ceil((n-1)/m).                             (N2)
```

Equivalently, for `m=2^d`,

```text
2^d * deg(f) >= n-1.                            (N3)
```

Consequences for secp256k1:

```text
d=1     -> degree at least (n-1)/2  approximately 2^255,
d=64    -> degree at least          approximately 2^192,
d=96    -> degree at least          approximately 2^160,
d=128   -> degree at least          approximately 2^128.
```

Thus a single exact rational selector reaches the Pollard degree frontier exactly when the explicit branch count does.

This is a representation-degree bound, not an arithmetic-circuit lower bound. Repeated squaring can represent very high degree with small multiplication depth, so coefficient generation, normalization, and evaluation cost must still be analysed separately.

## 3. Full Fourier support of one dyadic residue class

Fix a residue `r` with `0<=r<m`. Define on canonical representatives `0<=k<n`

```text
I_(m,r)(k)=1 if k mod m=r,
             0 otherwise.
```

Let `omega` be a primitive `n`-th root of unity. The nonzero positions are

```text
r, r+m, ..., r+(L_r-1)m,
L_r=floor((n-1-r)/m)+1.
```

The cyclic Fourier coefficient is

```text
Ihat_(m,r)(j)
 =omega^(-jr) *
  [1-omega^(-j*m*L_r)]/[1-omega^(-j*m)]          (N4)
```

for `j!=0`, while the zero-frequency coefficient is `L_r`.

Because `n` is prime, `m<n`, `j!=0 mod n`, and `0<L_r<n`:

```text
n does not divide j*m,
n does not divide j*m*L_r.
```

Hence neither denominator nor numerator in `(N4)` vanishes. Therefore

```text
support(Ihat_(m,r)) = Z/nZ                       (N5)
```

for every dyadic residue class.

The one-bit parity indicator is the special case `m=2`; its full support is the odd-cycle wrap defect in Fourier language.

## 4. Translation-linear state obstruction

Consider an exact state representation over a characteristic-zero splitting field:

```text
state(k)=T^k v,
output(k)=ell(state(k)),
T^n=I.
```

Since the characteristic does not divide `n`, `T` is semisimple. A `D`-dimensional state produces a scalar output sequence that is a linear combination of at most `D` additive characters of `Z/nZ`. Its Fourier support therefore has size at most `D`.

By `(N5)`, an exact indicator of even one dyadic residue class requires

```text
D >= n.                                         (N6)
```

Thus no bounded-rank linear theta state, fixed transfer matrix, or linear recurrence state can compress the selector. The standard exact linear state is as large as the entire cyclic group.

This theorem does not apply to nonlinear state updates or nonlinear output maps.

## 5. Unary deterministic-state version

The cyclic sequence `I_(m,r)` is nonconstant. Since `n` is prime, its fundamental cyclic period is exactly `n`.

A deterministic unary state machine whose next state depends only on the current state and whose output is read from the state cannot generate a period-`n` sequence with fewer than `n` states on its recurrent orbit.

This gives the same lower bound as `(N6)` without linear algebra, but only for sequential one-step state machines.

## 6. Combined interpretation

The two most natural compression formats now satisfy:

```text
explicit affine branches                  at least 2^d states,
one rational m-label selector             degree at least (n-1)/2^d,
translation-linear selector               dimension at least n.
```

The product tradeoff

```text
(number of dyadic labels) * (rational degree) >= n-1
```

is the algebraic analogue of the checkpoint-space tradeoff found in the cocycle branch.

## 7. Frozen exact replay

`nonlinear_dyadic_selector.py` verifies for frozen odd primes and every dyadic `m<n`:

1. all residue classes have the stated arithmetic-progression support;
2. the exact geometric-series nonvanishing conditions for every nonzero Fourier frequency;
3. full Fourier support of every residue indicator;
4. fundamental cyclic period `n`;
5. the degree-state product certificate;
6. secp256k1 degree bounds at depths `1,64,96,128`.

The replay checks the exact integer divisibility conditions behind `(N4)`, not floating-point Fourier approximations.

## 8. Answer

```text
Can explicit branches compress below 2^d states?           not in the branch-list model
Can one bounded-degree rational selector do it?             no
Exact rational degree tradeoff                              2^d D >= n-1
Can a bounded-dimensional linear theta/transfer state?      no
Exact linear-state dimension                                at least n
Does this exclude nonlinear short high-degree circuits?     no
Public parity / EDS-residue decoder                         absent
Unconditional classical sub-sqrt ECDLP                     absent
```

## 9. Next object

The surviving class is

```text
PARITY-DIVISOR-SYMMETRY-045.
```

Its first exact question is:

> What automorphisms of the secp256k1 subgroup preserve the canonical parity divisor, and can any CM/GLV/Frobenius quotient reduce its effective degree?

A key candidate theorem is that the multiplier stabilizer of the nonzero even canonical scalars is trivial. If true, the parity divisor has no nontrivial scalar symmetry, so GLV and unit quotients cannot reduce its orbit count. The package will then quantify the degree and circuit consequences while keeping open genuinely coordinate-sensitive nonlinear identities.

## 10. Formalization boundary

`Ecdlp/Proved/NonlinearDyadicSelector.lean` formalizes the elementary class-degree tradeoff, the implication from full Fourier support to a state-dimension bound, and the cardinality consequences. It does not formalize elliptic-curve divisor degrees, cyclotomic Fourier analysis, semisimplicity of the translation operator, general arithmetic circuits, or ECDLP.
