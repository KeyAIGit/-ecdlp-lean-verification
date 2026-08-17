# EDS-ABSOLUTE-ORIENTATION-RETURN-042

Date: 2026-08-12

Status: **full branch audit and exact telescoping reduction; the EDS segment primitive on the secp256k1 normalization is equivalent to scalar parity rather than an independent easier hidden layer**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Why return from the Legendre branch

Packages 034 through 041 produced an exact scalar-Legendre observable and several equivalent CM, ray-class, elliptic-Gauss, and Weil descriptions. Package 041 then showed that even a free exact Legendre oracle leaves a separate classical shifted-Legendre inversion problem. No unconditional classical sub-square-root recovery follows.

By contrast, an exact scalar-parity oracle has a literal logarithmic peeling reduction to the full discrete logarithm. The direct parity/EDS line therefore remains the shorter route.

## 2. Audit of the pre-existing cocycle branches

The repository already contains three isolated results that must be incorporated before selecting another object.

### COCYCLE-INTEGRATION-001

For

```text
Q=[k]G,
rho(k)=chi(psi_k(G)),
delta(k)=rho(k+1)rho(k),
```

the local edge `delta(k)` is public, and

```text
rho(k)=product_(i=1)^(k-1) delta(i)
```

with the anchor `rho(1)=1`. The absolute residue is a global primitive of a public local cocycle.

### GENERIC-COCYCLE-INTEGRATION-003

If the closed binary edge labels are treated as otherwise arbitrary, exact target-cut parity requires querying one entire side of the cut. The worst-case query bound is linear. This is a restricted local-oracle theorem, not an EDS lower bound.

### STRUCTURED-SEGMENT-PRIMITIVE-004 and CANONICAL-MIDPOINT-CIRCULARITY-005

A checkpoint-and-walk decoder obeys

```text
space * online_range >= n.
```

The public group half of `[k]G` is not the canonical scalar midpoint when `k` is odd. Selecting the correction branch is exactly the low bit being sought. Retaining both branches doubles the branch count per level unless a new exact compression invariant is supplied.

These results rule out local walking, hidden checkpoint tables, and canonical-midpoint recursion as explanations of a sub-square-root primitive.

## 3. Exact point-function coboundary

Let the raw public point-function character be

```text
u(k)=chi(phi_raw([k]G)),
c=chi(phi_raw(G)).
```

The raw EDS transport law gives

```text
u(k)=c^k rho(k).                                  (E1)
```

Because signs square to one,

```text
delta(k)=rho(k+1)rho(k)
        =c u(k+1)u(k).                            (E2)
```

Thus the public local EDS cocycle is a public point-function coboundary multiplied by one constant sign.

## 4. Exact segment telescoping

For a segment of length `m`, multiply `(E2)`:

```text
product_(i=0)^(m-1) delta(i)
 =c^m u(m)u(0).                                  (E3)
```

All internal public point-function factors occur twice and cancel.

With the EDS anchor `rho(1)=1`, the prefix ending at `[k]G` gives exactly

```text
rho(k)=c^k u(k).                                  (E4)
```

Equation `(E4)` is the same as `(E1)`, now derived as the complete output of every exact local segment integration.

For the fixed secp256k1 generator, the frozen branch certificate has

```text
c=-1.
```

Therefore

```text
rho(k)=(-1)^k u(k),                               (E5)
```

where `u(k)` is public.

## 5. Main decision

On this normalization, the following three tasks are computationally equivalent up to public field/group operations:

```text
absolute EDS residue rho(k),
anchored EDS segment primitive,
canonical scalar parity (-1)^k.
```

Hence a new EDS segment primitive would already be a parity decoder. It is not a weaker intermediate bottleneck.

This is useful because it prevents the research from repeatedly renaming the same missing bit as:

```text
global cocycle primitive,
segment product,
theta branch,
absolute EDS gauge,
point-function normalization.
```

Any successful construction must explicitly explain how it computes the canonical odd-cycle branch cut.

## 6. What remains open after the complete audit

Closed or reduced:

```text
local edge queries alone,
checkpoint plus local walk,
canonical midpoint recursion,
finite multiplicative division-polynomial sections,
near-period sections,
bounded isogeny transports,
local torsion jets in the tested/derived class,
standard theta splitting and pairing-extension routes.
```

Still open:

1. a midpoint-independent binary segment-composition circuit;
2. an `n`-dependent high-degree object with a genuinely short evaluation circuit;
3. a nonlocal additive determinant, resultant, or transfer-matrix identity not reducible to the public point-function coboundary;
4. an analytic or p-adic branch normalization whose full precision and representation cost is sub-square-root;
5. a direct compact evaluator for GLV carry or hard `R3`, which also has a complete oracle-to-ECDLP reduction.

## 7. Selected successor object

The next theorem-first package is

```text
DYADIC-BRANCH-COMPRESSION-043.
```

Its object is the exact correction after `d` public group halvings.

Write

```text
k=2^d q+r,
0<=r<2^d.
```

The publicly computable point

```text
H_d=[2^(-d) mod n]Q
```

has scalar

```text
q + [2^(-d)r mod n].
```

Recovering the canonical quotient `[q]G` requires selecting one correction from exactly `2^d` possible residues `r`.

The package will prove, in a declared affine-selector recursion model:

```text
exact depth-d canonical splitting needs at least 2^d branch states,
```

unless an explicit nonlinear compression invariant is supplied. At depth `d=128` on secp256k1 this reaches the Pollard scale exactly.

A positive escape must provide the nonlinear compressed state and its composition law. A negative result will close the broad family of branch-enumerating binary segment circuits.

## 8. Formalization boundary

`Ecdlp/Proved/EdsAbsoluteOrientationReturn.lean` formalizes the binary cocycle telescoping identity and the public-factor/parity equivalence. It does not formalize division polynomials, the raw point-function source normalization, secp256k1 arithmetic, arbitrary circuit lower bounds, or ECDLP.
