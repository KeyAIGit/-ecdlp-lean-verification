# RELATIVE-RESIDUE-GAUGE-001

Date: 2026-08-11
Status: isolated, non-executable structural result

This note targets no external point, wallet, or production discrete-log
instance. It changes no canonical Research Engine state and makes no universal
non-generic lower-bound claim.

## 1. Target and public relative primitive

Let `G` generate a cyclic subgroup of odd prime order `n`, and let

```text
Q = [k]G,   0 < k < n.
```

Write

```text
W(t) = psi_t(G),
rho(t) = chi(W(t)),
```

where `chi` is the quadratic character. The unresolved absolute bit is

```text
rho_G(Q) = rho(k).
```

Lauter and Stange prove that the adjacent relative sign

```text
rho(k+1) * rho(k)
```

is computable from public `G`, `Q`, and `Q+G` in polylogarithmic field time.
Thus a public local edge oracle exists. It determines a connected residue
window only up to one simultaneous global sign.

## 2. Exact rank-two net specialization

Apply the elliptic-net transformation formula to the rank-two point tuple

```text
(G,Q) = (G,[k]G)
```

and a fixed vector `(a,b)`. The exact raw-net identity is

```text
W_(G,Q)(a,b)
  * W(k)^(b^2-a*b)
  * W(k+1)^(a*b)
  = W(a+b*k).
```

Taking quadratic characters, and writing

```text
r(k) = rho(k+1)*rho(k),
nu_(a,b)(Q) = chi(W_(G,Q)(a,b)),
```

gives

```text
nu_(a,b)(Q) * r(k)^(a*b)
  = rho(a+b*k) * rho(k)^(b^2).          (R)
```

Every term on the left is public for fixed `(a,b)`.

Consequences:

1. If `b` is odd, equation (R) gives the relative label

   ```text
   rho(a+b*k) * rho(k).
   ```

   It is invariant under the global replacement `rho -> -rho`.

2. If `b` is even, equation (R) gives the raw integer-index residue

   ```text
   rho(a+b*k).
   ```

   After reducing `a+b*k` modulo the subgroup order, the period carry restores
   the missing normalization sign. The resulting canonical-point expression is
   the already-public perfectly periodic point-function character, not a new
   absolute decoder. `EVEN-PULLBACK-COLLAPSE-001` records this explicitly for
   every fixed even pullback.

## 3. Quadratic gauge cancellation

The normalization defect in the rank-two formula is exactly

```text
(a+b*k)^2
  - (b^2-a*b)*k^2
  - a*b*(k+1)^2
  = a*(a-b).
```

The right side is independent of the hidden index `k`. Therefore a quadratic
net rescaling

```text
W(t) -> alpha^(t^2) W(t)
```

cancels from the transported relation up to a fixed public constant depending
only on `(a,b)`.

This identity is formalized in
`Ecdlp/Proved/RelativeResidueGauge.lean` as:

- `rankTwoNetQuadraticDefect`;
- `rankTwoNetQuadraticBalance`;
- `pairLabel_invariant_under_globalNegation`.

## 4. Fixed-rank generalization

The same obstruction is not special to rank two. Let fixed affine indices be

```text
l_i(k) = a_i + b_i*k
```

and fixed net coefficients be `v_i`. Put

```text
L(k) = sum_i v_i*l_i(k),
e_i = 2*v_i^2 - v_i*sum_j v_j.
```

The net-transformation exponents satisfy the exact quadratic-form identity

```text
L(k)^2
  = sum_i e_i*l_i(k)^2
    + sum_(i<j) v_i*v_j*(l_i(k)+l_j(k))^2.
```

Thus every identity obtained solely by pulling back a fixed-rank elliptic net
along fixed affine combinations is invariant under the same quadratic gauge.
Increasing rank, adding more public affine combinations, or inserting a fixed
CM endomorphism does not by itself create an absolute residue anchor.

This is a mechanism-level closure, not a claim that every possible use of an
elliptic net is hard. A proposal can escape only by introducing information
that is not invariant under quadratic net equivalence.

## 5. Graph interpretation

View public relative labels as edges of a graph whose vertices are residue
values at public affine transforms of `Q`. On every connected component the
edge labels reconstruct all vertex signs once one sign is chosen, but both
assignments

```text
rho(v)
and
-rho(v)
```

satisfy every pairwise edge equation.

Cycles check consistency but cannot select between the two gauges. Reaching the
known anchor `rho(1)=1` by generic orbit navigation requires finding the hidden
index relation to `G`; birthday methods return the familiar square-root scale.
A sub-square-root result therefore needs an absolute odd-degree equation or an
absolute section, not more relative edges of the same type.

## 6. Biased-isogeny boundary for secp256k1

Stange's arbitrary-isogeny division-polynomial theory identifies extra root
factors for biased isogenies. A biased isogeny's kernel sum is a nonzero
2-torsion point.

For an isogeny defined over the base field, that kernel sum is Frobenius fixed.
secp256k1 has no nonzero rational 2-torsion, since its full rational point group
has odd prime order. Hence an `F_p`-defined secp256k1 endomorphism cannot supply
this particular biased-isogeny root anchor.

This is a scoped deduction pending dedicated source and formal binding. It does
not rule out an extension-field construction, but Frobenius descent or norming
can erase exactly the root phase one hoped to retain.

## 7. Current decision

The standard relative-residue route is now sharply classified:

```text
fixed net transformations -> public relative labels -> one global sign gauge
```

No amount of connected relative information fixes the absolute EDS residue
without one additional non-gauge-invariant anchor.

The next admissible positive mechanism must be one of:

1. an absolute root or theta-characteristic phase;
2. a biased isogeny correction that survives descent;
3. a p-adic or analytic normalization with exact precision and cost;
4. a nonlocal relation containing an odd number of absolute residue factors;
5. another observable proved not to be invariant under quadratic net
   equivalence.

`CM-QUARTIC-ANCHOR-001` records the first bounded toy witness that such an
absolute root-phase class is not empty, although it does not transfer directly
to secp256k1 and does not scale in the current controls.

## Primary mathematical anchors

- Katherine E. Stange, *Elliptic Nets and Elliptic Curves*, Proposition 4.3,
  for the exact net transformation formula.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*, Proposition 4, for public adjacent residue ratios.
- Katherine E. Stange, *Division Polynomials for Arbitrary Isogenies*, for
  biased-isogeny correction functions and generalized chain rules.
