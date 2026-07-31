# Results

Status: `REPRODUCED TOY EXACTNESS / ATTACK CLAIM UNRESOLVED`

The standard-library replay passed on 2026-07-30:

```text
CERT_OK TORUS-PRIME-TRACE-EXACTNESS-GATE-001 cases=7 solver_runs=0
```

For odd toy subgroup orders `H = 11, 17, 13, 41, 53, 71, 83`:

- subgroup traces and roots of `D_H(X)-2` agreed exactly;
- the raw Dickson polynomial had degree `H` and repeated non-fixed roots;
- the explicit squarefree root product had degree `(H+1)/2`;
- the trace map had one singleton fiber (`u=1`) and two-element fibers
  elsewhere;
- the fast Dickson recurrence agreed with the literal recurrence for every
  field element;
- the largest recorded nonlinear-gate count was 21.

The `j=0` lift counts did not uniformly dominate the non-`j=0` controls.
That is useful negative evidence against treating trace-set exactness as
relation-yield evidence.

For secp256k1, exact integer replay checked

```text
p+1 is divisible by 16 * 7,322,137 * 45,422,601,869,677
trace degree for H=7,322,137:          3,661,069
trace degree for H=45,422,601,869,677: 22,711,300,934,839
```

The large factor's trace degree satisfies the unfiltered arity-six
heuristic `D^6 > 6! * p`, but fails after charging six independent
one-half lift probabilities.  This narrow arithmetic coincidence is a
reason to measure exact lift and relation yield; it is not evidence of a
sub-Pollard attack.

## Decision impact

The bounded root-mismatch form of `H_ARTIFACT` was not observed on the toy
suite.  The central barrier is unchanged: an `O(log H)` circuit can be only
a compressed description of a squarefree polynomial of degree about
`H/2`.  No solver run is authorized by this result.
