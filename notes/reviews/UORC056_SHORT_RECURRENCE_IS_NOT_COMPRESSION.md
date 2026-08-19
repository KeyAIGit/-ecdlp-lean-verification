# UORC-056 A Short Recurrence Is Not Yet Compression

## Status

Proved conceptual boundary and corrected engine admission rule.

## Exact counterexample to the naive implication

In the primitive character coordinate of the cyclic group, define the truncated product

`P_m(z)=product_{j=0}^{m-1}(z-q^j)`.

It obeys the first-order recurrence

`P_{m+1}(z)=(z-q^m) P_m(z)`.

The recurrence width is one. Its description is constant-size.

Nevertheless, evaluating `P_m` for `m` of size approximately `n/2` is not automatically a `poly(log n)` computation. Sequential evaluation uses `m` multiplications.

The exact rational parity decoder from the character-coordinate theorem is built from two such half-cycle products. Thus exact parity already has a constant-width recurrence in this idealized coordinate, while no polylogarithmic random-access evaluator follows.

## Known generic acceleration

Truncated q-products and more general q-holonomic sequences admit baby-step/giant-step algorithms with arithmetic complexity quasi-linear in `sqrt(m)`. This improves the sequential cost but remains exponential in `log n` when `m` is proportional to `n`.

Reference: Alin Bostan and Sergey Yurkevich, *Fast Computation of the N-th Term of a q-Holonomic Sequence and Applications*, Journal of Symbolic Computation 115 (2023), 96-123; arXiv:2012.08656.

## Correct implication

A recurrence contributes to H-PCX only if the campaign also proves a jump-ahead theorem:

- the transition product from step `0` to step `m` is computable in `poly(log n)` time;
- all coefficients needed at distant indices are publicly computable;
- no product tree, multipoint table, extension, or advice of superpolynomial size is hidden;
- branch and normalization choices are exact and public.

Therefore the valid target is not

`small recurrence order`,

but

`small recurrence order + polylogarithmic random access`.

## Consequence for theorem search

The following observations alone are insufficient:

- recurrence width is constant;
- a state has only a few components;
- each local transition is cheap;
- the recurrence is q-holonomic;
- divide-and-conquer depth is logarithmic while the number of leaves remains linear.

The engine must record both:

1. state width;
2. total work needed to reach the target index.

## Remaining positive mechanisms

A short recurrence can still lead to H-PCX if one proves additional structure such as:

- commuting or simultaneously diagonalizable transitions;
- repeated-squaring of one fixed transition;
- a closed composition law for long segments;
- a polylogarithmic-size product certificate;
- a special CM/theta identity collapsing the half-cycle product;
- modular composition with total degree and representation cost controlled polynomially in `log n`.
