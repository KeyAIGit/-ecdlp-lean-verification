# TORUS-PRIME-TRACE-EXACTNESS-GATE-001

This is the first zero-solver test selected by `HYP-SELECT-004`.

It audits one prerequisite for the conditional
`HYP-PPLUS1-TRACE-RELATION-001` attack proposal: an odd-order subgroup of
the nonsplit norm-one torus must admit an exact reduced trace-set
representation and a logarithmic Dickson recurrence without importing a
discrete-log oracle.

Run:

```sh
python3 experiments/torus_prime_trace_exactness/validate.py
```

The validator uses only Python's standard library.  It independently
constructs each toy trace set from a subgroup of
`{u in F_(p^2)^*: Norm(u)=1}` and as the root set of `D_H(X)-2`.  It also
checks the odd-order factorization

```text
D_H(X)-2 = (X-2) * (U_s(X)+U_(s-1)(X))^2,  H=2s+1,
```

the squarefree trace degree `(H+1)/2`, inversion-fiber sizes, and a
fast recurrence using at most `3*bit_length(H)` nonlinear gates.  Seven
distinct toy primes are used, with `j=0` and non-`j=0` curve-lift
histograms recorded as controls.

## Scope

Passing this certificate establishes only a bounded toy algebraic identity
and exact secp256k1 parameter arithmetic for two known divisors of `p+1`.
It does **not** prove:

- a low Groebner/F4 solving degree;
- a relation-yield advantage;
- independent relation rank;
- a smaller linear-algebra or recovery cost;
- an asymptotic improvement;
- a secp256k1 ECDLP attack.

The remaining 184-bit cofactor is recorded by exact division but is not
given a formal primality certificate here.  The 23-bit and 46-bit factors
are checked by deterministic Miller--Rabin in the 64-bit range; this is a
computational replay, not a Lean theorem.

No Semaev solver, real key, wallet, or third-party target is used.
