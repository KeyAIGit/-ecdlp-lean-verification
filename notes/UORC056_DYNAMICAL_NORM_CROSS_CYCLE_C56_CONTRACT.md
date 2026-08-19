# UORC-056 C56 contract: dynamical norm or cross-cycle transport

Date: 2026-08-19

Status: successor research contract. No parity evaluator is claimed.

C55 proves that the exact 64-state secp256k1 doubling-cycle label and the cycle-orientation norm are both insufficient to decode point parity. The unresolved object is an oriented within-cycle phase or a relation crossing the 32 pair cycles.

C56 must construct or exclude within an explicit grammar one of:

```text
a sublinear evaluator of a full doubling-orbit norm,
a compressed open transport crossing multiplier cycles,
a public within-cycle phase not requiring the exponent j.
```

Mandatory gates:

1. no scalar-labelled path or exponent advice;
2. no table with one value per cycle vertex;
3. exact behavior under doubling, halving, GLV, and negation;
4. held-out validation;
5. all preprocessing, advice, memory, representation, and online costs charged;
6. independent replay and Lean checks;
7. one explicit positive epsilon for any claimed sub-square-root cost.

Reject any candidate that computes only `k^M`, only the cycle norm, solves the order-M DLP generically, or materializes an orbit factor of degree `Theta(M)`.
