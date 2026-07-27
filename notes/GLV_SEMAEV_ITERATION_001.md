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
determinant of the quadratic Sylvester matrix, and replays all 108 actions plus
the complete action/character witness partitions.

Frozen certificate:

```text
experiments/glv_semaev_symmetry/certificate.json
SHA-256 2142e8d66a8422768b609e42f5ce09377d5f93609941139fc9fc4e5abe4dfe59

experiments/glv_semaev_symmetry/fixed_target_certificate.json
SHA-256 9db5e0375421659f9abb905c12ae77232ef9957867f7194baaf548d45a1f091d
```

Kernel package source acceptance:

```text
Ecdlp/Proved/GlvSemaevSymmetry.lean
Git-blob SHA-256 2940166077cbb1de3840d31fc2e829c96c90549bc49466250f8f548225d99e73
Lean 4.31.0
Mathlib v4.31.0 / fabf563a7c95a166b8d7b6efca11c8b4dc9d911f
accepted content head be7a4d8e7da94b33ef74b0c146d732314b293827
GitHub Actions run 30163027316
```

The cited run accepted the exact content-addressed module in the repository's
full `lake build`, built-source no-`sorry` scan, and generated exhaustive axiom
audit containing all 14 public declarations. The branch was later rebased
without changing this module blob. The symbolic stabilizer classification
remains certificate-backed rather than being overstated as a kernel theorem.

The coefficient witnesses also make an arbitrary scalar exhaustive. A
coefficient-one anchor forces any proportionality scalar to be a power of
`beta`. The generated certificate gives every rejected action/character pair an
x-monomial with coefficient `+1` over `Z[b]`; these
obstructions survive every field characteristic. A compact characteristic
outside `{2,3}` derivation can also use the `S3` component
`-4*b*(x1+x2+x3)` to force all three exponents to equal the character. For
`S4`, the component

```text
64*b^3*((x1+x2)-(x3+x4))*((x3-x4)^2-(x1-x2)^2)
```

forces character zero and all four exponents to be equal.

## Exact result

For the polynomial classification, assume a field containing a primitive cube
root `beta`. No characteristic or `b != 0` assumption is needed. In
characteristic 3 that premise is empty because the only cube root of unity in
a field is `1`. Interpreting the same formulas as a nonsingular short
Weierstrass elliptic curve additionally assumes `b != 0` and characteristic
outside `{2,3}`.

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

The positive identities need only `beta^3=1` in a commutative ring. A primitive
root in a field is needed for the exact stabilizer classification; the
short-Weierstrass assumptions are needed only for its elliptic interpretation.

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

**Note the two directions, which point opposite ways and must not be conflated.** The
*polynomial identity* above carries the exponent `beta^(-t)` on the target. The *induced map on
solution fibers* is `x -> beta^t*x`, and it sends a solution at target `r` to a solution at
target `beta^t*r` — that is, it transports the problem for `R` to the problem for `phi(R)`, not
`phi^2(R)`. Reading the exponent of the identity as the direction of the fiber map is an error;
`S₄_glv_fibre_transport` in the Lean module therefore derives the fiber direction from full
diagonal invariance rather than from the transport identity.

**Strengthened scope (`fixed_target_certificate.json`).** The earlier wording said "generic
nonzero target". The exhaustive certificate is stronger: for **every** `r != 0`, and for **every**
characteristic outside `{2,3}`, the only fixed-target scalar covariance is the identity. Each of
the `78 = 26 x 3` pairs (nontrivial exponent tuple, surviving residue class) carries a *pure-`r`
witness* `N*r^k` with `k >= 1` and `|N|` in `{1,4}`; the only prime dividing any minimal `|N|` is
`2`, which is already excluded. So no additional exceptional characteristic exists, and no
genericity hypothesis on `r` is needed.

The slice `r=0` is preserved by the full diagonal `C3` (multiplier `1`) and is the **complete**
exceptional locus in characteristic outside `{2,3}`: all 81 action/character pairs are partitioned
into the three diagonal covariances and 78 rejections, each carrying a pure-`b` witness.
Characteristic 2 is a real excluded case: the zero slice can degenerate and acquire a larger
stabilizer. Characteristic 3 instead has no primitive cube root in a field. The certificate solves
the vanishing conditions for `r` rather than assuming `r=0` is the only solution. Whether that
locus is *inhabited* on a given curve is a separate
arithmetic question — it needs a rational point `(0,y)` with `y^2 = b` — and is **not** settled
here.

Scope caveat: `r` ranges over field elements, hence over **affine** targets only. A target at the
point at infinity has no `x`-coordinate and lies outside every statement in this note.

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
The orbit size is constant, so this result alone establishes no nonconstant
reduction. Ruling out every nonlinear batching or amortization mechanism would
require a separate formal full-cost theorem.

