# PKC smooth-subgroup M16 semantic bridge

This directory records the non-experimental TASK-016 result for the affine
left-fold S3 presentation proposed as a low-input-degree surrogate for the
direct M16 relation.

The result is a scoped blocker.  The affine chain is exact only on the stratum
where every required prefix sum is a finite curve point.  It is not globally
equivalent to the intended signed-point relation semantics: the identity has
no affine x-coordinate, while a repeated-x S3 slice retains the tangent branch
and drops the opposite-sign cancellation branch.

Nothing here expands or evaluates S17, materializes the M16 polynomial system,
runs a solver, computes a discrete logarithm, authorizes an experiment, or
makes a cost or security claim.

## Frozen presentation

For factor coordinates `x_1,...,x_16`, fixed target coordinate `x_target`,
and fourteen affine prefix variables `u_2,...,u_15`, the left fold is

```text
S3(x_1, x_2, u_2) = 0
S3(u_2, x_3, u_3) = 0
...
S3(u_14, x_15, u_15) = 0
S3(u_15, x_16, x_target) = 0.
```

The membership layer remains the exact 24-gate-per-coordinate circuit from
the preceding M16 desk artifact and enforces `x_i^564522 = 1`.

For distinct lifted inputs, the repository's S3 iff theorem identifies the
two roots with the x-coordinates of the sum and difference.  For repeated
inputs on `y^2 = x^3 + 7`,

```text
S3(x,x,z) = -4*y^2 * (z - x(2P)).
```

On secp256k1, the no-two-torsion theorem makes `4*y^2` nonzero for every
affine point, so the repeated-x slice has the unique affine root `x(2P)`.
The other sign choice is `P + (-P) = O`; it has no affine x-coordinate and
therefore cannot be stored in an internal `u_k`.

The exact conditional bridge is:

- a signed relation with every fixed-order prefix of sizes 2 through 15
  nonidentity projects to the affine S3 chain;
- after exact base-field lift and local-root recovery, an affine-chain
  solution glues to a signed group relation;
- relations requiring an identity prefix need a separate projective or
  explicitly stratified presentation.

## Small no-two-torsion fixed-resultant boundary

Over `F_13` on `y^2 = x^3 + 7`, take

```text
P = (7,5),  Q = (8,5).
```

The signed points `P,-P,Q,-Q` sum to the identity.  The two repeated-coordinate
S3 slices are linear:

```text
S3(7,7,z) = 4z + 7,  root 8
S3(8,8,z) = 4z + 8,  root 11.
```

They have no common affine root.  Nevertheless, the fixed-size `(2,2)`
Sylvester determinant used by S4 is zero because both padded quadratic
leading coefficients vanish.  Thus the direct fixed-resultant boundary and
the affine common-root presentation differ exactly on the identity stratum.
This small witness deliberately excludes rational two-torsion.  It is not
used to claim an absolute minimal counterexample.

## Membership does not imply a base-field lift

There are two independently replayed extension-only witnesses.

The minimal one is over `F_5` on `y^2 = x^3 + 2`.  Since
`gcd(564522,4)=2`, the exact membership roots are `H={1,4}`.  Yet `x=1`
has right-hand side `3`, a nonsquare, while `x=4` lifts.  Moreover,

```text
S3(1,4,z) = 4z^2 + 2z + 1
```

has nonsquare discriminant `3` and no root in `F_5`, although its fixed
`(2,2)` self-resultant is zero.

The stronger witness uses the same control field, arity, `D`, and membership
layer as the M16 certificate.  In `F_564523`, where `H=F_p^*`,

```text
S3(1,-1,z) = 4z^2 - 28z + 1
```

has discriminant `768`, a nonsquare.  Thus the first affine-chain equation
has no base-field root.  The ordered M16 tuple

```text
1, -1, 1, -1, x(P), ..., x(P)
```

with twelve copies of `x(P)` and target `x([12]P)` satisfies every membership
equation.  Over the quadratic extension, the two repeated coordinate pairs
can be assigned opposite lifts and cancel, leaving `[12]P`.  Recovery must
still reject the tuple because `x=1` has no base-field curve lift.  This is a
base-field recursive-recovery semantics blocker, not a usable base-field
relation and not an S17 evaluation.

## Source-faithful M16 membership witness

The stronger witness keeps the registered `m=16`, `D=564522`, and source
factor chain:

```text
p = 564523 = D + 1
#E(F_p) = 564469 = 163 * 3463
H = F_p^*
```

The generator deterministically checks that `p`, `163`, and `3463` are prime,
counts the curve points, verifies that the curve has no rational two-torsion,
and constructs a point `P` of exact order `3463`.

Let

```text
A = [50]P
R = [14]P.
```

Use sixteen factor points with scalars

```text
50, 50, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
```

and signs

```text
+, -, +, +, +, +, +, +, +, +, +, +, +, +, +, +.
```

Their signed sum is `[14]P = R`, and every witness x-coordinate is nonzero and
satisfies `x^D = 1`.

