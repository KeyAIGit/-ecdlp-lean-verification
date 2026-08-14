# GPT Pro focused continuation

## HIGH-DEGREE-INVARIANT-ADDITION-CIRCUIT-067

Work only on the UORC056 endpoint-gauge branch. Reproduce C9-C16 before extending them. Use only frozen toy curves, known toy scalars, public generator replacements, and public secp256k1 constants. Do not accept an unknown-scalar external point, wallet, or production key.

## Central target

C16 defines

```text
N_phi Z(P)=Z(P)Z(phi(P))Z(phi^2(P))=R_G(y(P)).
```

This invariant flips sign under the global branch change `Z -> -Z`, so it is a valid branch selector. But its descended divisor has

```text
nonzero support >= (n-1)/3-4,
pole degree >= (n-1)/6-2.
```

Compute `R_G(y(Q))` or its regularized local valuation with complete charged cost

```text
O(n^(1/2-epsilon))
```

without constructing `R_G` densely, evaluating three independent endpoint gauges, or receiving a branch seed.

## Mandatory attack order

### A. Cubic Kummer norm decomposition

For a rational section written as

```text
C(x,y)=C0(x^3,y)+x*C1(x^3,y)+x^2*C2(x^3,y),
```

use the exact norm identity

```text
Norm(C)=C0^3+x^3*C1^3+x^6*C2^3-3*x^3*C0*C1*C2.
```

Determine whether the three residue-class components of the C13/C10 gauge admit short public recurrences. Charge their construction and representation. Merely rewriting a dense polynomial into three dense polynomials is not progress.

### B. Division-polynomial / elliptic-net recurrence

Test whether the descended invariant, unlike the original oriented branch, is expressible by a fixed number of high-index division/net values with public indices. Reapply the exact gauge and support gates. A formula whose branch selection is hidden in one input is rejected.

### C. Transposed y-line evaluation

Treat the descended divisor as structured input on the `y`-line. Search for transposed multipoint evaluation, rational interpolation duality, displacement structure, or modular composition with state `o(sqrt(n))`. Dense coefficient or point lists are charged.

### D. Addition-enabled circuit

Search for a short circuit using additions, multiplications, derivatives, residues, and resultants whose output is `R_G(y(Q))`. Degree alone is not a rejection. The circuit must be explicit and generator-covariant.

### E. Scoped lower bound

If no construction survives, prove a square-root or stronger bound in one declared grammar: bounded-width invariant recurrence, finite high-index net expressions, transposed divisor blocks, or cubic-residue-class circuits with charged component state.

## Completion gates

A positive result must handle every subgroup point, all divisor collisions, generator replacement, complete preprocessing/advice/memory/representation cost, and independent replay. A negative result must state the exact grammar. Do not claim a parity oracle unless the full cost gate passes.
