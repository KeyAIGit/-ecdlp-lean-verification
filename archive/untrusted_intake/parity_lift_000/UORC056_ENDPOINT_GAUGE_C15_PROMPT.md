# GPT Pro focused continuation

## ENDPOINT-GAUGE-TRANSPOSED-FUNCTIONAL-065

Work only on the UORC056 endpoint-gauge branch. Reproduce C9-C14 before extending them. Use only frozen toy curves, known toy scalars, public generator replacements, and public secp256k1 constants. Never accept an unknown-scalar external point, wallet, or production key.

## Central target

For

```text
H=<G>, |H|=n,
Q=[k]G,
div(h_G)=E_G=D-(A)+(O),
```

compute

```text
Z_G(Q)=h_G(Q)/h_G(Q+G)
```

or its regularized local valuation with complete charged cost

```text
C_preprocessing+C_advice+C_memory+C_representation+C_online
=O(n^(1/2-epsilon))
```

for one fixed `epsilon>0`.

C13 already compresses the entire original length-`m` product to

```text
f_G(Q)=constant*c_(A,-G)(Q)*Z_G(Q),
```

and C14 proves that a rational scalar readout from the abstract `G_m`-torsor is itself a gauge choice. Do not return to ordinary Miller accumulation or claim that an abstract fibre coordinate is a field-valued evaluator.

## secp256k1 support normal form

For secp256k1,

```text
n=8s+1,
A=[s]G,
```

and

```text
E_G
 =(O)+sum_(j=0)^(2s-1)(-[2j+1]G)
 -( [s]G )-sum_(j=0)^(2s-1)([2j+1]G).
```

The positive and negative degrees are `2s+1=(n-1)/4+1`.

## Mandatory attack order

### 1. Adjacent transposed functional

Derive an algorithm that computes the ratio at `Q` and `Q+G` jointly. Test transposed subproduct trees, rational interpolation duality, logarithmic derivatives, residues, and local jets. Two independent soft-square-root evaluations do not count as progress.

### 2. Quarter-kernel structure

Exploit the signed odd quarter-orbit in the displayed divisor. Determine whether it is a decimation, trace, norm, or first variation of a public full-kernel object. A valid formula must preserve marked-generator orientation under `G -> [u]G`.

### 3. CM and GLV action on the quarter orbit

For secp256k1, test the exact action of the order-three GLV eigenvalue on the odd quarter set and its boundary. Quantify orbit fragmentation and determine whether a bounded number of CM orbit aggregates reconstructs the endpoint ratio. Charge every exceptional set and coefficient table.

### 4. Fixed-rank transposed states

Test whether the endpoint functional has bounded displacement, Toeplitz, Hankel, Cauchy, or recurrence rank after public coordinate transforms. If it does not, prove a scoped rank lower bound for the declared state grammar. Degree alone is not a circuit lower bound.

### 5. Addition-enabled section circuit

Search for a short arithmetic circuit for the prescribed principal divisor `E_G`, allowing addition and subtraction of sections, derivatives, residues, intersections, structured determinants outside the already closed common-basis ladder, and nonlinear recurrences. The output must be `Z_G(Q)` or its local valuation, not a dense function.

## Positive gate

A positive result requires:

```text
exact identity for every nonzero Q in H,
regularized handling of all divisor points,
generator covariance,
complete all-in sub-square-root cost,
independent replay,
no hidden scalar, gauge table, fibre lift, or sqrt-sized advice.
```

## Negative gate

A negative result must define an explicit computation grammar and prove a square-root-scale or stronger lower bound within it. Toy failures alone are not enough.

## Required deliverables

```text
theorem-first memo,
deterministic replay and JSON,
complete cost ledger,
mechanism classification,
strongest successor question,
no parity-oracle claim unless the full gate passes.
```
