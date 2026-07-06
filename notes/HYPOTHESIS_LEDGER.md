# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)

## `sig:9d28ebf41c21` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** The endomorphism ψ = π + π^{-1} on the x-coordinate of secp256k1 yields a decomposition base where for any point P with x-coordinate in F_p, the points P, π(P), ψ(P) satisfy a low-degree polynomial relation over F_p that factors into linear terms in x, effectively reducing the degree of the Semaev decomposition system from O(n^(1/2)) to O(log p) for the factor base elements.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:5893031628f6` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The rational map from E × E → P^1 given by the y-coordinate of point addition (when x(P) ≠ x(Q)) induces a degree-2 cover of P^1 by a genus-1 curve. For secp256k1 (j=0), the branch locus consists exactly of the images of the 2-torsion points under the x-projection (x([2]Q) = 0) and possibly ∞, and the j-invariant of the cover curve is 0, matching secp256k1's isomorphic class.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:ca0c7e37f531` — axis: cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory) — outcome: **parked**
- **Hypothesis:** The discrete log on secp256k1 reduces to finding a path in a dynamical system on the Jacobian of a genus-2 curve derived from a Kummer surface via a Howe pair (C1,C2), where the Frobenius endomorphism acts as a shift on a tensor network of binary trees encoding the 2-adic scalar expansion. The network contraction yields a polynomial system over F_p whose sparse resultant in the group of rational points of a K3 surface vanishes if and only if the discrete log holds.
- **Sub-claim:** For p=163, given a Kummer surface K derived from a genus-2 curve with a Howe pair (C1, C2) and a random point P on K, the resultant of the polynomials f1(t) and fk(t) derived from iterated Frobenius and scalar multiplication respectively, is zero if and only if the scalar k matches the discrete logarithm of Qk with respect to P.
- **Evidence:** `utation)
Traceback (most recent call last):
  File "/tmp/tmpfzuskej8/cert.py", line 22, in <module>
    raise ValueError('Resultant is not zero')
ValueError: Resultant is not zero`

