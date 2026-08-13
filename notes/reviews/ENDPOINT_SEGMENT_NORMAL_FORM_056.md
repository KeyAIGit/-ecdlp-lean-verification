# UNIFORM-ORIENTED-ROOT-CIRCUIT-056
## Track A: endpoint EDS segment products

Date: 2026-08-13

Branch: `research/uorc056-endpoint-segment`

Base: `research/parity-lift-000`

Status: scoped negative result for three explicitly declared endpoint grammars.

The central task is unchanged:

```text
A(E,G,Q) = Y_G(x(Q))/y(Q) = (-1)^k,  Q=[k]G,
```

with preprocessing, advice, memory, representation, precision, branch
selection, and online work all charged inside the target cost bound.

## 1. Exact EDS segment identity

Use the inherited notation

```text
rho_k = chi(psi_k(G))
u_k   = chi(phi_raw([k]G))
c     = chi(phi_raw(G)).
```

The point-function relation gives

```text
u_k = c^k rho_k.
```

For the adjacent residue sign

```text
delta_k = rho_(k+1) rho_k,
```

this implies

```text
delta_k = c u_(k+1) u_k.
```

For every ordinary non-wrapping segment `1 <= a < b < n`, define

```text
Seg(a,b) = product_(a <= i < b) delta_i.
```

Then

```text
Seg(a,b)
  = rho_a rho_b
  = c^(b-a) u_a u_b.
```

All internal public phases cancel. After removing the endpoint contribution,
the exact residual is

```text
Seg(a,b) u_a u_b = c^(b-a).
```

For the fixed secp256k1 generator used by the parent line, `c = -1`. Hence the
remaining factor is the segment-length parity character. The global product
isolates the missing bit but does not eliminate it.

Binary composition is exact:

```text
Seg(a,b) = Seg(a,m) Seg(m,b),  a < m < b.
```

However every parenthesization preserves the same residual `c^(b-a)`.

## 2. Additive endpoint-coboundary normal form

The formal additive grammar is

```text
edge(i) = defect + potential(i+1) - potential(i).
```

Every consecutive segment satisfies

```text
segment(start,length)
  = length • defect
    + potential(start+length)
    - potential(start).
```

Thus binary parenthesization can telescope only the endpoint potential. The
remaining state is the length character `length • defect`.

Formal file:

```text
Ecdlp/Proved/EndpointCocycleNormalForm.lean
```

## 3. Conjugated-product normal form

For a group-valued transition system

```text
T_i = B_(i+1) C B_i^(-1),
```

the ordered product has the exact form

```text
T_(b-1) ... T_a = B_b C^(b-a) B_a^(-1).
```

Removing the endpoint gauges leaves `C^(b-a)`. This is the noncommutative
analogue of the same length character.

Formal file:

```text
Ecdlp/Proved/ConjugatedProductNormalForm.lean
```

## 4. Uniform endpoint-summary separation theorem

The consequences file proves two restricted separation statements.

First, suppose a map sees only the two endpoint potential values and must return
the additive segment for every potential and every length. Then the constant
defect must be zero.

Second, suppose a map sees only the two endpoint basis values and must return
the ordered conjugated product for every basis and every length. Then the
constant transition must be the identity.

The proof compares zero-length and one-edge instances whose visible endpoint
summary values coincide. It is therefore a theorem about the declared summary
grammars, not an information-theoretic lower bound for algorithms that use full
curve coordinates.

The same file specializes the additive residual to `ZMod 2`: with unit defect,
the normalized residual is exactly the segment length modulo two.

Formal file:

```text
Ecdlp/Proved/EndpointNormalFormConsequences.lean
```

## 5. Product-tree accounting

A balanced product tree changes parallel depth but not total charged work. A
segment of length `L` still requires

```text
L leaf values
L - 1 combines
ceil(log2 L) parallel depth
```

unless a separate primitive evaluates a long block without materializing its
leaves. The product tree itself is not that primitive.

## 6. Recurrence and compact-representation audit

Known-index Ward or division-polynomial recurrences can evaluate an EDS term
using a double-and-add chain when the integer index is supplied. The present
input is the public point `Q=[k]G`, not the canonical integer `k`. Supplying the
addition chain, midpoint choices, or the low bits of `k` would move the missing
information into advice or branch selection.

A transposed-evaluation method faces the same gate. An anchored prefix
functional contains an unknown cut at the canonical index. A positive method
must generate a different endpoint functional from `(E,G,Q)` without storing or
receiving that cut.

Analytic sigma, elliptic-net, theta, p-adic, and modular-composition
representations are not closed by this result. They remain valid candidates
only if they provide a public orientation or branch normalization and include
all representation and precision costs.

## 7. Decision boundary

Closed in this track:

```text
1. additive endpoint summaries that are a public potential coboundary plus one
   constant defect;
2. arbitrary binary parenthesizations inside that grammar;
3. group-valued products gauge-conjugate to one constant transition;
4. endpoint-only maps whose visible state is restricted to the two potential or
   basis summary values formalized above.
```

Not closed:

```text
1. genuinely nonconstant jump laws;
2. coordinate-sensitive formulas using more than the declared endpoint summary;
3. analytic or p-adic sections with a public branch normalization;
4. transposed or modular-composition methods that generate the unknown cut
   rather than receive or store it;
5. the full UNIFORM-ORIENTED-ROOT-CIRCUIT-056 target.
```

No uniform evaluator for `Y_G(x(Q))/y(Q)`, public parity oracle, absolute EDS
residue oracle, or classical sub-square-root ECDLP algorithm has been obtained.

## 8. Next exact Track A subproblem

The next candidate must provide a public, genuinely nonconstant segment state

```text
S(E,G,P,Q)
```

with an associative composition law

```text
S(P,R) = Compose(S(P,Q), S(Q,R)),
```

such that `S(G,Q)` yields the required oriented residue, while all of the
following remain true:

```text
1. no canonical midpoint or scalar distance is supplied;
2. no checkpoint table or cut vector stores the answer;
3. the state is not gauge-conjugate to one constant transition;
4. generator reversal changes the oriented output correctly;
5. every preprocessing, advice, state-size, and evaluation cost is charged.
```

The first concrete source of candidate jump laws should be the four-term Ward
recurrence and rank-two elliptic-net identities. Every candidate should first be
normalized by the endpoint-coboundary theorem above; only the genuinely
nonconstant residual deserves further evaluation.

## Sources

- Kristin E. Lauter and Katherine E. Stange, *The elliptic curve discrete
  logarithm problem and equivalent hard problems for elliptic divisibility
  sequences*, SAC 2008, arXiv:0803.0728.
- Katherine E. Stange, *Elliptic nets and elliptic curves*, Algebra & Number
  Theory 5 (2011), arXiv:0710.1316.
