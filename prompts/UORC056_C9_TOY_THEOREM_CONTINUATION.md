# UORC056 C9 theorem-first continuation

## Scope

Work only on the six frozen toy curves and the committed C9 result data. Do not accept external points, unknown scalars, wallet material, production keys, or real-world cryptographic targets. Do not attempt to construct or deploy an oracle for secp256k1 or any production curve.

## Established C9 statements

Formalize and independently check the following mathematical claims:

1. For an odd prime-order cyclic subgroup `H=<G>`, the sign function `sigma_G([k]G)=(-1)^k` is anti-invariant under point negation and therefore does not descend to the Kummer quotient.
2. With `m=(n-1)/2`, there is a unique polynomial `r_G` of degree below `m` satisfying `r_G(x([i]G))=(-1)^i/y([i]G)` for `1<=i<=m`.
3. On every nonzero point of the frozen subgroup, `sigma_G(Q)=y(Q)r_G(x(Q))`.
4. For the Kummer kernel polynomial `h_H`, the congruence `F*r_G^2=1 mod h_H` holds.
5. The unsigned even-index and odd-index x-products both equal `h_H`.
6. Any rational function agreeing with `sigma_G` on all nonzero subgroup points has pole-divisor degree at least `(n-1)/2`.
7. No nonzero globally periodic scalar function on an odd cycle satisfies `tau_G f=-f`.

## Required work

Produce theorem-first proofs and narrow Lean lemmas for the claims above. Recheck the committed JSON counts and transformations on the frozen cases only. Distinguish exact proofs from finite verification. Audit exceptional denominators and the assumptions `char != 2`, odd prime subgroup order, and nonsingularity.

A continuation may prove scoped impossibility results for bounded-degree rational formulas, inversion-invariant kernel constructions, or ordinary unsigned product identities. It must not broaden into real-world key recovery, production-curve exploitation, or instructions for overcoming deployed cryptographic security.

## Output

Use the sections:

```text
PROVED
FORMALIZED
REPLAY-DATA-CHECKED
ASSUMPTIONS
SCOPED NO-GO
OPEN MATHEMATICS
```

Keep all algorithmic-success flags false. The purpose is rigorous theorem verification and boundary mapping on frozen toy data.
