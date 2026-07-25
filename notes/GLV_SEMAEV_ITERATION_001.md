# GLV-Semaev bounded structural iteration 001

Date: 2026-07-24

Iteration: `GLV-SEMAEV-ITER-001`

Route: `R-GLV-SEMAEV`

Hypothesis record: `HYP_GLV_SEMAEV_001`

Decision: `RS-2026-07-24-001`

## Decision scope

This iteration answers one structural question about the coordinatewise
order-three action on the third and fourth Semaev polynomials for

```text
E_b: y^2 = x^3 + b.
```

It is not an attack experiment. It does not target a secp256k1 discrete-log
instance, run a Groebner solver, estimate an attack exponent, or authorize
route promotion. Promotion and exact-target work remain disabled.

## Question

For `e in (Z/3Z)^k`, classify the tuples for which a nonzero scalar `c_e`
satisfies

```text
S_k(beta^e1*x1, ..., beta^ek*xk) = c_e * S_k(x1, ..., xk).
```

The classification must not assume that the stabilizer is diagonal. It must
also distinguish simultaneous target transport from symmetry of one fixed
target.

## Method and provenance

The producer in `experiments/glv_semaev_symmetry/generate.py` uses pinned
SymPy 1.14.0 to:

1. Expand the repository's exact `S3` formula with `b` symbolic.
2. Construct `S4` from its defining resultant, rather than a copied formula.
3. Enumerate all 27 coordinatewise actions for `S3` and all 81 for `S4`.
4. Compare every transformed polynomial with all three possible characters.
5. Repeat the comparison in both `beta^3-1` and the primitive component
   `beta^2+beta+1`.
6. Specialize the same tables exactly to secp256k1's field, `b=7`, and GLV
   factor `beta`.

The independent validator imports neither SymPy nor the producer. It rebuilds
`S3` using sparse integer polynomial arithmetic, constructs `S4` as the
determinant of the quadratic Sylvester matrix, and replays all 108 actions.

Frozen certificate:

```text
experiments/glv_semaev_symmetry/certificate.json
SHA-256 cec55fc266d729b4cf02dfcb3c98433f056f68c487b14931343c8ac6cad99d31
```

The coefficient witnesses also make an arbitrary scalar exhaustive. A
coefficient-one anchor forces any proportionality scalar to be a power of
`beta`. For `S3`, the component `-4*b*(x1+x2+x3)` forces all three exponents
to equal the character. For `S4`, the component

```text
64*b^3*((x1+x2)-(x3+x4))*((x3-x4)^2-(x1-x2)^2)
```

forces character zero and all four exponents to be equal.

## Exact result

Assume a primitive cube root `beta`, nonzero `b`, and characteristic different
from 2 and 3 for the exact elliptic stabilizer interpretation.

```text
H3 = { ((t,t,t), beta^t) : t in Z/3Z }
H4 = { ((t,t,t,t), 1)    : t in Z/3Z }.
```

Equivalently:

```text
S3(beta^t*x1, beta^t*x2, beta^t*x3)
  = beta^t * S3(x1,x2,x3)

S4(beta^t*x1, beta^t*x2, beta^t*x3, beta^t*x4)
  = S4(x1,x2,x3,x4).
```

No other coordinatewise `C3` scaling is a scalar polynomial covariance in the
symbolic primitive component or in the exact secp256k1 specialization.

The positive identities need only `beta^3=1` in a commutative ring. The
stronger assumptions above are needed for the exact primitive classification
and the nonsingular elliptic-curve interpretation.

## Fixed target

Let

```text
F_r(x1,x2,x3) = S4(x1,x2,x3,r).
```

The exact transport law is

```text
F_r(beta^t*x1, beta^t*x2, beta^t*x3)
  = F_(beta^(-t)*r)(x1,x2,x3).
```

Thus diagonal scaling maps the fiber for `r` to the fiber for `beta^t*r`.
For a generic nonzero fixed target, only the identity is a fixed-target scalar
covariance. The special slice `r=0` is preserved by the full diagonal `C3`;
other exceptional geometric fibers are not classified here.

The certificate includes the exact witness over `F_13`, with `b=2` and
`beta=3`:

```text
S4(1,2,3,5) = 0
S4(3,6,9,5) = 7
S4(3,6,9,2) = 0.
```

Scaling the relation inputs while retaining the target breaks this relation;
scaling the target as well transports it exactly.

## Point-group consequence

Because the GLV map `phi` is an additive bijection,

```text
P1 + ... + Pm = R
iff
phi(P1) + ... + phi(Pm) = phi(R).
```

This is a bijection between relation sets. Processing `R`, `phi(R)`, and
`phi^2(R)` supplies at most three linked target fibers. On a GLV-closed factor
base their rows can be orbit permutations rather than independent information.
The orbit size is constant, so this fact alone cannot change an asymptotic
relation-generation exponent.

`S4(...,xR)=0` is an x-coordinate relation and does not encode one fixed sign:
`x(R)=x(-R)`. The point-group statement above is therefore recorded
separately from the polynomial statement.

## Research disposition

Outcome taxonomy:

| Item | Outcome | Scope |
|---|---|---|
| Diagonal `S3` and `S4` laws | `proved` | Exact symbolic certificate; Lean package pending kernel acceptance |
| Full coordinatewise semi-invariant classification | `proved` | Symbolic primitive component and exact secp256k1 specialization |
| Independent `u_i=x_i^3` quotient | `bounded_negative` | It quotients by `C3^m`, not the diagonal `C3`, and loses relative phase |
| Fixed-target scaling premise | `bounded_negative` | Nonidentity diagonal action transports a generic target instead of preserving it |
| Whole GLV-Semaev route | `open_parked` | No general Groebner lower bound or faithful Petit no-go was proved |

This result does not imply that all geometric zero-variety automorphisms are
classified. Failure of scalar polynomial covariance is weaker than inequality
of geometric zero sets; a radical or absolute-irreducibility bridge would be
required for that stronger statement.

## Next decision

The result selects no F4, Sage, msolve, scaling, or secp256k1 run.

| Observed result | Current action | Reopening requirement |
|---|---|---|
| Only diagonal `C3` survives | Close the naive coordinatewise-cube and fixed-target scaling premises as bounded negatives | A materially different phase-preserving quotient or birational mechanism |
| Target orbit has size at most three | Treat target batching as a constant factor | A formal full-cost theorem showing a nonconstant gain |
| No replacement mechanism is present | Keep `R-GLV-SEMAEV` parked after this structural iteration | Exact quotient, recovery map, orbit tags, excluded components, falsifiable prediction, and independent validator |

The next permitted work on this route is proposal intake satisfying the final
row. Until such a proposal exists, another solver run would repeat a closed
premise rather than reduce uncertainty.

## Claim boundary

No discrete logarithm was recovered. No secp256k1 attack was executed. No
subgeneric or practical complexity result was established. This iteration
improves the verified research memory by closing one precise false quotient
premise and preserving the remaining route boundary.
