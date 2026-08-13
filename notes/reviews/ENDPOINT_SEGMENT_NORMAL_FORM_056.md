# UNIFORM-ORIENTED-ROOT-CIRCUIT-056
## Track A: endpoint segment normal form

Date: 2026-08-13

Branch: `research/uorc056-endpoint-segment`

Base: `research/parity-lift-000`

Status: scoped negative result for two declared mechanism classes.

## EDS specialization

Use the parent-line notation

```text
rho_k = chi(psi_k(G))
u_k   = chi(phi_raw([k]G))
c     = chi(phi_raw(G)).
```

The inherited point-function relation gives

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

For every non-wrapping segment `1 <= a < b < n`,

```text
Seg(a,b) = product_(a <= i < b) delta_i
         = rho_a rho_b
         = c^(b-a) u_a u_b.
```

All internal public phases cancel. Removing the endpoint contribution leaves
exactly

```text
Seg(a,b) u_a u_b = c^(b-a).
```

For the fixed secp256k1 generator used by the parent line, `c = -1`. Hence the
remaining factor is the segment-length parity character. The endpoint product
isolates the missing bit but does not eliminate it.

## Additive normal form

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

Thus arbitrary binary parenthesization can telescope only the public endpoint
term. The residual is `length • defect`.

Formal file:

```text
Ecdlp/Proved/EndpointCocycleNormalForm.lean
```

## Conjugated-product normal form

For a group-valued system

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

## Product-tree accounting

A balanced product tree changes parallel depth but not total work. A segment of
length `L` still requires `L` leaf values and `L-1` combines unless a separate
long-block primitive is supplied.

## Decision boundary

Closed in this track:

```text
constant endpoint coboundaries, arbitrary binary parenthesization, and systems
gauge-conjugate to one constant transition.
```

Not closed:

```text
genuinely nonconstant jump laws, coordinate-sensitive formulas, analytic or
p-adic sections, or other representations outside the declared grammars.
```

No endpoint evaluator satisfying the full cost gate has been obtained. The
central task remains `UNIFORM-ORIENTED-ROOT-CIRCUIT-056`.
