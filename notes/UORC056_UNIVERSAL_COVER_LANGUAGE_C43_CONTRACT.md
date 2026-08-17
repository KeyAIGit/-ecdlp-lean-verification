# UORC-056 C43 execution contract

## Inputs

Only the following inputs are allowed:

- public secp256k1 constants `p` and `n`;
- the five inherited frozen prime orders `31, 79, 67, 127, 139`;
- held-out order `61`;
- additional synthetic odd prime diagnostic orders;
- deterministic gauge functions and exact integer arithmetic.

No external elliptic-curve point, wallet, key, signature, nonce, unknown scalar or production target may be accepted.

## Required outputs

The replay must certify:

1. seven hypothesis records;
2. the universal-cover carry identity and section-gauge law;
3. trivial `mu_2` character and central-extension classes for odd cyclic groups;
4. the symbolic-doubling digit identity;
5. `ord_n(2)=(n-1)/64` for the secp subgroup order;
6. `ord_p(2)=(p-1)/14` for the secp base field;
7. exactly 32 doubling cycles on the secp pair quotient;
8. the `cot(pi/(2n))` nonzero-parity Fourier peak;
9. the secp trace-bound exponent greater than `127.34`;
10. gauge-neutrality of squares and closed loops;
11. endpoint charge of open transport;
12. zero arithmetic errors.

## Decision gates

The machine-readable result must state:

```text
cheap_parity_decoder_found = false
parity_oracle_found = false
sub_sqrt_ecdlp_found = false
old_transitivity_claim_correct = false
only_surviving_local_type = unsquared anchor-to-query open transport
```

## Claim limits

- The cohomology result is for central `mu_2` extensions with trivial action.
- The p-adic closure applies to ordinary additive/formal logarithmic homomorphisms, not all p-adic polylogarithms or regulators.
- The tropical closure applies to explicit continuous piecewise-linear threshold representations charged by segment count.
- The trace-function closure is conditional on the candidate class supplying the declared uniform `B*sqrt(p)` twist bound.
- The gauge type system is a static impossibility filter, not an evaluator for charged objects.
