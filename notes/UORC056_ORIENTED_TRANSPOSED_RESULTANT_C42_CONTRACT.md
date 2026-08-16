# UORC-056 C42 contract: oriented transposed resultant

Date: 2026-08-16

Status: fulfilled by the canonical C42 package in
`notes/UORC056_ORIENTED_TRANSPOSED_RESULTANT_C42.md`.

## Contract outcome

The completed package derives and verifies:

1. exact target-root localization of the C39 orbit factors;
2. the exact GLV cubic relative norm
   `c0^3 + T*c1^3 + T^2*c2^3 - 3*T*c0*c1*c2`;
3. the reduction of the outer determinant dimension from `(n-1)/2` to
   `(n-1)/6`;
4. the fact that query-root localization returns the original missing branch
   `Y_G(x(Q))/y(Q)` rather than bypassing it;
5. a complete affine quadratic-character screen of the anti-Frobenius
   `2 by 2` minor on five frozen curves and one held-out curve;
6. an exact secp256k1 representation and two-level product cost ledger.

The declared explicit and two-level mechanisms do not meet the fixed-epsilon
sub-square-root gate. No unrestricted resultant or arithmetic-circuit lower
bound is claimed.

## Canonical files

```text
notes/UORC056_ORIENTED_TRANSPOSED_RESULTANT_C42.md
experiments/parity_lift_000/uorc056_c42_glv_transposed_resultant.py
experiments/parity_lift_000/uorc056_c42_antifrobenius_minor.py
experiments/parity_lift_000/uorc056_oriented_transposed_resultant_c42.py
experiments/parity_lift_000/test_uorc056_oriented_transposed_resultant_c42.py
Ecdlp/Proved/Uorc056OrientedTransposedResultant.lean
.github/workflows/uorc056-oriented-transposed-resultant-c42.yml
```

## Decision

```text
exact query-root localization                  found
exact GLV cubic relative norm                  found
asymptotic exponent improvement                no
anti-Frobenius affine-character decoder        no
cheap parity decoder                           not found
parity oracle                                  not found
sub-square-root ECDLP                          not found
```

The successor is `LOCAL-GLV-GAUGE-BREAKING-C43`.