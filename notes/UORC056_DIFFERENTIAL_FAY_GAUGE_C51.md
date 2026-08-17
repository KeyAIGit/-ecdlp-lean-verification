# UORC-056 C51: differential/Fay gauge boundary

Date: 2026-08-17

Status: exact differential normal form plus scoped negative decoder boundary. The package constructs a public constant-width differential state with logarithmic index cost, then proves that the first period-shift differential loses the integer lift through an exact quasiperiod cancellation. The second and third logarithmic derivatives reduce to ordinary public coordinate functions. No cheap parity decoder, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. Central target

Let

\[
E/\mathbb F_p:y^2=x^3+7,
\qquad
H=\langle G\rangle,
\qquad
|H|=n,
\]

where \(n\) is odd and prime to \(p\). For a public point

\[
Q=[k]G,
\qquad
1\le k<n,
\]

the target remains

\[
\sigma_G(Q)=(-1)^k.
\]

C50 corrected a false high-index elliptic-net candidate. The Ward quasiperiod \(a\) is a square, so its quadratic character cannot carry parity. C51 asks whether differentiating an anchor-normalized sigma or Fay expression can break the quadratic net gauge even when the value-level character does not.

The intended mechanism is important. A high-index net value has a short addition-chain evaluator, but its multiplicative normalization is gauge-equivalent. A logarithmic derivative could, in principle, expose the exponent of the hidden gauge factor. C51 tests that possibility exactly.

## 2. Normalized rank-two sigma section

On a complex or formal uniformization, use the normalized rank-two section

\[
\Psi_{a,b}(z,w)
=
\frac{\sigma(az+bw)}
{\sigma(z)^{a^2-ab}
 \sigma(w)^{b^2-ab}
 \sigma(z+w)^{ab}}.
\]

Its first logarithmic derivative with respect to \(w\) is

\[
L_{a,b}(z,w)
=
 b\,\zeta(az+bw)
 -(b^2-ab)\zeta(w)
 -ab\,\zeta(z+w).
\]

Now specialize

\[
w=kz,
\qquad
nz=\Omega,
\]

where \(\Omega\) is a period and \(k\) is the hidden canonical scalar representative.

A period-lattice shift of the net index has the form

\[
(a,b)\longmapsto(a+rn,b+sn).
\]

Put

\[
t=a+bk.
\]

The shifted numerator argument changes by

\[
(r+sk)\Omega.
\]

Since

\[
\zeta(u+j\Omega)=\zeta(u)+j\eta,
\]

one might expect the quasiperiod \(\eta\) to expose the integer lift \(k\). The exact calculation shows that it does not.

## 3. Periodic regularized torsion jet

Define

\[
\boxed{
H(j)=j\eta-n\zeta(jz).
}
\]

It is periodic:

\[
H(j+n)=H(j).
\]

For the period shift above, define

\[
A_1
=2bs-as-rb+n(s^2-rs),
\]

\[
A_2
=as+rb+nrs.
\]

Then direct substitution and collection of all zeta and quasiperiod terms gives

\[
\boxed{
L_{a+rn,b+sn}-L_{a,b}
=-sH(t)+A_1H(k)+A_2H(k+1).
}
\]

The coefficient of the naked quasiperiod is

\[
s(a+bk)-A_1k-A_2(k+1)+(b+sn)(r+sk).
\]

It vanishes identically:

\[
\boxed{
 s(a+bk)-A_1k-A_2(k+1)+(b+sn)(r+sk)=0.
}
\]

This is the central C51 theorem.

### Interpretation

The derivative does not expose the integer lift \(k\). Every occurrence of the nonperiodic quantity \(k\eta\) cancels. The result factors through the periodic torsion state

\[
H:\mathbb Z/n\mathbb Z\to K.
\]

Thus the first differential is not a canonical-section evaluator on the universal cover. It is another descended public state on the finite subgroup.

## 4. High-index specialization

Choose

\[
(a,b)=(1,0),
\qquad
(r,s)=(0,1).
\]

The shifted section is \(\Psi_{1,n}\). The coefficients become

\[
A_1=n-1,
\qquad
A_2=1,
\qquad
t=1.
\]

Therefore

\[
\boxed{
\partial_Q\log\Psi_{1,n}(G,Q)
=-H(G)+(n-1)H(Q)+H(Q+G).
}
\]

