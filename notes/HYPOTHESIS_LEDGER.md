# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)

## `sig:c205425ba075` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The secp256k1 elliptic curve over F_p admits an endomorphism τ of order 3, defined over an extension field F_{p^6}, that acts on the x-coordinate by multiplication by a primitive cube root of unity ω ∈ F_{p^3} and on the y-coordinate by multiplication by a square root of ω (i.e., τ(x,y) = (ωx, ω^{(p^2-1)/3}? y) with appropriate scaling). The endomorphism τ is rational and satisfies τ^3 = id, and its minimal polynomial over End(E)⊗Q has the form X^2 - t' X + d for some integers t' and d, yielding a nontrivial relation in the endomorphism ring that could reduce the effective security of the discrete log problem on secp256k1.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:5bba426a9f74` — axis: algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n]) — outcome: **parked**
- **Hypothesis:** On secp256k1, the endomorphism ring is the maximal order in Q(√-3), and the curve has CM by an order of conductor 2. This induces an extra endomorphism ψ with ψ^2 = -3, which acts on the isogeny graph and on torsion subgroups.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:908d9f35c65d` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** For secp256k1, restricting x1, x2 to the factor base of x-coordinates in F_{p^{1/2}} in the Semaev polynomial S_3 yields a polynomial equation over F_p whose splitting involves the curve's endomorphism ring. This yields a relation that factors via a degree-6 polynomial arising from the characteristic polynomial of Frobenius, allowing a subexponential index-calculus variant.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:1e371155bcdf` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** There exists a factor base consisting of irreducible polynomials of degree at most d (e.g., d=2) in the coordinate ring of secp256k1 such that the discrete log can be reduced to solving sparse linear systems over F_p via a decomposition method that uses resultants of Semaev polynomials with auxiliary polynomials derived from the curve's endomorphism ring (specifically, the Frobenius endomorphism and the multiplication-by-m map).
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:036bcc566807` — axis: analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions) — outcome: **parked**
- **Hypothesis:** The formal logarithm of the formal group of an elliptic curve over Q_p, when evaluated at points of E(K) for an unramified extension K/Q_p, maps into p^k Z_p for some fixed k>0, under the condition that the points are in the image of the cyclotomic character.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:3d3065cb4f37` — axis: reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants) — outcome: **parked**
- **Hypothesis:** The ECDLP on secp256k1 is equivalent to computing a rational divisor class on a genus-2 curve C embedded in the Kummer surface K of the Weil restriction of E to F_{p^2}, such that the equivalence factors through factoring a principal ideal in End(A) for a supersingular elliptic curve A in characteristic p.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:de27c1055480` — axis: cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory) — outcome: **parked**
- **Hypothesis:** The secp256k1 DLP reduces to computing the contraction of a one-dimensional tensor network (matrix product state) of length O(log p), where each tensor encodes the elliptic curve addition law, and the hardness is determined by the entanglement entropy across any cut, which scales like O(log p) (feasible) or O(p) (hard) depending on the tensor structure.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:b12f9b30c890` — axis: analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions) — outcome: **parked**
- **Hypothesis:** The local Selmer group of the E[p]-twist of the formal group of E at the prime p contains a local factor (k mod p) from the image of a rational point, where this factor satisfies a p-adic logarithmic relation between Q and P in the formal group, independent of computing the global discrete log.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:3170443798cd` — axis: analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions) — outcome: **parked**
- **Hypothesis:** The p-adic elliptic logarithm of a point on secp256k1, reduced modulo p^2, satisfies a quadratic relation with coefficients in F_p that depends only on the x-coordinate of the point. This relation, derived from the formal group logarithm series truncated at O(p^2), may hold only for points in the kernel of reduction (or for all points under a suitable lift), thereby constraining the discrete log search to a subset of points whose x-coordinates satisfy the quadratic equation.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:0f953e7327dd` — axis: algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n]) — outcome: **parked**
- **Hypothesis:** The endomorphism ring of secp256k1 is isomorphic to the maximal order of Q(√-3), with CM map φ satisfying φ^2 + φ + 1 = 0. For ℓ ≡ 1 mod 3 splitting in Q(√-3), a twisted pairing via the CM action distorts the DLP in E(ℓ)[F_p] and allows transfer to F_{p^2}.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:e8c1667278b3` — axis: reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants) — outcome: **parked**
- **Hypothesis:** The discrete log problem on secp256k1 reduces to factoring a univariate polynomial f(x) over F_p whose irreducible factors are the x-coordinates of points in E(F_p) up to the group law, specifically f(x) = ∏_{P∈E(F_p)} (x - x(P)) has degree n = #E(F_p) but factors as product of polynomials corresponding to cyclic subgroups.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:f20a275f4105` — axis: reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants) — outcome: **parked**
- **Hypothesis:** The discrete log problem on secp256k1 reduces in deterministic polynomial time to factoring a quartic integer in the ring of integers of Q(√-7) derived from the 7-division polynomial and the endomorphism corresponding to √-7.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:f3f0eddace24` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The 2-descent map from secp256k1 to the Jacobian of the genus-2 curve C: y^2 = x^5 + 7, defined via a degree-4 cover branched at the 2-torsion points of E, embeds E into Jac(C) such that the addition law on E corresponds to a linear condition in the Mumford representation on Jac(C).
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:0a59cfdcd21c` — axis: cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory) — outcome: **parked**
- **Hypothesis:** The endomorphism ring of secp256k1, isomorphic to Z[√-7], can be represented as a Matrix Product Operator (MPO) acting on a tensor network that encodes the Frobenius endomorphism. The spectral gap of the transfer matrix derived from this tensor network determines the discrete log complexity by limiting the mixing of the corresponding dynamical system.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:557f93354784` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** For secp256k1, the Semaev polynomial S_3(x1,x2,x3) over F_{p^2} factorizes as a product of two polynomials each of total degree 2, due to the action of the automorphism φ(x,y)=(ωx,y) where ω is a primitive cube root of unity in F_p. This factorization reveals a decomposition basis of size 2 in F_{p^2}, reducing the decomposition step complexity.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:9373cccf9c3f` — axis: cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory) — outcome: **parked**
- **Hypothesis:** The discrete log problem on secp256k1 reduces to finding the closest lattice point in a rank-2 lattice L = {(x,y) ∈ Z^2 : x + yπ ∈ lEnd(E)} under a metric derived from the Weil pairing, where π is the Frobenius endomorphism satisfying π^2 - tπ + p = 0. The reduction is based on representing the Frobenius action on a generator G as π(G) = [a]G + [b]G with a,b ∈ F_l satisfying a^2 + b^2 ≡ c (mod l) for some constant c, leading to a CVP instance with potential for a subexponential attack if the covering radius of L is unexpectedly small.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

