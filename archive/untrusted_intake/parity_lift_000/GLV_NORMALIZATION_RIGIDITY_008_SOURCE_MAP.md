# GLV-NORMALIZATION-RIGIDITY-008 — source map

This file records the source-to-claim boundary for the scoped theorem.

## Stange, *Elliptic Nets and Elliptic Curves*

Source-supported inputs:

1. net polynomials are defined by sigma quotients with quadratic exponents;
2. integral matrices induce the stated net-polynomial transformation law;
3. multiplying an elliptic net by a quadratic form preserves the recurrence;
4. every non-degenerate net has a unique normalized scaling;
5. the explicit rank-three polynomial `Psi_(1,1,1)` has the alternating
   numerator used in the GLV common-`y` cancellation.

Repository inference built from these inputs:

- the homogeneous net/theta operations in `C_quad` preserve a quadratic
  normalization exponent;
- fixed-rank pullbacks cannot create an additional binary normalization class.

The full category-theoretic statement about line bundles and jet bundles is not
claimed as source-verbatim or fully formalized.

## Lauter–Stange, *The Elliptic Curve Discrete Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility Sequences*

Source-supported inputs:

1. the perfectly periodic point function is a quadratic normalization of the
   original EDS;
2. it is evaluable from the public point without the hidden multiplier;
3. an exact parity oracle recovers the full discrete logarithm;
4. an EDS-residue oracle yields parity under the stated hypotheses;
5. adjacent EDS-residue ratios are publicly computable.

Repository inference built from these inputs:

- the point-function C3 norm supplies the known `g*R3` equation;
- a section separating either factor would enter the established recovery
  pipeline.

## Formal boundary

Lean formalizes only the integer parity identities, fixed-rank coefficient
cancellation, common-`y` rank-three numerator cancellation, and the fact that an
order-three eigenvalue is a square. It does not formalize the cited papers,
elliptic line bundles, theta groups, or asymptotic cost.
