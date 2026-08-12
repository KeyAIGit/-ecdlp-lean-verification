# Parity research spine and package-027 admission gate

Date: 2026-08-12

Branch: `research/parity-lift-000`

Research PR: `#365`

## One objective

Given public data

```text
E, G, Q=[k]G
```

compute one exact generator-relative bit, preferably

```text
par_G(Q)=k mod 2
```

or an exactly equivalent GLV/EDS bit, with total online time, preprocessing,
storage, advice size, and precision cost below the generic `sqrt(n)` baseline.

A coordinate change, a projective lift, or a large precomputed table is not an
algorithmic improvement by itself.

## The verified research spine

### A. Exact parity is enough

An exact parity oracle on arbitrary public points recovers the complete scalar
by repeated public halving:

```text
b_i = par_G(Q_i)
Q_(i+1) = [2^(-1) mod n] (Q_i-[b_i]G)
```

At most `ceil(log_2 n)` oracle calls recover `k`.

### B. Periodic EDS normalization localizes the missing bit

Let

```text
rho_G(Q)=chi(psi_k(G)).
```

For the secp256k1 normalization currently used in this branch,

```text
(-1)^k = chi(phi_raw(Q)) * rho_G(Q).
```

The first factor is publicly computable from `Q`. The second factor is the
hidden absolute EDS-residue bit. Thus the periodic representation did not solve
parity; it isolated the exact missing bit.

The source display has a recorded raw-versus-normalized exponent discrepancy,
so this bridge remains subject to the existing independent normalization audit.

### C. GLV turns the hidden bit into a carry bottleneck

For the three-point GLV orbit define

```text
R3(Q)=rho_G(Q) rho_G(phi Q) rho_G(phi^2 Q).
```

Let canonical scalar representatives satisfy

```text
k_0+k_1+k_2=gamma(Q)n,
gamma(Q) in {1,2},
g(Q)=(-1)^gamma(Q).
```

The public point-function orbit product obeys

```text
C3(Q)=g(Q)R3(Q).
```

Therefore an exact public decoder for either `g` or hard-branch `R3` gives the
other one.

### D. Carry or R3 completes the attack chain

The carry function has an explicit triangular description and a constant-heavy
additive Fourier spectrum. With exact chosen-multiple oracle access

```text
t -> g([t]Q),
```

the hidden scalar multiplicatively shifts the known heavy frequencies. Subject
to the still-required literal audit of the cited local sparse-Fourier theorem,
this gives

```text
exact R3 decoder
  -> exact carry decoder
  -> full scalar k.
```

Thus `g` and hard-branch `R3` are exact bottlenecks, not merely heuristic
features.

### E. A global periodic/theta phase exists, but is not public from Q

On the cyclotomic cover,

```text
M_G(Q)=product_i (1-zeta_n^(k_i))
```

has

```text
g(Q)=sign(Im M_G(Q)).
```

The missing operation is the public evaluation of the dual character

```text
[k]G -> zeta_n^k.
```

Standard pairing, fixed theta-space, trace/norm, and direct p-adic routes were
scoped out because they are trivial, lose the sign, or require an object whose
degree or dimension is far above the square-root scale for secp256k1.

### F. The half-kernel is an exact specification, not yet an algorithm

The carry-positive C3 halves define

```text
H_G(Y)=product_(carry-positive C3 orbits) (Y-y_orbit),
```

with

```text
H_G(y(Q))=0 iff g(Q)=+1,
P_G(Y)=H_G(Y)H_G(-Y),
deg H_G=(n-1)/6.
```

This is an exact algebraic encoding of the desired bit. However, the current
construction chooses the roots using the already-known carry labels. It is
therefore a giant answer sheet written as a polynomial, not a public decoder.

A useful result begins only when `H_G(y(Q))`, its zero-membership, or the
oriented quotient

```text
R_G(Y)=H_G(Y)/H_G(-Y)
```

can be evaluated without materializing the degree-`(n-1)/6` factor or using
comparable advice.

## Drift audit

The original periodic/theta idea was not abandoned. It produced:

1. the exact parity-to-DLP target;
2. the EDS-residue localization;
3. the GLV carry and hard-R3 bottlenecks;
4. the exact cyclotomic phase;
5. several scoped no-go results for naive representations.

The later order-13441 lookup and ML packages were falsification probes for one
possible nonlinear decoder family. Their independent extension failed. That
route is closed and should not be retuned without a new exact identity.

The main risk now is circularity: defining a generator-oriented factor from the
answers and then treating its existence as progress. Package 027 is admissible
only as a compression-or-obstruction theorem package.

## Critical new gate: generator orientation

The full degree-`n` CM isogeny or Frobenius kernel describes the subgroup as a
set. The factor `H_G` is stronger: it chooses one point from every pair of
opposite C3 halves according to the canonical scalar representatives relative
to the chosen generator `G`.

Before searching for a compact formula, package 027 must answer:

```text
What public G-dependent datum distinguishes H_G from H_G(-Y),
and how does H_G transform when G is replaced by [u]G?
```

If the proposed CM/theta construction depends only on the subgroup kernel and
not on the generator orientation, it cannot select the required half. In that
case the route must stop rather than continue with more screens.

## Revised package 027

Name:

```text
GENERATOR-ORIENTED-HALF-KERNEL-027
```

### Stage 0: covariance and non-circularity

Derive the exact law for `H_[uG]` in terms of `H_G`. Identify the minimum public
G-dependent orientation data. Prove that no hidden carry labels, scalar table,
or `Omega(sqrt(n))` advice is embedded in preprocessing.

### Stage 1: compact CM description

Construct and independently verify the Eisenstein norm representation,
endomorphism/kernel relation, divisor, and every normalization factor for the
full kernel polynomial.

### Stage 2: oriented factor selection

Determine whether a cubic-theta, sigma, elliptic-unit, or net factor provides a
canonical public choice between `H_G(Y)` and `H_G(-Y)`.

### Stage 3: costed black-box evaluation

Produce an explicit straight-line program or recurrence for zero-membership or
`R_G(Y)` with total time, memory, preprocessing, and advice

```text
O(n^(1/2-epsilon))
```

for a fixed positive `epsilon`.

### Stage 4: binary decision

Either:

1. obtain an exact identity, operation count, cross-order scaling replay, and
   literal carry-to-DLP recovery reduction; or
2. prove a scoped obstruction showing that the tested CM/theta representation
   is generator-blind or requires square-root-scale-or-larger information.

No additional broad ML or character screens are admitted inside this package.

## Central question

```text
Does there exist a uniform public algorithm A(E,G,Q) that computes the
canonical generator-relative GLV carry g_G(Q), equivalently selects the
oriented half-kernel H_G rather than H_G(-Y), or computes hard-branch R3,
with total time, memory, preprocessing, advice, and precision cost
O(n^(1/2-epsilon)), without first recovering k?
```

## Decision

Proceed with package 027 only in the revised theorem-first form above.

The first deliverable is not another experiment. It is the generator-change
covariance theorem and the generator-blindness audit. A failure there closes
the CM half-kernel route. A success supplies a justified route to a public carry
oracle and therefore to the full discrete logarithm.