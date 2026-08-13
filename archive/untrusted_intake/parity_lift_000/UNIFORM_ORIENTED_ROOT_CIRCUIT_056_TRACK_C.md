# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C: uniform high-degree straight-line circuits

Date: 2026-08-13

Status: **degree comparable with `n` is compatible with a genuinely uniform
`O(log n)` straight-line program, so algebraic degree alone cannot exclude a
sub-square-root evaluator. This degree-compression fact does not construct the
generator-oriented root `Y_G`: the explicit short witnesses are unchanged under
`G -> -G` and therefore fail the mandatory orientation gate.**

The executable scope is limited to public secp256k1 constants and the fixed toy
instances already frozen by package 046.

## 1. Central target remains unchanged

For an odd prime-order subgroup

```text
H=<G>, |H|=n, Q=[k]G,
```

track C keeps exactly the target

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
```

with the complete charged budget

```text
C_preprocessing
+C_advice
+C_memory
+C_representation
+C_online
=O(n^(1/2-epsilon)).
```

A circuit is not admitted if a degree-`Theta(n)` coefficient table, hidden
basis, multiplication table, curve-specific oracle, or instruction DAG of
comparable size is treated as free.

## 2. Exact circuit model used for the boundary

Consider a straight-line program over a field whose primitive gates are

```text
+, -, *, /.
```

For a rational value `f=N/D`, define

```text
delta(f)=max(deg N, deg D).
```

Cancellation may reduce this quantity, so the following is an upper bound. For
every binary gate applied to values with caps `delta_1` and `delta_2`, the new
numerator and denominator have degree at most

```text
delta_1+delta_2.
```

If `D_s` is the maximum cap after `s` gates, then

```text
D_0 <= 1,
D_(s+1) <= 2 D_s,
D_s <= 2^s.                                      (C1)
```

A degree-`d` output therefore forces only the degree-based lower bound

```text
s >= ceil(log_2 d).                              (C2)
```

It does not force `Omega(d)` or `Omega(sqrt(d))`. The same envelope applies to a
DAG with arbitrary fan-out: sharing can reduce stored nodes, but one ordinary
binary gate still cannot increase the current rational-degree cap by more than
a factor of two.

## 3. Tight uniform witness

The logarithmic boundary is attained exactly. Start with a register containing
`X` and repeat

```text
r <- r*r
```

`s` times. The resulting uniform program has

```text
instruction count = s,
output             = X^(2^s),
output degree      = 2^s.                         (C3)
```

For an arbitrary positive exponent `e`, left-to-right binary exponentiation
uses exactly

```text
(bitlength(e)-1)+(popcount(e)-1)                  (C4)
```

field multiplications in the emitted program. Thus a degree on the scale of the
secp256k1 subgroup order can occur in a few hundred uniform instructions.

## 4. Exact secp256k1 degree-scale audit

Let

```text
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
M = (n-1)/2.
```

A monomial at the maximal possible interpolation degree scale, `X^(M-1)`, has

```text
bitlength(M-1)             = 255,
popcount(M-1)              = 195,
squarings                   = 254,
multiplications by X        = 194,
total field multiplications = 448.                (C5)
```

The exact replay reconstructs exponent `M-1` from those instructions.

Two conservative charged ledgers are recorded.

### 4.1 Streamed binary program

```text
preprocessing   0
advice          0
memory          2
representation  255
online          448
full total      705
```

### 4.2 Materialized instruction program

```text
preprocessing   255
advice          0
memory          2
representation  448
online          448
full total      1153
```

Both totals are `O(log n)` and far below the square-root scale. They certify
only a same-degree monomial program, not a program for `Y_G`.

## 5. Mandatory `G -> -G` audit

The repeated-squaring and binary-power programs depend only on the exponent and
input variable. Their code is identical when the marked generator changes from
`G` to `-G`.

The target root satisfies

```text
Y_(-G)=-Y_G,                                     (C6)
```

and the target bit is complemented for a fixed query point. Therefore a
compiler satisfying

```text
compile(G)=compile(-G)                            (C7)
```

cannot be correct for both marked generators. The Lean artifact formalizes this
as a compiler-level consequence of the existing generator-orientation
blindness theorem.

The short high-degree witnesses fail this gate deliberately and are not
candidate evaluators.

## 6. Full representation-cost boundary

Let the complete cost object be

```text
(preprocessing, advice, memory, representation, online).
```

If an implementation explicitly materializes at least `L` field elements,
coefficients, basis vectors, or instructions, then

```text
L <= C_representation <= C_total.                 (C8)
```

Consequently a claimed full budget below `L` is impossible for that declared
representation.

For `Y_G`, an explicit coefficient vector has up to `M` entries. It remains
`Theta(n)` even when Horner evaluation or a balanced DAG is later called the
online phase. The coefficient list cannot be moved into preprocessing, advice,
a quotient-algebra basis, or cached constants without being charged.

This closes explicit materialization only. It does not exclude a genuinely
short generator-sensitive algorithm that produces its required constants on
demand.

## 7. Frozen oriented-root certificates reused from package 046

Track C does not introduce a second elliptic-curve implementation. Its workflow
first reruns

```text
ORIENTED-PARITY-DIVISOR-CIRCUIT-046
```

on the six frozen prime-order `j=0` subgroups

```text
n=19,31,67,271,397,433.
```

The predecessor replay checks the square-root congruence, every nonzero parity
identity, all marked-generator orientations, and the global sign change under
`G -> -G`. Track C then imports only the resulting certificates and verifies:

```text
six certificates are present,
every toy Y_G has degree M-1,
every parity replay is exact,
each generator orbit has n-1 orientations,
negating G globally negates the selected root.
```

These facts show that the actual target is high-degree and generator-sensitive.
They do not imply a nonlinear circuit lower bound.

## 8. What track C closes

The following are invalid as general obstructions:

```text
"degree Y_G is Theta(n), therefore its circuit has Theta(n) gates";
"maximal interpolation degree rules out a short evaluator";
"a dense expanded polynomial proves a large nonlinear circuit".
```

The first two are disproved by the exact uniform degree-amplification witness.
The third confuses one representation with minimum straight-line complexity.

The following restricted routes remain excluded when the full cost is charged:

```text
explicit coefficient materialization,
explicit one-leaf-per-root products,
precomputed instruction or basis tables of comparable size,
generator-blind circuit compilers.
```

## 9. What remains open

Track C does not prove a general circuit lower bound for the specific
secp256k1 root `Y_G`. A positive candidate remains admissible only if it gives:

1. a uniform compiler from public `(E,G,n)`;
2. code or constants that transform correctly under `G -> -G`;
3. exact evaluation of `Y_G(x(Q))`, not merely a same-degree function;
4. no materialized `Theta(n)` coefficient, kernel, basis, or advice object;
5. a complete cost ledger below `n^(1/2-epsilon)`;
6. an exact proof or frozen-to-formal bridge for the parity identity.

The narrowed constructive question is:

```text
Can marked-generator orientation enter a short recurrence or composition law
without first materializing the oriented half-kernel?
```

High degree is not by itself the bottleneck. The bottleneck is compact, uniform,
generator-sensitive selection of the correct Kummer branch.

## 10. Formal and executable artifacts

Lean file:

```text
Ecdlp/Proved/UniformOrientedRootCircuitBoundary.lean
```

It kernel-checks:

1. the five-part charged cost ledger;
2. the explicit-materialization contradiction;
3. one-gate degree doubling;
4. the global bound `D_s <= 2^s`;
5. the exact repeated-squaring witness of length `s` and degree `2^s`;
6. the generator-blind compiler obstruction.

Exact replay:

```text
python3 experiments/parity_lift_000/oriented_parity_divisor_circuit.py \
  --out /tmp/oriented_parity_divisor_circuit_results.json 

python3 experiments/parity_lift_000/uniform_high_degree_circuit.py \
  --oriented-root-results /tmp/oriented_parity_divisor_circuit_results.json \
  --out /tmp/uniform_high_degree_circuit_results.json
```

Focused Lean build:

```text
lake build Ecdlp.Proved.UniformOrientedRootCircuitBoundary
```

## 11. Answer

```text
Can degree Theta(n) have a uniform O(log n) SLP?        yes
Exact witness                                           repeated squaring
Arbitrary-exponent witness                            binary exponentiation
Does degree alone give a polynomial lower bound?        no
Does the witness compute Y_G?                           no
Does the witness change under G -> -G?                  no
Do explicit coefficient tables pass full cost?         no
Are frozen Y_G roots maximal-degree and oriented?       yes
General short nonlinear circuit for Y_G                 open
Public parity / absolute EDS-residue oracle             absent
Classical sub-sqrt ECDLP                                 absent
```

The scoped result is not a parity evaluator. It removes an invalid no-go
argument and makes the positive search more precise: only a compact,
marked-generator-sensitive construction of the actual root `Y_G` can advance
the central target.
