# UORC-056 H-RPCX true multiregister DAG CEGIS V10/V10A

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

where division is admitted only when its denominator is nonzero on the complete declared training corpus.

Public readout macros `chi2`, `chi3`, `chi6`, inversion and negation are charged by expanded arithmetic cost. Their internal exponentiation registers are not exposed to other gates in V10; this is a declared remaining limitation rather than hidden sharing.

## True DAG accounting

Every generated node stores:

- parent register identifiers;
- one unique gate identifier;
- the union of all ancestor gate identifiers;
- the sum of charged weights over that union.

When two parents share an ancestor, set union counts the ancestor once. Thus the reported cost is the size of the constructed DAG, not the size of a recursively expanded formula.

V10A independently audits the selection rule and computes formula-tree expansion with memoized node costs. Duplicate parent occurrences remain duplicated in the formula-tree comparison, but a 254-step square ladder is audited in linear rather than exponential runtime.

## Counterexample-guided search

Four frozen curves are used for synthesis. The fifth frozen curve and the independent curve

`(p,n,G)=(61,61,(2,25))`

are held out from candidate selection.

The active constraint set begins with two scalar positions from each training curve. After each deterministic synthesis pass, the CEGIS-guiding candidate is checked against the complete training corpus. Exact failing positions are added round-robin across training curves, and the search is rerun.

V10A separates two roles that V10 originally conflated:

- the CEGIS candidate is used only to generate new counterexamples;
- the reported best training candidate is selected independently over every discovered node by complete training error and charged DAG cost.

Neither holdout contributes to selection.

## Audited replay result

The completed V10A replay used:

- 300 training points on four curves;
- 138 points on one frozen holdout curve;
- 60 points on the independent `(61,61)` holdout curve;
- four counterexample-refinement rounds;
- two binary synthesis layers per round;
- 254 exposed squaring registers on each declared ladder;
- a retained pool of 128 nodes and 384 retained binary results per layer.

No exact parity candidate was found.

The best node selected solely by training error had:

- `115 / 300` training errors;
- charged expanded cost `32`;
- `63 / 138` errors on the frozen holdout;
- a zero denominator on the independent holdout, so it was not even regular on the full transferred corpus.

Its five computed outputs were three quadratic-character readouts separated by one subtraction and one division. It had no shared-subgraph savings and therefore is not evidence for the central high-degree DAG hypothesis.

The best discovered node that actually used nontrivial DAG sharing had:

- charged DAG cost `30`;
- expanded formula-tree cost `2066`;
- `126 / 300` training errors;
- `81 / 138` frozen-holdout errors;
- `29 / 60` independent-holdout errors.

Thus the engine genuinely constructed and evaluated shared high-degree DAGs, but the sharing did not reveal parity.

In the best synthesis round, 3,839 retained nodes had positive savings relative to their expanded formula trees. The maximum formal saving was enormous because repeated squaring creates exponentially large expression trees. This validates the accounting implementation; it is not evidence of predictive value.

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

V10/V10A provides working infrastructure plus a deterministic discovery screen.

It does not prove a circuit lower bound, and failure to find a candidate does not imply that no multiregister parity DAG exists.

Its scientific value is concrete but limited:

- shared intermediate values are now represented and charged correctly;
- 254-step high-degree ladders expose all intermediate registers;
- CEGIS guidance is separated from unbiased training selection;
- holdout curves remain untouched until evaluation;
- no exact or near-transferable parity evaluator emerged from the declared search.

## Next target

The next expansion should add genuinely new public state families rather than merely widen the same coordinate grammar:

- compact Miller values and their exact defects;
- ordered GLV-sector states;
- CM-coupled multiregister templates;
- modular-composition jump nodes with fully expanded cost;
- ancestry-aware Pareto retention so semantically identical nodes with different sharing structure are not prematurely merged.
