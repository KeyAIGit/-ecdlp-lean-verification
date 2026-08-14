# GPT Pro focused continuation

## ENDPOINT-GAUGE-TRANSPOSED-EVALUATION-064

Work only on the UORC056 uniform-circuit track. Reproduce C9-C13 before extending them. Use only the six frozen toy curves, known toy scalars, public generator replacements, and public secp256k1 constants. Do not accept an unknown-scalar external point, wallet, or production key.

## Central target

Let

```text
H=<G>, |H|=n=2m+1,
D=sum_k d_k([k]G),
D0=(A)-(O),
A=[a]G,
div(h_G)=D-D0.
```

C13 proves

```text
f_G(P)=constant*c_(A,-G)(P)*h_G(P)/h_G(P+G),
```

where `c_(A,-G)` is a public four-point Miller quotient. Therefore compute

```text
Z_G(Q)=h_G(Q)/h_G(Q+G), Q=[k]G,
```

or its regularized local valuation, with complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon))
```

for one fixed `epsilon>0`.

## Established facts that must not be renamed as progress

```text
1. canonical parity is exact and equals the local valuation of f_G;
2. ordinary Miller products need linear support;
3. C11 gives an exact soft-O(sqrt(n)) oriented evaluator with 4-jets;
4. nested dense blocks/resultants do not beat sqrt(n);
5. translated multiplicative divisor rank is n-1;
6. a one-state rational telescoper has degree at least n;
7. C13 compresses the entire length-L cocycle to one four-point Miller factor;
8. the only remaining scalar datum is the endpoint gauge h_G(P)/h_G(P+G);
9. deg_poles(h_G) is r or r+1, r=floor((n+1)/4);
10. high degree alone is not a circuit-size lower bound.
```

## Mandatory attack order

### A. Transposed endpoint difference

Try to compute the ratio or logarithmic derivative of `h_G` at the two adjacent points simultaneously, without materializing `h_G`. Use transposition principles, subproduct-tree reversal, rational interpolation duality, or a direct local-jet functional. Charge coefficient generation and every representation.

A method that performs two independent square-root evaluations is not progress.

### B. Explicit generalized-Jacobian model

Construct the `G_m`-extension associated with `A in Pic^0(E)` in explicit public coordinates. Determine whether a canonical lift of `Q` and a scalar comparison of the fibres at `Q` and `Q+G` can be computed without choosing the meromorphic gauge `h_G`.

Required fork:

```text
positive: give formulas and complete sub-sqrt cost;
negative: prove that every scalar readout in the declared coordinate model factors through a rational trivialization whose transition function is h_G or an equivalent branch input.
```

Do not count an abstract line-bundle isomorphism as a field-valued evaluator.

### C. Addition-enabled principal-divisor circuit

Search for a short circuit for the principal divisor

```text
E_G=D-(A)+(O).
```

Allowed primitives include additions of rational sections, derivatives, residues, intersections, structured determinants not already covered by the common-basis Frobenius-Stickelberger theorem, and nonlinear coordinate recurrences.

The circuit must output the endpoint ratio or its local valuation, not a dense numerator/denominator.

### D. Scoped lower bounds

If no construction survives, prove a theorem for one explicit grammar, such as:

```text
bounded-dimensional generalized-Jacobian coordinate charts,
affine determinantal scalar readouts,
fixed-rank displacement/Hankel endpoint functionals,
finite collections of rational trivializations,
or transposed product trees whose states have declared degree/support bounds.
```

The theorem must charge preprocessing, advice, memory, and representation. Do not infer circuit size from polynomial degree alone.

### E. Multilinear resultants only after A-D

A true three-way or higher resultant is relevant only if applied to the endpoint-gauge support and if it avoids a degree-sqrt intermediate. Standard nested binary elimination and affine Macaulay/multiplication matrices are already noncompetitive.

## Positive completion gate

A positive result must include all of:

```text
exact identity for every nonzero Q in H,
public handling of Q at every divisor point,
generator covariance under G -> [u]G,
regularized local-jet extraction,
complete all-in O(n^(1/2-epsilon)) cost,
independent frozen replay,
no hidden scalar, branch table, fibre lift, or sqrt-sized advice.
```

## Negative completion gate

A negative result must state a precise computation grammar and prove a sqrt-scale or stronger lower bound inside it. Finite toy failure is supporting evidence only.

## Required deliverables

```text
1. theorem-first memo with exact conventions;
2. deterministic Python replay and JSON result;
3. explicit cost ledger;
4. positive or negative mechanism classification;
5. strongest successor question;
6. no claim of a parity oracle unless the complete cost gate passes.
```
