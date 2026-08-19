# UORC-056 H-RPCX true multiregister DAG CEGIS V10

## Purpose

V10 replaces the corrected V5 formula-tree model and the V9 unary macro-chain model with a genuine shared-register DAG representation.

A computed register is stored once. Any later gate may consume it repeatedly, and its ancestry is charged only once in the final output DAG.

For example, if

`u=x*y`

and

`v=u+u`,

then the DAG cost is two gates. Expanding the expression as

`(x*y)+(x*y)`

would incorrectly charge three gates. V10 contains a mandatory self-test for this distinction.

## Search state

The public base register library contains:

- coordinates of `[s]Q` for `s=1,2,3,4,5,7,8`;
- `x(Q) +/- x(G)` and `y(Q) +/- y(G)`;
- `x(Q) +/- y(Q)`;
- `x(Q)^3` and `beta*x(Q)`;
- public constants `0,1,-1,7,x(G),y(G),beta`.

Twelve selected seeds receive explicit repeated-squaring ladders through depth 254. Every squaring is an actual one-gate node and every intermediate power remains available as a register for later reuse.

The binary gate set is

`+,-,*,/`,

where division is admitted only when its denominator is nonzero on the complete declared corpus.

Public readout macros `chi2`, `chi3`, `chi6`, inversion and negation are charged by expanded arithmetic cost. Their internal exponentiation registers are not exposed to other gates in V10; this is a declared remaining limitation rather than hidden sharing.

## True DAG accounting

Every generated node stores:

- parent register identifiers;
- one unique gate identifier;
- the union of all ancestor gate identifiers;
- the sum of charged weights over that union.

When two parents share an ancestor, set union counts the ancestor once. Thus the reported cost is the size of the constructed DAG, not the size of a recursively expanded formula.

A formula-tree cost is also computed for the final witness, allowing the output certificate to report the exact savings caused by sharing.

## Counterexample-guided search

Four frozen curves are used for synthesis. The fifth frozen curve and the independent curve

`(p,n,G)=(61,61,(2,25))`

are held out from candidate selection.

The active constraint set begins with two scalar positions from each training curve. After each deterministic synthesis pass, the current best candidate is checked against the complete training corpus. Exact failing positions are added round-robin across training curves, and the search is rerun.

This is counterexample-guided refinement. It does not make the retained-library search exhaustive.

## Search pruning

Every binary gate in one expansion may use any two nodes in the retained pool. However, the pool is selected deterministically by active errors, complete training errors and expanded DAG cost. The search therefore remains heuristic.

Semantic deduplication keeps a cheapest standalone representation and may discard another representation whose different ancestry could share more effectively with a future node. V10 records this limitation explicitly.

## Admission rule

A candidate is called an algorithm only if one unchanged DAG is exact on:

1. every point of all four training curves;
2. every point of the frozen holdout curve;
3. every point of the independent `(61,61)` holdout curve.

Even then it is only a transferable toy candidate. A secp256k1 claim additionally requires a symbolic identity, independent replay, complete cost expansion and proof of all exceptional branches.

## Claim boundary

V10 is infrastructure plus a deterministic discovery screen.

It does not prove a circuit lower bound, and failure to find a candidate does not imply that no multiregister parity DAG exists.

Its scientific value is narrower and concrete: future searches can now use shared intermediate values without accidentally charging formula-tree cost or calling a unary macro chain a multiregister circuit.
