# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C10: jump recurrence equals a carry-defect predicate

Date: 2026-08-14

Status: **the most natural nonlocal jump-recurrence proposal has been reduced exactly to a cyclic carry predicate. A fixed public jump does not create a new smooth orientation law: its only nontrivial information is whether the hidden index crosses the canonical cut at `n`. This reconnects the jump route to the previously identified segment/boundary bottleneck. No compact evaluator is obtained.**

## 1. Setup

Let

```text
H=<G>, |H|=n,
n odd,
P=[i]G, 0<=i<n,
R=[r]G, 0<r<n,
sigma_G([u]G)=(-1)^u for the canonical representative 0<=u<n.
```

Write

```text
c_r(i)=1 if i+r>=n, and 0 otherwise.
```

Then the canonical representative of `P+R` is

```text
i+r-n*c_r(i).
```

Therefore

```text
sigma_G(P+R)
=(-1)^(i+r-n*c_r(i)).
```

Since `n` is odd,

```text
(-1)^(-n*c_r(i))=(-1)^c_r(i).
```

Hence

```text
boxed:
sigma_G(P+R)/sigma_G(P)
=(-1)^r * (-1)^c_r(i).                           (C1)
```

This is the exact jump law.

## 2. The defect is exactly terminal-interval membership

The factor differing from the constant `(-1)^r` is

```text
(-1)^c_r(i).
```

It equals `-1` exactly when

```text
i in {n-r, n-r+1, ..., n-1}.                     (C2)
```

Thus a nonlocal jump multiplier for a fixed known shift `R=[r]G` is equivalent to detecting whether the hidden canonical index of `P` lies in a terminal interval of length `r`.

```text
boxed:
nontrivial jump orientation = cyclic carry across the canonical cut.    (C3)
```

The jump law is not a new independent source of orientation information. It is a repackaging of boundary/segment membership.

## 3. Consequence for doubling jumps

For a known doubling jump

```text
R_j=[2^j]G
```

with the integer representative `r_j=2^j mod n`, equation `(C1)` gives

```text
sigma_G(P+R_j)/sigma_G(P)
=(-1)^r_j * (-1)^c_(r_j)(i).                     (D1)
```

When `r_j` is represented by an even integer below `n`, the nominal multiplier is `+1`; the sign flips only when the addition crosses the canonical cut.

Therefore a proposed fast doubling/jump recurrence must still compute the carry predicate. Repeated doubling by itself does not bypass the hidden-index boundary.

## 4. Primal branch form

From C9,

```text
sigma_G(P)=y(P) r_G(x(P)).
```

Thus any proposed primal jump identity

```text
r_G(x(P+R)) = Phi_R(E,G,P,r_G(x(P)))
```

must, after multiplying by the public `y` ratio, reproduce `(C1)`:

```text
[y(P+R) r_G(x(P+R))] / [y(P) r_G(x(P))]
=(-1)^r * (-1)^c_r(i).                           (P1)
```

Consequently the nontrivial part of `Phi_R` cannot be a globally smooth basepoint-independent constant. It must encode or detect the carry set `(C2)`, or introduce an equivalent divisor/branch defect supported on its boundary.

## 5. Scope of the obstruction

Closed by C10:

```text
fixed-jump recurrences whose claimed advantage is only that the jump length is large,
basepoint-independent jump multipliers,
recurrences that omit the canonical-cut defect,
claims that powers-of-two jumps alone integrate orientation without a boundary test.
```

Not closed:

```text
a genuinely fast public evaluator for the carry predicate,
a nonlinear divisor identity that evaluates terminal-interval membership below sqrt(n),
a compressed oriented product whose first variation exposes the carry without materializing the interval,
an auxiliary cover whose branch crossing computes the carry with a proven exponent improvement.
```

This is a scoped reduction, not a lower bound for arbitrary arithmetic circuits.

## 6. Strategic consequence

The proposed task `FAST-ORIENTED-BRANCH-RECURRENCE-060` must be narrowed. Searching for an arbitrary long-jump recurrence is no longer the right first question, because the exact recurrence is already determined by `(C1)`.

The next high-value question is:

```text
CARRY-DEFECT-COMPRESSION-060

Can the predicate

    c_r(i)=1_{i>=n-r},   P=[i]G,

for one structurally useful family of public shifts r, be evaluated from primal elliptic coordinates with complete cost below n^(1/2-epsilon), without recovering i, storing the interval, or reducing to a known segment walk?
```

A candidate receives priority only if it identifies a concrete non-generic resource that can evaluate the cut crossing more cheaply than generic cyclic search.

## 7. Relation to earlier checkpoints

C9 showed that canonical parity is an oriented etale square-root branch and that local translation recurrence does not compress. C10 identifies the exact obstruction for replacing unit steps by long public jumps: the missing information is a carry across the canonical representative cut.

This explains why earlier segment and midpoint routes repeatedly encountered endpoint information. The boundary is not an artifact of one EDS representation; it is intrinsic to the fact that `(-1)^k` is defined on canonical integer representatives of an odd cyclic group and is not a group character.

## 8. Result flags

```text
jump_carry_identity_found=true
long_jump_without_boundary_test_rejected=true
carry_predicate_compact_evaluation_found=false
compact_sub_sqrt_evaluation_found=false
evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
