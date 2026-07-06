# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)

## `sig:f9292aa1ec28` — axis: reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants) — outcome: **parked**
- **Hypothesis:** The discrete log problem on secp256k1 is equivalent to factoring integers of the form p^k - 1 for k dividing the order of the elliptic curve group, via an explicit reduction that uses the Weil pairing to embed the DLP into the multiplicative group of an extension field of degree equal to the embedding degree. Since the embedding degree is large, we consider constructing a tower of field extensions where at each step we factor p^{k_i} - 1 and find a smooth factor, ultimately solving the DLP by index calculus in the compositum field.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:ce818689bd0a` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The secp256k1 curve is (2,2)-isogenous to the Jacobian of a genus-2 curve C over its prime field, where the isogeny kernel is the full 2-torsion of the product with a specific twist. This embeds the ECDLP into the divisor class group of C, where index-calculus with a factor base of size O(p^{2/3}) and relations from degree-4 rational maps yields subexponential complexity.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:3186fe0a38f3` — axis: cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory) — outcome: **parked**
- **Hypothesis:** The secp256k1 point addition can be realized as a specific birational map on the x-coordinate that corresponds to a word in the braid group B_3. Under this correspondence, the discrete logarithm problem reduces to the word problem in B_3, and the word length is bounded by a polynomial in the number of group operations required for the scalar multiplication by n.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:595565868b17` — axis: geometric (higher genus, abelian varieties, moduli, covers) — outcome: **parked**
- **Hypothesis:** The secp256k1 elliptic curve E: y^2 = x^3 + 7 over F_p (p = 2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1) admits a genus-2 hyperelliptic curve C: y^2 = x^5 + ax^3 + bx^2 + cx + d over F_p such that there exists a (2,2)-isogeny between Jac(C) and E × E', where E' is another elliptic curve, and the embedding degree of Jac(C) for a prime factor ℓ of #E(F_p) is less than 20.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:40eca048e3b8` — axis: index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases) — outcome: **parked**
- **Hypothesis:** For secp256k1, with extension degree d=2, the factor base consists of points with x-coordinate in F_p. The Semaev polynomial S_2(x1,x2) for the sum of two points being equal to a given target point R has degree 5 in each variable. For a fixed factor base point Q (x_Q in F_p), the univariate polynomial S_2(x1, x_Q) in x1 may factor nontrivially over F_p or a small extension, yielding a relation that expresses R as a sum of Q and another point with x-coordinate in F_p. The hypothesis is that for some R and Q, such a factorization exists, giving a linear relation among factor base points.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:99ddf7c39e2e` — axis: analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions) — outcome: **parked**
- **Hypothesis:** The Frobenius endomorphism π on secp256k1 acts as multiplication by p on the formal group Ê(pℤp), giving an exact relation log_E(π(P̃)) = p·log_E(P̃). For a lifted point P̃ ∈ E(ℚp) with formal group coordinate t = -x(P̃)/y(P̃) mod p, the discrete logarithm k for P = [k]G satisfies log_E(t_G)^k = p^{k-1}·log_E(t_G) (where t_G corresponds to generator G), and the p-adic valuation of log_E(t_P) - k·log_E(t_G) determines the solution uniquely.
- **Sub-claim:** 
- **Evidence:** `(rigour tier produced no checkable sub-claim/script)`

## `sig:03d6b08caa7a` — axis: algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n]) — outcome: **refuted**
- **Hypothesis:** The endomorphism ring of secp256k1 (j=0 over F_p, p as given) is the maximal order in Q(√{-163}) because p splits in that field, the trace t of Frobenius satisfies t^2 - 4p = -163 n^2 for some integer n (with t the given 0x14551231950b75fc4402da1732fc9bebf), and the class polynomial H_{-163}(x) has a root mod p at j=0.
- **Sub-claim:** The class polynomial H_{-163}(x) = x + 640320 has a root at j=0 modulo p, and the group order n computed from the trace t of Frobenius satisfies n = sqrt((4p - t^2)/163) exactly as an integer, and the minimal polynomial x^2 - tx + p has discriminant -163n^2.
- **Evidence:** `Traceback (most recent call last):
  File "/tmp/tmpev2eov4l/cert.py", line 12, in <module>
    assert H_163.eval(0) == 0
           ^^^^^^^^^^^^^^^^^^
AssertionError`