This is a positive algorithmic result. Each term is evaluable by a fixed-order local division-polynomial recurrence with index \(n\), so the field-operation count is polynomial in \(\log n\) for fixed truncation order.

It is not a parity decoder. The entire expression is periodic in the subgroup point and contains no surviving canonical-lift phase.

## 5. Higher logarithmic derivatives collapse further

Use

\[
\zeta'(z)=-\wp(z),
\qquad
\wp(z)=x(P),
\qquad
\wp'(z)=2y(P).
\]

The second logarithmic derivative is

\[
\boxed{
\partial_Q^2\log\Psi_{1,n}(G,Q)
=-n^2x(G)+(n^2-n)x(Q)+n x(Q+G).
}
\]

The third is

\[
\boxed{
\partial_Q^3\log\Psi_{1,n}(G,Q)
=-2n^3y(G)+2(n^2-n)y(Q)+2n y(Q+G).
}
\]

Both are ordinary public coordinate expressions. They have short evaluators, but they do not carry a new branch normalization.

The same pattern persists conceptually for higher derivatives: after the first zeta level, derivatives are elliptic functions and therefore descend to public algebraic coordinate data. C51 does not claim a theorem for every arbitrarily mixed higher Fay derivative, but it closes the declared one-section logarithmic ladder through order three and identifies the reason for the collapse.

## 6. Finite-field regularization

For a nonzero prime-to-characteristic \(n\)-torsion point \(P=(x,y)\), expand the division polynomial in the local x-chart:

\[
\psi_n(x+T)=c_1T+c_2T^2+c_3T^3+\cdots.
\]

Separability gives

\[
c_1\ne0.
\]

The invariant local parameter has derivation

\[
D_\omega=2y\frac{d}{dx}.
\]

The regularized finite part corresponding to the periodic zeta state is

\[
R_n(P)
=
\frac{3x(P)^2}{2y(P)}
+2y(P)\frac{c_2}{c_1},
\]

and C51 uses

\[
\boxed{
H_n(P)=\frac{R_n(P)}{n}.
}
\]

Only a constant number of local coefficients is required. The division-polynomial recursion halves the public index, so this state has an \(O(\log n)\) addition-chain description at fixed precision.

## 7. Exact symmetry of the torsion jet

The replay verifies on every declared prime-to-characteristic curve:

\[
\boxed{H_n(-P)=-H_n(P).}
\]

For the \(j=0\) GLV endomorphism

\[
\phi(x,y)=(\beta x,y),
\qquad
\beta^3=1,
\]

it also verifies

\[
\boxed{H_n(\phi P)=\beta^2H_n(P).}
\]

Thus \(H_n\) is a public GLV eigenfunction. It is not the marked ordered-sector root \(J_G\). It depends on the point and the public subgroup order, not on the canonical scalar labeling relative to a chosen generator.

The symmetry implies the CM form

\[
\boxed{
H_n(P)
=
\frac{x(P)^2}{y(P)}R_n(x(P)^3)
}
\]

on the nonexceptional chart. The interpolated quotient polynomial \(R_n\) is dense on all 12 declared curves. Its degree is within nine of the full interpolation ceiling in the complete corpus. This is finite representation evidence, not an unrestricted circuit lower bound.

## 8. Exact finite replay

The separable corpus contains four inherited frozen curves and eight held-out curves:

```text
frozen:
(p,n)=(43,31),(67,79),(79,67),(163,139)

held out:
(p,n)=(97,79),(211,199),(349,313),(433,397),
      (577,613),(733,691),(823,829),(907,967)
```

For every curve, the replay checks the full nonzero subgroup for the torsion jet and the regular chart \(2\le k\le n-2\) for the net logarithmic derivatives.

Aggregate result:

```text
12 curves
4 frozen
8 held out
4,392 torsion-jet rows
4,368 first-derivative identities
4,368 second-derivative identities
4,368 third-derivative identities
73,500 exact quasiperiod coefficient cancellations
all H states have mixed-parity collisions
all declared affine character survivors are zero
all CM quotient polynomials are dense
maximum degree deficit from interpolation ceiling: 9
0 arithmetic errors
```

### Decoder screen

For each curve, C51 exhaustively tests the simplest affine quadratic-character families

\[
\chi(H_n(Q)+c),
\]