`S4(...,xR)=0` is an x-coordinate relation and does not encode one fixed sign:
`x(R)=x(-R)`. The point-group statement above is therefore recorded
separately from the polynomial statement.

## Research disposition

Outcome taxonomy:

| Item | Outcome | Scope |
|---|---|---|
| Diagonal `S3` and `S4` laws | `proved` | Exact symbolic certificate and kernel-accepted Lean package |
| Full coordinatewise semi-invariant classification | `certificate_replayed` | Symbolic primitive component and exact secp256k1 specialization; not kernel-checked |
| Independent `u_i=x_i^3` quotient | `bounded_negative` | It quotients by `C3^m`, not the diagonal `C3`, and loses relative phase |
| Fixed-target scaling premise | `bounded_negative` | For affine targets with `x(R) != 0` in characteristic outside `{2,3}`, nonidentity diagonal action transports the target instead of preserving it; the `x(R)=0` slice has exactly the diagonal `C3` |
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

## Invariant rings, named precisely

Two different rings are involved, and the naive quotient is the wrong one:

```text
K[x1^3, ..., xm^3]                 = R^((Z/3)^m)        order 3^m, COORDINATEWISE
R^(diagonal C3)                    = the third Veronese subring of K[x1..xm]
```

The diagonal invariant ring is spanned by the monomials of total degree `= 0 (mod 3)` and is
minimally generated by the `C(m+2,3)` monomials of degree exactly `3`, modulo a toric ideal
generated by quadratic binomials; it is **not** a polynomial ring for `m >= 2`. Since the diagonal
`C3` sits inside the coordinatewise `(Z/3)^m`, we get a strict containment

```text
K[x1^3, ..., xm^3]  (  R^(diagonal C3),
```

so `u_i = x_i^3` over-quotients: its fibers are full `(Z/3)^m`-orbits of size `3^m`, while diagonal
orbits have size `3`, and it therefore fails to separate diagonal orbits by a factor `3^(m-1)`.
The **mixed** degree-three invariants — `x_i*x_j^2` and `x1*x2*x3` — lie in the diagonal invariant
ring but not in `K[x_i^3]`, and they retain exactly the relative phase that `u_i = x_i^3` loses.

## Prior art and novelty

None of the mathematics in this iteration is a new attack idea, a new technique, or new invariant
theory. The following are the direct antecedents, and the diagonal-only observation together with
the fixed-target obstruction are **already in print**:

- **S. W. Gebregiyorgis**, *Algorithms for the Elliptic Curve Discrete Logarithm and the
  Approximate Common Divisor Problem*, PhD thesis, University of Auckland, 2016, **Ch. 4
  §§4.2–4.3**. For the characteristic-3 additive analogue `psi(x,y) = (x+1, y)` he builds
  `G = Z3 x S_m` with the order-3 automorphism acting *"to each variable simultaneously"* (the
  diagonal-only observation), states the fixed-target obstruction — *"the action of H on this
  relation is both on the sum R and the points of the factor base summing to R … we get another
  valid relation for a different element Q"* — computes the invariant ring, and reports the
  outcome as **negative**: *"an automorphism of an elliptic curve is worse in the actual
  polynomial system solving."* This is the closest prior work and it anticipates the qualitative
  conclusion of this iteration.
- **B. Sturmfels**, *Algorithms in Invariant Theory*, 2nd ed., **§2.1 Prop. 2.1.5, p. 28**. The
  diagonal scalar `Z/p` action is the textbook worked example; the invariant ring is identified as
  the Veronese subalgebra with the `C(m+p-1, m-1)` generator count. The invariant-ring section
  above is a restatement of this 1993 proposition.
- **I. Duursma, P. Gaudry, F. Morain**, *Speeding up the discrete log computation on curves with
  automorphisms*, ASIACRYPT 1999, LNCS 1716, 103–121, **§4.2**. The order-6 automorphism group of
  `E_{0,b}` with `[rho_n](x,y) = (rho_p x, y)` — the exact map used here — was fully worked out
  for Pollard rho, giving a `sqrt(6)` speedup, in 1999.
- **S. Tsakou, S. Ionica**, *Index calculus attacks on hyperelliptic Jacobians with efficient
  endomorphisms*, Mathematical Cryptology 1(2):102–114, 2021, **Example 4**. The literal
  `phi(x,y) = (beta x, y)`, `beta^3 = 1`, on a `j = 0` curve is already used in index calculus —
  over `F_{q^2}`, and only to build factor-base equivalence classes.
