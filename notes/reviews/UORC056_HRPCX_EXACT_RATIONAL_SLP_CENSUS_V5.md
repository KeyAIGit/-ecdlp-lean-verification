# UORC-056 H-RPCX bounded rational formula-tree census V5 — audit correction

## Corrected status

The previous claim of an exhaustive eight-gate straight-line-program census is withdrawn.

Two independent problems were found during audit:

1. the GitHub Actions run did not complete the requested eight-gate search; it stopped after constructing the cost-5 level because the semantic cap was exceeded;
2. the enumerator measures expression-tree size, not straight-line-program or DAG circuit size, because repeated subexpressions are charged again rather than shared.

Therefore the old statement

> no parity circuit with at most eight gates exists in the declared grammar

was not established.

## What the failed run actually showed

The aborted run reported semantic counts

`[8, 82, 959, 13073, 193404, 2991347]`

for costs zero through five and then raised a `semantic cap exceeded` exception. No result artifact was produced and levels six through eight were never searched.

Because the run aborted, the repository must not use it as an eight-gate certificate.

## Corrected certified class

The CI workflow now performs a complete census only through **four expression-tree gates**.

Public leaves are:

- `0`, `1`, `-1`, and `7`;
- `x(G)` and `y(G)`;
- `x(Q)` and `y(Q)`.

Allowed internal nodes are:

- addition;
- subtraction;
- multiplication;
- inversion when the denominator is nonzero on the complete joint toy corpus.

The same formula tree is evaluated without coefficient retraining on five deterministic small prime-subgroup instances of `y^2=x^3+7`.

Semantic merging is sound for this finite corpus: expressions with identical joint value vectors are interchangeable under all declared pointwise operations. Dynamic programming by increasing tree size therefore gives an exhaustive result for the stated formula-tree class and size bound.

## Corrected result

No formula tree with at most four internal arithmetic nodes in this declared grammar equals exact canonical parity on the full five-curve toy corpus.

This is a very small bounded negative result. It does not materially constrain a realistic parity algorithm.

## What is not proved

- no formula of size five through eight;
- no straight-line program with shared subexpressions;
- no DAG arithmetic circuit;
- no formula using coordinates of `[s]Q`;
- no GLV, CM, Miller, theta, division-polynomial, pairing, or p-adic state;
- no circuit specialized to secp256k1;
- no general arithmetic-circuit lower bound.

## Terminology rule

Until a search engine explicitly supports shared intermediate values and charges each computed gate once, its result must be called a **formula-tree census**, not an SLP or circuit census.
