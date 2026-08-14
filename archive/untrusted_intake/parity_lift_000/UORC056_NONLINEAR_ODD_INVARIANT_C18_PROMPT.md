# GPT Pro focused continuation

## NONLINEAR-ODD-INVARIANT-RATIONAL-CIRCUIT-068

Work only on the UORC056 endpoint-gauge branch. Reproduce C9-C17 before extending them. Use only frozen toy curves, the publicly generated C17 extension corpus, known toy scalars, public generator replacements, and public secp256k1 constants. Do not accept an external point with an unknown scalar, wallet, or production key.

## Central target

For the three GLV conjugates of the endpoint gauge, define

```text
E1=Trace(Z),
E2=sum_(i<j) Z_i Z_j,
E3=Norm(Z).
```

C17 proves that `E1` and `E3` are odd under `Z -> -Z`, that

```text
E1=3*C0,
E2=3*(C0^2-t*C1*C2),
E3=C0^3+t*C1^3+t^2*C2^3-3*t*C0*C1*C2,
t=y^2-7,
```

and that every nonzero constant linear combination `alpha*E1+beta*E3` has support at least `(n-1)/6-4` and pole degree at least `(n-1)/12-2` on secp256k1.

Find an exact nonlinear odd rational invariant that evaluates the canonical branch with complete cost

```text
O(n^(1/2-epsilon))
```

or prove a square-root boundary for one declared nonlinear invariant grammar.

## Mandatory attack order

### A. Rational combinations of E1,E2,E3

Enumerate reduced expressions of bounded formula size and bounded rational degree in the generators, with parity condition odd under `(E1,E3)->(-E1,-E3)`. Remove public factors and test exact divisor cancellation. A toy cancellation is not promoted until it transfers symbolically and across the extension corpus.

### B. Residue-component recurrences

Search for public recurrences for `C0,C1,C2` using high-index division polynomials, elliptic nets, GLV maps, or addition chains. Charge every component state. Rewriting one dense function into three dense functions is rejected.

### C. Transposed y-line evaluation

Try modular composition, rational interpolation duality, residue pairings, or displacement structure that returns one component value at `y(Q)` without constructing its coefficients or roots. State preprocessing, memory, representation, and online costs separately.

### D. Bounded-width invariant circuits

Define a circuit or ABP grammar inside `F_p(y)` with explicit leaves and permitted n-dependent public indices. Search for a short exact odd invariant. If no construction survives, prove a support, state, query, or rank lower bound for that grammar.

### E. Adversarial branch audit

Every candidate must be checked under `G -> -G`, `G -> [u]G`, `Q -> -Q`, and gauge replacement. Reject any expression whose odd sign is inserted through an input trivialization or branch seed.

## Completion gate

A positive result must handle every subgroup point and divisor collision, include regularized local extraction, pass the complete sub-square-root cost ledger, and reproduce on frozen and extension corpora. Do not claim a parity oracle unless every gate passes.
