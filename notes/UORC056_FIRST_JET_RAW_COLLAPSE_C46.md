# UORC-056 C46: geometric first jet collapses to the raw state

Date: 2026-08-17

Status: exact structural collapse. The ordinary geometric first derivative of the order-`n` division condition is not a second independent public state. No ordered-sector evaluator, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. What is a first jet?

A **first jet** means the first derivative of a function at a point. Here the function is the order-`n` division polynomial `psi_n`, which vanishes at every nonzero point of the order-`n` subgroup.

For

\[
Q=(x(Q),y(Q)),
\]

define

\[
J_n(Q)=2y(Q)\frac{d}{dx}\psi_n(Q).
\]

The factor `2y(Q)` removes the denominator introduced when differentiation follows the curve relation

\[
y^2=x^3+7.
\]

This is the most natural local derivative of the equation `psi_n(Q)=0`. It looked like a plausible second measurement independent of the C45 state `Phi_raw(Q)`.

## 2. Exact value at the public generator

Let `A,B` be the Ward constants from C45. Exact dual-number evaluation gives

\[
\boxed{J_n(G)=-nB.}
\]

A dual number has the form `a+b epsilon` with `epsilon^2=0`. It carries a function value in `a` and its first derivative in `b`, allowing the complete division-polynomial recurrence and its derivative to be evaluated together.

## 3. Main collapse

The first-jet composition formula gives

\[
J_n([k]G)
=(-1)^{k-1}n^{1-k^2}J_n(G)^{k^2}
\psi_k(G)^{-n^2}.
\]

Substituting

\[
J_n(G)=-nB
\]

and the C45 identity

\[
\Phi_{\rm raw}([k]G)=\psi_k(G)c^{k^2},
\qquad c^{n^2}=B^{-1},
\]

all constants and signs simplify to

\[
\boxed{
J_n(Q)=-n\Phi_{\rm raw}(Q)^{-n^2}.
}
\]

### Plain meaning

The derivative does not provide a second sensor. Once `Phi_raw(Q)` is known, `J_n(Q)` is already completely determined by one exponentiation and multiplication by the public constant `-n`.

Taking the square/nonsquare sign also adds nothing new:

\[
\chi(J_n(Q))=\chi(-n)\chi(\Phi_{\rm raw}(Q)).
\]

Thus its binary information is the same raw-state sign, up to one public fixed phase.

## 4. Exact replay

```text
8 public toy curves
1 fixed secp256k1 instance with known scalar indices
294 sampled nonzero scalars
9 generator-jet identities
294 raw-state collapse identities
294 first-jet composition identities
294 character identities
0 arithmetic errors
```

The three smallest groups are checked on their complete nonzero orbits. The larger groups and fixed secp256k1 are checked on deterministic public scalar samples.

## 5. What this closes

C46 closes the **ordinary geometric first jet** as an independent open section.

It does not close:

- the p-adic arithmetic jet (a different object obtained after lifting modulo `p^2`);
- second and higher derivatives;
- nonlinear functions of `Phi_raw`;
- the joint GLV triple `Phi_raw(Q), Phi_raw(alpha Q), Phi_raw(alpha^2 Q)`;
- theta functions, elliptic units, or unrestricted arithmetic circuits.

## 6. Successor

The next package is

```text
GLV-RAW-TRIPLE-OR-INDEPENDENT-SECTION-C47
```

It tests whether the three complete raw values on the public GLV orbit contain a cheaply decodable joint state that is absent from each value separately. If that triple also collapses to the already-known carry/EDS observables, the search must leave the Ward/geometric-jet family and construct a genuinely independently transforming theta, elliptic-unit, or p-adic section.
