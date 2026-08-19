# UORC-056 H-RPCX rational DAG degree floor V8

## Status

Scoped paper theorem with exact secp256k1 arithmetic replay and a Lean-checked numerical endpoint.

This is a genuine DAG cost statement: a shared intermediate value is charged once and may be reused. It is not the formula-tree model corrected in V5.

The result does not prove that a 254-gate decoder exists, and it does not rule out polynomial-time parity algorithms.

## Model

Let `f` be one rational function on secp256k1, constructed from:

- public field constants;
- the coordinate functions `x` and `y`;
- addition, subtraction and multiplication;
- inversion of nonzero intermediate rational functions.

The computation is a directed acyclic graph. Each binary arithmetic node is counted once even when its output is reused many times.

Assume `f` is regular at every nonzero point of the prime-order subgroup and returns exact canonical parity:

`f([k]G)=+1` for even `k`, and `f([k]G)=-1` for odd `k`.

## Lower bound from the target

There are `n-1` nonzero subgroup points. Since the target takes both signs, `f` is nonconstant.

The function

`f^2-1`

vanishes at every one of those points. On a smooth projective curve, a nonzero rational function has equally many zeros and poles when multiplicity is counted. The pole degree of `f^2-1` is at most twice the pole degree of `f`.

Therefore

`pole_degree(f) >= (n-1)/2`.

This is the V2 divisor argument specialized to a direct decoder.

## Upper bound from a rational DAG

On a short Weierstrass elliptic curve:

- `x` has pole degree `2`;
- `y` has pole degree `3`;
- constants have pole degree `0`.

For rational functions `a` and `b`:

- the pole degree of `a+b` or `a-b` is at most the sum of their pole degrees;
- the pole degree of `a*b` is at most the sum;
- inversion preserves total pole degree, because the zeros and poles of a nonzero rational function have equal total degree.

Suppose the DAG has already used `g` binary nodes. Starting from maximum initial pole degree `3`, every new binary node can at most double the current degree budget. Hence every output satisfies

`pole_degree(f) <= 3*2^g`.

This estimate permits arbitrary sharing. Reusing a node does not increase the gate count or invalidate the bound.

## secp256k1 gate floor

Combining the two bounds gives

`3*2^g >= (n-1)/2`,

so

`g >= ceil(log2((n-1)/6))`.

For the exact secp256k1 subgroup order, the least possible integer is

`g=254`.

More explicitly:

- `3*2^253` is strictly smaller than `(n-1)/2`;
- `3*2^254` is at least `(n-1)/2`.

Therefore no rational decoder in this model with at most 253 charged binary DAG gates can compute exact parity on the complete nonzero subgroup.

## Interpretation

This result corrects the scale of the search.

Testing four or eight tiny arithmetic nodes cannot tell us much about the surviving high-degree regime. A direct rational parity decoder, if it exists in the declared language, must begin at roughly 254 nonlinear arithmetic nodes.

At the same time, 254 field operations are not remotely an impossibility result. Repeated squaring can create exponential algebraic degree with only a linear number of gates. V8 therefore establishes a floor, not a cryptographic security bound.

## Charged high-degree leaves

The bound assumes that the initial nonconstant leaves are `x` and `y`.

A proposal may introduce a leaf such as `x([s]Q)`, a Miller value, a division polynomial, or another high-degree rational map. Such a leaf is not free. Its construction DAG, scalar-multiplication chain, coefficients, preprocessing and memory must be included in the cost ledger.

If the total charged initial pole budget is `B`, the same proof gives

`g >= ceil(log2((n-1)/(2B)))`.

Allowing an exponentially large precomputed leaf without charging it would merely hide the missing algorithm in the input representation.

## What V8 closes

- direct rational decoders from `x,y` with at most 253 binary arithmetic DAG nodes;
- claims that an exact rational parity decoder exists in an extremely tiny arithmetic circuit;
- uncharged reuse as a way to evade the pole-degree ledger.

## What remains open

- rational DAGs with 254 or more binary gates;
- a huge-degree rational function with an explicit short construction;
- branch, comparison, character, square-root, theta, p-adic or other nonrational operations;
- multistate algorithms and query-dependent jump-ahead mechanisms;
- CM, Miller or modular-composition circuits whose complete construction cost is polynomial;
- the existence of any classical polynomial-time parity algorithm.

## Next research target

The next synthesis stage must not enumerate arbitrary 254-gate programs. It must search structured families whose large degree is generated compactly:

1. repeated-composition and addition-chain templates;
2. sparse products and sums of public high-degree states;
3. modular-composition chains;
4. coupled CM/Miller states with exact branch transport;
5. true DAG templates in which shared intermediate nodes are explicit.

Every candidate must be tested as a direct random-access evaluator at `Q`, not as a recurrence that still requires walking through the hidden scalar index.