- **J.-C. Faugère, P. Gaudry, L. Huot, G. Renault**, *Using Symmetries in the Index Calculus for
  Elliptic Curves Discrete Logarithm*, J. Cryptology 27(4):595–635, 2014 (ePrint 2012/199),
  **Prop. 3**: the same stabilizer method (`g·f = h_g·f` with `h_g` a unit, then pin the
  character) for the `Z/2` sign action.
  **Applicability caveat:** their **Prop. 2** cost statement assumes `G` is a *pseudo-reflection
  group*. The diagonal scalar `C3` is **not** one for `m >= 2` — a scalar `zeta*I_m` has all `m`
  eigenvalues `!= 1`, whereas a pseudo-reflection has exactly one. Prop. 2 must therefore **not**
  be applied here, and no numerical cost ceiling derived from it appears in this note.
- **J.-C. Faugère, L. Huot, A. Joux, G. Renault, V. Vitse**, *Symmetrized Summation
  Polynomials: Using Small Order Torsion Points to Speed Up Elliptic Curve Index Calculus*,
  EUROCRYPT 2014, LNCS 8441:40–57, **§§1 and 3**, DOI
  `10.1007/978-3-642-55220-5_3`. This is the decisive comparison for the cost argument:
  translation by a rational order-`m` torsion point may be applied independently to the
  free coordinates subject to `sum k_i = 0 mod m`. For rational 2-torsion this gives an
  even-weight subgroup of order `2^(n-1)`, which grows with the number of relation
  variables. The GLV scalar action is different: it is sum-compatible only on the
  diagonal, whose order remains three. Fixed order of a curve symmetry alone therefore
  proves no constant-factor ceiling; the relation-preserving coordinatewise action is
  the relevant object. The direct rational-2-torsion mechanism is unavailable on
  secp256k1 over `F_p`: the kernel-checked theorem
  `Ecdlp.Curve.secp256k1_no_nonzero_two_torsion` proves `E(F_p)[2] = {O}`. This
  target-specific screen does not exclude auxiliary curves or extension fields.

**Defensible contribution.** Specialization of the classification to the multiplicative `j = 0`
case over a prime field, its exact certification (including the characteristic-uniform witness),
and its Lean formalization. **Not** the discovery of a new ECDLP attack, and not a new
mathematical technique.

**Source-access correction and remaining novelty gate.** No novelty claim is made while the
remaining source below lacks a claim-level comparison:

- **C. Petit, M. Kosters, A. Messeng**, *Algebraic Approaches for the Elliptic Curve Discrete
  Logarithm Problem over Prime Fields*, PKC 2016, LNCS 9615(II):3–18,
  [official IACR archival PDF](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf),
  DOI `10.1007/978-3-662-49387-8_1`. The earlier statement that this source was unavailable or
  only paywalled was false. A full-text term and construction review found no GLV,
  automorphism, endomorphism, invariant-coordinate, or fixed-target symmetry claim. Its relevant
  contribution is instead the faithful prime-field factor basis
  `F={(x,y):L(x)=0}` with `L` composed from low-degree rational maps, together with the complete
  Semaev relation system and an explicit statement that its asymptotic complexity remains open.
  It therefore does not overlap the bounded stabilizer result, but it is required provenance for
  any future `R-PETIT-COMPOSED-MAPS` proposal.
- **A. Amadori, F. Pintore, M. Sala**, *On the Discrete Logarithm Problem for
  Prime-Field Elliptic Curves*, Finite Fields and Their Applications 51:168–182, 2018,
  **§§2.2–3**, DOI `10.1016/j.ffa.2018.01.009` (IACR ePrint 2017/609). It independently
  describes the faithful Petit factor base `L(x)=0` over a prime field and proposes a
  separate one-Gröbner-basis variant. It is prior art for prime-field proposal design,
  not evidence that P4 implemented either construction.
- **M. Kudo, Y. Yokota, Y. Takahashi, M. Yasuda**, *Acceleration of Index Calculus for Solving
  ECDLP over Prime Fields and Its Limitation*, CANS 2018, LNCS 11124:377–393,
  DOI `10.1007/978-3-030-00434-7_19` — the Springer metadata and abstract are available, but no
  open primary manuscript was confirmed and the full paper was not inspected. Its abstract states
  *"We also make use of symmetries of summation polynomials … discuss a limitation of our
  acceleration"*, making it the **most likely overlap** with the fixed-target result.

Absence of a result from this repository is explicitly **not** evidence of novelty.

## Claim boundary

No discrete logarithm was recovered. No secp256k1 attack was executed. No
subgeneric or practical complexity result was established. No claim is made that a fixed-order
curve symmetry cannot change a Gröbner solving degree. The torsion-translation construction above
shows why that inference is unsound: one order-two point induces a relation-preserving
coordinatewise subgroup of order `2^(n-1)`. This iteration
improves the verified research memory by closing one precise false quotient
premise and preserving the remaining route boundary.
