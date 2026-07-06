# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)

## `sig:a0ebbc540847` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** The specialization of Semaev polynomial S_3(x1,x2,x3) to factor-base x-coordinates x1, x2 ∈ 𝔽_p yields a polynomial in x3 whose resultant in (x1,x2) factors nontrivially, revealing an algebraic dependency that increases the probability of finding a decomposition relation beyond the 1/p naive heuristic.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:d6a8d040ef94` — axis: algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n]) — outcome: **parked**
- **Hypothesis:** The endomorphism ring of secp256k1 is larger than Z[π] because there exists a rational 3-isogeny to a curve with CM by Q(√-3) when p ≡ 1 mod 3, implying the endomorphism ring contains an element of norm 3, making it an order in Q(√-3) or a larger field.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:648e65701745` — axis: analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions) — outcome: **parked**
- **Hypothesis:** The formal group logarithm of secp256k1 at p, evaluated at a point of order related to the trace of Frobenius t, has a zero modulo p^2, linking the canonical height regulator to the p-adic L-function value at s=1.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:d5e25bb5d90c` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** On secp256k1, there exists a factor base consisting of points whose order divides 2^k (k fixed, e.g., k=3) and whose x-coordinates satisfy S_m(x_1,...,x_m)=0, where S_m is the m-th Semaev polynomial. The number of such factor-base points is subexponential in log(p) because the system S_m=0, when restricted to these x-coordinates, has a solution count O(p^{c/m}) for some c<1, i.e., faster than the generic bound for arbitrary points.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:1da72118f0ee` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The group law on secp256k1 can be realized as a translation on a genus-2 curve C that is the fiber product of two elliptic curves E and E', where E' is a quadratic twist of E, both isogenous to secp256k1. The discrete logarithm problem on secp256k1 then reduces to finding a translation on the Jacobian Jac(C) that preserves a reducible polarization, effectively converting ECDLP to a problem on the product of two elliptic curves.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:71bcfb984976` — axis: algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n]) — outcome: **parked**
- **Hypothesis:** The endomorphism ring of secp256k1 contains an endomorphism ψ satisfying ψ^2 + 3 = 0 in the ring, acting on E[n] as multiplication by some t mod n with t^2 ≡ -3 mod n. This imposes that the discrete logarithm k (satisfying Q = kP) must also satisfy a linear congruence modulo n in the ring Z[√-3]/(n), because ψ(Q) = ψ(kP) = k ψ(P) implies that the ratio ψ(P)/ψ(Q) in the CM order yields (ψ(P)/ψ(Q))^2 ≡ -3 mod n, constraining k modulo n when n divides the discriminant.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:b895e4221351` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The genus-4 curve C = E / ⟨ (x,y) → (ζx, ζ²y) ⟩ over F_p(ζ) (ζ^3=1, ζ≠1) where p≡1 mod 3, has its Jacobian isogenous to E × A for some abelian surface A, and the discrete logarithm in E[F_p] can be transferred to a discrete log in the Jacobian of C via the Weil restriction of the 3-torsion subgroup. If #C(F_p) has a prime factor q distinct from the curve's embedding degree, the DLP in C's Jacobian might be vulnerable to index calculus on higher genus curves.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