The affine chain cannot recover this relation in the fixed order.  Its first
slice is `S3(x(A),x(A),u_2)`, whose unique affine root is `x([100]P)`.
After adding fourteen copies of `P`, the only reachable scalar classes modulo
global sign are

```text
86, 88, 90, ..., 112, 114.
```

The target class `14` is absent.  The validator independently checks all 105
layer-indexed parent occurrences and both roots of every quadratic transition;
these occurrences represent 27 unique parent scalar classes and 54
corresponding root evaluations.

This is not a counterexample over the secp256k1 target field.  It is an exact
structural counterexample at the same arity, source degree, factor chain, and
membership equation.  It proves that this fixed labeled-topology substitution
needs an explicit nonidentity localization or identity/projective strata.
A union over independently justified permutations or topologies is another
possible completion, but it changes multiplicity and recovery accounting and
must be established before solving cost can be priced.

## Recovery contract

A later relation row is acceptable only after all of the following:

- every leaf x-coordinate has an `F_p` lift;
- the `2^15` relative sign classes are resolved, directly or by the recorded
  `2^7` by `2^8` meet-in-the-middle split;
- duplicate signed points are combined;
- coordinate permutations are canonicalized and are not counted as
  independent relations;
- if `Q=eta*phi^j(P0)`, an occurrence `epsilon*Q` contributes coefficient
  `epsilon * eta * lambda^j mod n` only under the proved eigenvalue and
  full-group membership theorems;
- the complete curve relation and target coefficient are verified exactly.

A raw recursive polynomial solution is rejected unless every internal value
is the x-coordinate of the recovered finite prefix point and all local sign
choices glue to the final exact relation.

For the control witness, the certificate also performs a finite permutation
and multiplicity replay.  The multiset `{50P,50P,P,...,P}` has `120` unique
orders and `240` direct relative-sign preimages.  Exactly two preimages, both
in rank zero where the two `50P` leaves occur first, hit the identity at
prefix size two and are unavailable to the affine chain.  The other `238`
are affine-admissible.  All `240` normalize to the single row

```text
14P - R = O.
```

The repeated-point coefficient cancels to zero.  The artifact hashes the
accepted sign records, admissible subset, per-order counts, and normalized
row; the validator reconstructs them independently with a `2^7` by `2^8`
meet-in-the-middle replay.

The bottom-up recovery contract retains exact point states and backpointers,
routes identity states to a named non-affine stratum, accepts only root states
`R` or `-R`, and then normalizes the target coefficient to `-1`.  Ordered
tuples, coordinate multisets, and normalized sparse GLV rows remain distinct
objects.  GLV coefficient transport is bound directly to
`Ecdlp.Curve.secp256k1_glvPoint_eq_lam_on_zmultiples` and full-group
membership to `Ecdlp.Curve.secp256k1_mem_zmultiples`.  The full GLV orbit,
point-sign transport, and compressed-row replay remain a TASK-017
requirement; this artifact records their exact contract but does not claim to
have executed that replay.

The finite audit also does not instantiate the supplied-internal-coordinate
dynamic program or its backpointers.  That replay remains a TASK-017
requirement alongside the full GLV replay.

## Projective completion candidate

The certificate records, but does not promote to a proved global bridge, the
homogeneous Kummer coordinate

```text
kappa(O) = [1:0],  kappa((x,y)) = [x:1].
```

For a repeated finite input, the exact homogeneous slice is

```text
S3^h(x,x;U,V) = V * (-4*y^2*U + (x^4 - 56*x)*V).
```

Its roots are the identity branch `[1:0]` and the tangent branch
`[x(2P):1]`.  The validator independently checks the full homogeneous
polynomial on the affine chart, with one point at infinity, with two points
at infinity, and on repeated finite inputs.  A future projective construction
must exclude only invalid `[0:0]` coordinates.  Saturating by coordinate
differences would wrongly delete valid tangent and duplicate strata.

## Reproduce and validate

From the repository root:

```bash
python3 experiments/engine/pkc_smooth_m16_semantic_bridge/generate.py --check
python3 experiments/engine/pkc_smooth_m16_semantic_bridge/validate.py
(cd experiments/engine/pkc_smooth_m16_semantic_bridge && sha256sum -c artifact.sha256)
python3 -m py_compile \
  experiments/engine/pkc_smooth_m16_semantic_bridge/generate.py \
  experiments/engine/pkc_smooth_m16_semantic_bridge/validate.py
```

To intentionally regenerate after review:

```bash
python3 experiments/engine/pkc_smooth_m16_semantic_bridge/generate.py --write
```

The validator imports neither the producer nor its helpers.  It independently
recomputes field primality, the full control-curve point count, group
arithmetic, local S3 roots, reachable M16 states, the S4 Sylvester determinant,
extension-only fibers, permutation recovery counts, projective
specializations, source-artifact digest, canonical JSON, and terminal
boundary.
