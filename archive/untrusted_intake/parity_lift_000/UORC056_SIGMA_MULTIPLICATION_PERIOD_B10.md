# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — SIGMA MULTIPLICATION PERIOD B10

Date: 2026-08-14

Status: **the alternating parity index set has trivial translation stabilizer on a prime-order cycle. There is no proper periodic block or lower-order subgroup whose sigma/multiplication formula isolates the oriented half. The only nontrivial translation orbit is the full kernel, whose product is the generator-blind degree-`n` Miller object.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all-in `O(n^(1/2-epsilon))` cost.

Package B8 represents the oriented factor by the alternating index set

```text
S_odd={1,3,...,2M-1},
n=2M+1.                                             (B10.1)
```

A standard multiplication formula would be useful if this set decomposed into short periodic or subgroup orbits.

## 2. No proper nontrivial period

Let `n` be prime and let `t!=0 mod n`. Translation by `t` has orbit length

```text
n/gcd(t,n)=n.                                      (B10.2)
```

Thus every nonempty set invariant under translation by `t` is the full cycle.

But

```text
#S_odd=M,
0<M<n.                                             (B10.3)
```

Therefore

```text
boxed:
S_odd+t != S_odd for every t!=0 mod n.             (B10.4)
```

The same holds for the even half.

Equivalently, the translation stabilizer of either oriented half is trivial.

## 3. Consequence for subgroup multiplication formulas

The cyclic group of prime order has no nontrivial proper subgroup. Standard sigma or isogeny multiplication formulas naturally factor products over:

```text
a full finite subgroup,
a full orbit under a subgroup,
or a union of subgroup cosets.                    (B10.5)
```

For the public kernel `H=<G>`, the only subgroup choices are:

```text
{O},
H.                                                 (B10.6)
```

The full `H` product is the ordinary degree-`n` Miller/kernel norm already isolated in B8:

```text
H_G(P)J_G(P)=f_(n,G)(P).                          (B10.7)
```

It is invariant under swapping the two parity halves and does not choose `H_G`.

Therefore a standard lower-period sigma multiplication formula cannot compress the alternating half. Any useful formula must be a genuinely nonperiodic endpoint/segment identity or a new nonlinear special-function relation.

## 4. Why step two does not create a smaller cycle

The local cocycle in B8 uses translation by `2G`. Since `n` is odd prime,

```text
gcd(2,n)=1,                                       (B10.8)
```

so `2G` also generates the entire subgroup. The two-step traversal is only a reordering of all `n` points, not a cycle of length `M`.

The unique parity cut appears when that full traversal wraps through the canonical representative boundary.

## 5. Frozen exact replay

`uorc056_sigma_multiplication_period.py` uses the ten frozen prime orders from B4-B9. For every nonzero translation it verifies:

1. the translation orbit of zero has length `n`;
2. the odd half is not invariant;
3. the even half is not invariant;
4. translation by two also has full orbit;
5. the two halves partition the nonzero labels but their union is not a subgroup.

No curve point or unknown scalar is evaluated.

## 6. Formalization boundary

`Ecdlp/Proved/SigmaMultiplicationPeriodBoundary.lean` kernel-checks that a nontrivial divisor/period of a prime order equals the full order and that the canonical half has cardinality strictly between zero and `n`.

It does not formalize sigma functions, isogenies, elliptic curves, secp256k1, parity recovery, or ECDLP.

## 7. Answer for this B-track class

```text
Translation stabilizer of the parity half                  trivial
Proper subgroup/coset decomposition                        none
Orbit length of step 2                                     n
Standard subgroup multiplication formula                   full kernel only
Does full kernel norm select the alternating factor?       no
Public parity / absolute EDS oracle                        absent
Sub-square-root ECDLP                                      absent
```

## 8. B-track conclusion

The standard Kummer/CM route has now produced one exact positive object and a clean boundary:

```text
positive: alternating Miller potential with fast local edge,
closed: symmetric kernels, explicit resultants, transposed linear states,
        bounded linear CM states, proper-period sigma products,
open:   endpoint-only nonlinear evaluation of the alternating potential.
```

The open endpoint problem is exactly the structured segment primitive being studied in track A. A further B-specific claim now requires a new identity, not another representation of the full kernel norm.
