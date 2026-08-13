# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — MILLER KERNEL EDGE B2

Date: 2026-08-13

Status: **the standard fast Miller function attached to a public subgroup point gives a relative two-endpoint EDS-residue edge, not the absolute generator-oriented root. Finite products of such functions remain invariant under the global EDS sign gauge.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target is not renamed:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all-in cost below the square-root generic baseline.

For the EDS residue

```text
rho_G(k)=chi_p(psi_k(G)),
```

the unresolved information is one absolute generator-relative sign. Public adjacent ratios determine only relative edges.

## 2. Why the Miller function is a serious candidate

For a public point `R` of order `n`, the Miller function `f_(n,R)` has divisor

```text
div(f_(n,R))=n(R)-n(O).
```

Miller's double-and-add algorithm evaluates `f_(n,R)(Q)` in `O(log n)` line-function steps. Thus, if its quadratic character were parity or the absolute EDS residue, the central task would be solved immediately.

The package tests this candidate before any larger kernel-product or modular-composition construction.

## 3. Exact relative-edge law under the standard normalization

Let

```text
R=[r]G,
Q=[k]G,
k != r,0.
```

The sigma/Weil-function description of `f_(n,R)` restricts on the cyclic subgroup to the ratio of the two endpoint sigma values at `k-r` and `k`, multiplied by a normalization depending on `R` but not on `k` at the quadratic-character level.

The resulting sign law is

```text
boxed:
chi_p(f_(n,[r]G)([k]G))
 = c_G(r) * rho_G(k-r) * rho_G(k),               (M1)
```

where `c_G(r)` is independent of `k`; the signed integer `k-r` is used before periodic reduction.

The load-bearing conclusion is the endpoint count: every Miller character contains two residual EDS factors.

The branch treats `(M1)` as a scoped Miller/Weil normalization statement and independently replays it in exact finite-field function arithmetic on the frozen corpus. It does not infer the field-level value of the Miller function from the character identity.

## 4. Gauge obstruction

Replace every residue sign by its global negative:

```text
rho'_G(j)=-rho_G(j).
```

Then each Miller edge is unchanged:

```text
rho'_G(k-r)rho'_G(k)
 =rho_G(k-r)rho_G(k).                            (M2)
```

Therefore every finite product or ratio of public Miller characters is also unchanged by the global gauge flip.

But the desired absolute residue changes sign:

```text
rho'_G(k)=-rho_G(k).                             (M3)
```

Hence this entire multiplicative Miller-function class cannot select the missing absolute EDS orientation. In particular, it cannot construct `Y_G` by multiplying any finite collection of standard Miller kernel functions whose centres and exponents are public.

This is a mechanism-class result, not a lower bound against sums of Miller values, nonmultiplicative circuits, derivatives with a new normalization, or arbitrary arithmetic circuits.

## 5. Why taking an n-th root does not help

For secp256k1,

```text
gcd(n,p-1)=1.
```

Thus raising to the `n`-th power is an automorphism of `F_p^*`, and a unique field-value `n`-th root may be taken. Since `n` is odd, this operation preserves quadratic character. It can change the field representative but cannot turn the gauge-even edge `(M1)` into one absolute residue factor.

## 6. Frozen exact replay

`uorc056_miller_kernel_edge.py` implements Miller functions as exact elements

```text
(A(x)+B(x)y)/D(x)
```

of the function field `F_p(E)`, with polynomial gcd cancellation after every operation. It does not evaluate through potentially singular intermediate line quotients.

The frozen cofactor-one prime-order curves are

```text
(p,n)=(13,7),(43,31),(61,61),(67,79),(79,67),(97,79),
      (127,127),(163,139),(211,199),(349,313).
```

For public centre scalars

```text
r in {1,2,3,5,7}
```

when admissible, and every nonzero `k != r`, the replay checks:

1. the Miller divisor function is nonzero and finite at `[k]G`;
2. `chi(f_(n,[r]G)([k]G))*rho(k-r)*rho(k)` is independent of `k`;
3. the predicted edge is invariant under the global residue flip;
4. the public Miller character is not promoted to parity from bounded coincidence;
5. the loop length is logarithmic in `n`.

All arithmetic is exact. No target outside the frozen corpus is accepted.

## 7. Formalization boundary

`Ecdlp/Proved/MillerKernelEdgeBoundary.lean` kernel-checks the binary gauge core:

```text
edge_rho(r,k)=rho(k-r)+rho(k) in ZMod 2,
edge_(rho+1)(r,k)=edge_rho(r,k).
```

It also proves invariance for finite sums of such edge labels and the elementary indistinguishability consequence for any decoder that receives only gauge-invariant Miller-edge data.

The Lean file does not formalize elliptic curves, Miller functions, sigma functions, division polynomials, secp256k1, or the analytic derivation of `(M1)`.

## 8. Answer for this candidate

```text
Miller evaluation cost                                  O(log n)
Does one Miller character expose a nontrivial sign?     yes
What sign?                                              relative edge rho(k-r)rho(k)
Residual EDS weight                                     2
Global EDS gauge invariant?                             yes
Can finite multiplicative Miller data select rho(k)?   no
Can it select Y_G/parity?                               no
Public parity / absolute EDS oracle                     absent
Sub-square-root ECDLP                                   absent
```

## 9. Remaining B-track classes

The next B-track gates are:

1. the compact Frobenius-minus-identity kernel map and all invariant local leading data;
2. direct evaluation of the generator-oriented half-divisor rather than a full kernel function;
3. square-root-Velu/index-system product evaluation and its square-root frontier;
4. transposed evaluation or modular composition that does not materialize the degree-`(n-1)/2` factor;
5. a genuinely nonmultiplicative generator-sensitive circuit.

The central target remains `UNIFORM-ORIENTED-ROOT-CIRCUIT-056` throughout.