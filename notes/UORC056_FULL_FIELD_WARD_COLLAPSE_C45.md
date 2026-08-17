# UORC-056 C45: full-field Ward collapse

Date: 2026-08-17

Status: exact structural collapse of the complete declared Ward near-period field family to one already-known public state. No ordered-sector evaluator, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. What was tested

C44 closed the route that immediately converts Ward values to `+1/-1` signs. C45 keeps the **complete field value** instead. A field value is an ordinary nonzero number modulo the curve prime, so it contains much more information than one sign.

Let

\[
Q=[k]G,
\qquad W_j=\psi_j(G),
\]

where `psi_j` is the `j`-th division polynomial. For every public offset `a`, define

\[
R_a(Q)=\frac{\psi_{n+a}(Q)}{\psi_a(Q)}.
\]

The hope was that several offsets might provide several independent measurements of the hidden orientation.

## 2. The public raw state

Define

\[
\Phi_{\rm raw}(Q)=
\left(
\frac{\psi_{p-1}(Q)}{\psi_{p-1+n}(Q)}
\right)^{(n^2)^{-1}\bmod(p-1)}.
\]

This is publicly computable by logarithmic-depth division-polynomial recursions. It is one number in the base field, not a table indexed by the unknown scalar.

Let `A,B` be the exact Ward quasi-period constants and set

\[
c=B^{-(n^2)^{-1}\bmod(p-1)}.
\]

The replay verifies

\[
A c^{2n}=1,
\qquad B c^{n^2}=1,
\]

and

\[
\Phi_{\rm raw}([k]G)=W_k c^{k^2}.
\]

## 3. Main identity

Division-polynomial composition gives

\[
\psi_m([k]G)=\frac{W_{mk}}{W_k^{m^2}}.
\]

Ward quasi-periodicity then gives

\[
R_a([k]G)=(A^aB)^{k^2}W_k^{-n(n+2a)}.
\]

Using the two constant relations above, the expression collapses exactly to

\[
\boxed{R_a(Q)=\Phi_{\rm raw}(Q)^{-n(n+2a)}.}
\]

This holds for every regular public offset `a`, not only for the offsets used in the finite replay.

### Plain meaning

Changing `a` does not create a new sensor. Every `R_a` is only a different public power of the same number `Phi_raw(Q)`.

The whole family is a geometric progression:

\[
\frac{R_{a+1}(Q)}{R_a(Q)}=\Phi_{\rm raw}(Q)^{-2n}.
\]

After one member and this one transition are known, every other member is determined.

## 4. What remains after canonical square-root extraction

For secp256k1, `p = 3 mod 4`. Put

\[
T(Q)=\frac{R_2(Q)}{R_1(Q)}=\Phi_{\rm raw}(Q)^{-2n}.
\]

`T` is a square. The field has a deterministic square root lying in the square subgroup:

\[
S(Q)=T(Q)^{(p+1)/4}.
\]

The only residual sign is

\[
\varepsilon(Q)=\frac{R_1(Q)}{S(Q)^{n+2}}
=\chi\bigl(\Phi_{\rm raw}(Q)\bigr).
\]

On secp256k1 this equals

\[
\chi\bigl(\Phi_{\rm raw}([k]G)\bigr)=(-1)^k\rho_G(k),
\]

where `rho_G(k)=chi(psi_k(G))` is the already-known EDS sign.

Thus preserving the complete field value does not reveal a second independent binary channel. After deterministic extraction, it returns the same combined parity/EDS sign already isolated earlier.

## 5. Exact replay

```text
8 public toy curves
1 fixed secp256k1 instance with known scalar indices
294 sampled nonzero scalars
294 raw-state identities
2,352 full-field offset identities
2,058 offset-recurrence identities
294 canonical residual-phase identities
0 arithmetic errors
```

Three small toy groups are checked on their complete nonzero orbits. Larger toy groups and fixed secp256k1 are checked on deterministic public scalar sets, including endpoints and interior positions.

## 6. Decision

```text
Full-field Ward near-period family             constructed
Public logarithmic evaluation                  yes
Every offset a is a power of Phi_raw            yes
Independent information from changing a        no
Residual secp binary phase                      parity times rho_G
Cheap nonlinear decoder of Phi_raw              not found
Second independent open section                 not found
Ordered-sector evaluator                        not found
Parity oracle                                   not found
```

This is stronger than the C44 sign closure: even before taking a character, the complete Ward offset family is one-dimensional.

## 7. Successor

The next target is

```text
SECOND-INDEPENDENT-OPEN-SECTION-C46
```

A positive construction must do at least one of the following:

1. construct an unsquared, generator-sensitive field section that is not a public function of `Phi_raw` alone;
2. construct a genuinely short nonlinear circuit that decodes the ordered sector directly from `Phi_raw`;
3. couple `Phi_raw` to a theta, elliptic-unit, p-adic, or other independently transforming section before taking a norm, square, or character.

Another Ward offset, ratio, product, or rational power is not new: C45 proves that it remains inside the same one-state family.

## Claim boundary

The all-offset identity uses the standard division-polynomial composition and Ward quasi-period laws, with exact executable replay on the declared instances. It closes independence of this Ward family, not arbitrary nonlinear functions of `Phi_raw`, theta functions, elliptic units, p-adic constructions, modular composition, or unrestricted arithmetic circuits.