\[
\chi(\partial_Q\log\Psi_{1,n}(G,Q)+c),
\]

\[
\chi(\Psi_{1,n}(G,Q)+c),
\qquad c\in\mathbb F_p.
\]

Neither phase is accepted as a free fitted global sign unless it is exact on the complete regular chart. The number of exact survivors is zero in every family on every curve.

This closes only the declared affine-character grammar. It does not claim that no nonlinear function of several \(H\)-values can ever decode parity.

## 9. Anomalous controls

The curves

```text
(p,n)=(127,127),(61,61)
```

are deliberately excluded from the separable torsion-jet claim. Here the subgroup order equals the field characteristic. The local series for \(\psi_p\) is inseparable or degenerate; the first four coefficients vanish in the declared chart.

This is a domain correction, not a failed test. secp256k1 is prime to characteristic:

\[
p\ne n,
\qquad
n\in\mathbb F_p^\times.
\]

## 10. secp256k1 certificate

The package independently verifies the public generator order and evaluates the constant-truncation division and net recurrences at public scalar samples.

It records:

```text
chi(Ward a) = +1
chi(Ward b) = -1
14 public H_n samples
9 first-derivative checks
9 second-derivative checks
9 third-derivative checks
```

The Ward result preserves the C50 correction. The phase that had been proposed as parity is a square. The differential state is real and fast, but the exact identities show that it is periodic rather than a canonical-lift bit.

## 11. Gauge interpretation

Under the ordinary quadratic net scaling

\[
W_v\longmapsto c^{q(v)}W_v,
\]

a derivative taken only along the elliptic point coordinate treats \(c\) as constant. It therefore cannot see \(d\log c\).

The sigma derivation reaches the same conclusion more sharply. A period shift appears to inject a quasiperiod proportional to the hidden lift, but the preferred-basis normalization forces exact cancellation. The surviving object is the periodic finite part \(H_n\).

Therefore the first differential/Fay route does not break the section gauge:

\[
\boxed{
\text{horizontal point differentiation preserves the descended net gauge.}
}
\]

## 12. Decision

```text
Fast regularized torsion jet                         found
Fast anchor-mixed high-index derivative              found
First derivative exposes the integer lift            no
Naked quasiperiod survives preferred normalization   no
Second derivative carries new branch data            no
Third derivative carries new branch data             no
Affine character decoder on the declared corpus      no
Cheap exact parity decoder                           not found
Parity oracle                                        not found
Sub-square-root ECDLP                                 not found
```

The main exact conclusion is

\[
\boxed{
\text{the differential attack descends from the cover to periodic torsion jets.}
}
\]

## 13. Successor: C52 nonhorizontal deformation gauge

A derivative can detect the quadratic scale only if the scale itself varies. The next valid mechanism must therefore differentiate in a direction that is not merely the elliptic point coordinate.

C52 is

```text
NONHORIZONTAL-DEFORMATION-GAUGE-C52
```

and must specify a family

\[
(E_t,G_t,Q_t)
\]

satisfying

\[
Q_t=[k]G_t
\]

without receiving \(k\) as an input.

It must then determine whether a curve, moduli, p-adic, Gauss-Manin, or sigma-parameter derivative produces a gauge term whose coefficient reveals parity.

Mandatory gates:

1. the deformation and connection are public and functorial;
2. preservation of the relation \(Q=[k]G\) does not inject the hidden scalar into the tangent data;
3. the chosen trivialization is stated and charged;
4. any p-adic or extension precision is included in the cost;
5. branch normalization is not supplied as advice;
6. frozen and held-out curves are both tested;
7. a positive candidate must give a literal decoder and a complete all-in cost ledger.

A deformation whose tangent relation explicitly contains the unknown multiplier \(k\) is not a decoder. It has moved the secret from the point relation into the derivative input.

## 14. Claim boundary

C51 does not claim:

1. an unrestricted differential-circuit lower bound;
2. an unrestricted Fay, sigma, or theta lower bound;
3. nonexistence of every nonlinear decoder using several torsion jets;
4. a production-size coefficient-density theorem for secp256k1;
5. a parity oracle;
6. a sub-square-root ECDLP algorithm.

It gives an exact differential normal form, a kernel-checked quasiperiod cancellation, deterministic full-orbit replay on 12 prime-to-characteristic curves, public secp256k1 sample verification, and a precise successor gate.
