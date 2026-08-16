# UORC-056 C40: equivariant transfer gauge boundary

Status: exact structural no-go for public-action coherence alone. No parity oracle or sub-square-root ECDLP algorithm is claimed.

## Setup

C39 reduces parity decoding to choosing an oriented root section on the split pair quotient:

\[
R_i^2=q_i,
\qquad
1\le i\le r,
\qquad
r=(n-1)/2.
\]

Public multipliers such as doubling and the GLV automorphism permute the pair components. In the C39 spectral coordinate, define

\[
L_u(z_i)=z_{ui},
\qquad
T_u(z_i)=\frac{R_{ui}}{R_i}.
\]

The exact square-transfer identity is

\[
\boxed{
T_u(z_i)^2
=\frac{z_i^2-4}{L_u(z_i)^2-4}.
}
\]

Every multiplier cycle satisfies the Hilbert-90 loop identity

\[
\prod_{j=0}^{m-1}T_u(L_u^j(z))=1.
\]

## Gauge theorem

Choose any sign function

\[
s_i\in\{\pm1\}
\]

and replace the oriented section by

\[
R_i'=s_iR_i.
\]

Then

\[
\boxed{
T_u'(i)=s_{ui}s_iT_u(i).
}
\]

This transformation preserves:

- all public root squares `R_i^2`;
- all public transfer squares `T_u(i)^2`;
- every multiplier cocycle identity;
- every product around every closed multiplier loop.

Fixing one anchor sets one `s_i`, but leaves exactly

\[
\boxed{2^{r-1}}
\]

coherent root sections. Adding more public multipliers does not change this gauge count. If their action graph is connected, oriented edge values would determine the section from the anchor, but their squares and loop identities do not determine those edge values.

Therefore public doubling/GLV incidence and Hilbert-90 coherence alone cannot select parity orientation.

## Exact frozen replay

For the five frozen curves, both the pair-coordinate map `L_u` and the oriented transfer `T_u` were interpolated for `u=2` and `u=lambda`.

In every case:

```text
deg L_u = r-1,
support L_u = r,
deg T_u = r-1,
support T_u = r.
```

Thus the low-degree Lattes appearance in the original Kummer coordinate is not retained after conjugation into the Miller spectral coordinate. The coordinate and transfer polynomials are dense on every frozen quotient.

The replay verifies all square-transfer identities, every multiplier-cycle norm identity, and deterministic nontrivial gauge transformations preserving all public squared and loop data.

## secp256k1 consequence

Exact modular-order arithmetic gives

\[
\operatorname{ord}_n(2)=\frac{n-1}{2}=r.
\]

Hence doubling is transitive on the secp256k1 pair quotient. Even in this strongest connected case, one anchor plus all public doubling incidence, transfer squares, cocycle laws and loop products leaves

\[
\boxed{2^{r-1}}
\]

coherent oriented sections.

Transitivity is therefore not the missing ingredient. A positive decoder must provide at least one genuinely oriented numerical transfer or another relation that is not invariant under the componentwise sign gauge.

## Decision

Closed in C40:

- the idea that doubling or GLV connectivity itself couples the C39 component signs;
- the idea that Hilbert-90 loop products select the root section;
- low-degree coordinate or transfer polynomials in the C39 spectral coordinate;
- adding arbitrary public multiplier edges without a generator-sensitive edge-value law.

The next admissible route must break the gauge symmetry. It must evaluate an oriented transfer, or produce a nonlinear generator-sensitive relation whose value changes under `R_i -> s_i R_i`. A relation built only from squares, public permutations and closed-loop products cannot decode parity.