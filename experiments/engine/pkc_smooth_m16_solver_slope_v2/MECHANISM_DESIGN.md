# TASK-029 M16 solver-slope mechanism design

Date: 2026-08-09

Status: `DESIGN ONLY / SCOPED ABSTENTION / NOT EXECUTABLE`

Threat model: classical, representation-aware, plain single target.

This note records what is exact after TASK-028 and where the proposed
solver-slope mechanism still dies at desk review. It is not a solver input, a
run configuration, an authorization, or an ECDLP result.

## 1. Exact published input

Use `k = 16`. For every factor-base leaf `i`, the TASK-028 specialization of
the published chain is

```text
x_i2 = x_i1^2
x_i3 = x_i2^3
x_i4 = x_i3^7
1 - x_i4^13441 = 0
```

Thus `L = L4 o L3 o L2 o L1 = 1 - x^564522`, and its roots in the prime field
form the unique subgroup of order `D = 564522`.

For a nonidentity affine relation point `R = (X,Y)`, direct source System (4)
contains:

- 64 factor coordinates, four for each of 16 leaves;
- 48 transition equations;
- 16 terminal equations;
- one target-specialized equation `S17(x_11,...,x_16,X) = 0`;
- 65 equation members in total.

The direct `S17` relation has degree 32768 in each leaf before target
specialization and the recorded total-degree upper bound after specialization
is 524288. These are exact representation facts, not solving-degree, fill-in,
memory, or runtime bounds.

A quadratic addition-chain circuit can preserve the pointwise predicate
`x^564522 = 1`, but TASK-028 does not establish equality of ideals,
multiplicities, solving degree, fill-in, or solving complexity between that
circuit and the literal source chain. No complexity claim may cross that gap.

## 2. Fixed-target semantics

Fix one safe synthetic cofactor-one toy curve `(p,E,q,G)` and one target
`Q = [z]G`. For each relation attempt `j`, sample and commit known scalars
`alpha_j, beta_j` before any solver randomness, then form

`R_j = [alpha_j]G + [beta_j]Q`.

If `R_j` is the identity, the displayed affine source system has no coordinate
`X`; the attempt must be separately classified and resampled or handled by a
future frozen identity branch. It cannot silently enter the affine stream.

The target `Q` remains fixed. Only the committed relation point `R_j` varies.
No public production target or secp256k1 target belongs to this design.

## 3. Sound acceptance and incomplete recovery

The printed source recovery step is ambiguous because it checks a zero-sum of
recovered factor-base points although System (4) contains the sampled target
coordinate. The repository completion is only the following sound filter:

1. verify every field and curve equation independently;
2. lift every finite leaf over the base field or reject it;
3. retain signs, multiplicities, identities, and backpointers;
4. accept only if independent curve arithmetic verifies
   `sum_i epsilon_i P_i + epsilon_R R_j = O`;
5. normalize the full relation so the target coefficient is `-1`;
6. aggregate duplicate factor-base columns and retain `alpha_j, beta_j`;
7. verify the normalized row
   `sum_i c_ij lambda_i - beta_j z = alpha_j (mod q)`;
8. replay rank, recover a candidate `z`, and require `[z]G = Q`.

Passing this filter proves soundness of one accepted relation. It does not prove
that every direct-System-(4) solution is recovered, nor does it price missed
components, multiplicities, or the recovery distribution. Relation equivalence
and recovery completeness therefore remain `specified_unproved`.

The formal recursive projective S3-tree work supplies exact semantics for its
own frozen presentation, including infinity branches and conditional affine
reduction. It does not prove that direct source System (4), a quadratic circuit,
and that recursive presentation have the same ideal or solver cost. The direct
source bridge must remain explicit.

## 4. Exact partial cost and the desk blocker

The primary source supplies only

`W_partial = P(p,16) + (16! * p / D^15) * T(E,16,L) + D^omega`.

It also gives the heuristic relation yield `D^16/(16!*p)` and, at the heuristic
balance `D^16 approximately 16!*p`, the necessary reference condition
`T(E,16,L) < p^(7/16)` for beating square-root work. The source explicitly
leaves the generalized-root complexity open.

TASK-027 fixes the exact secp256k1 public-parameter census: 283527 of the
564522 subgroup coordinates lift, none has zero right-hand side, and the exact
three-element coordinate orbits give 94509 liftable x-orbits. These facts do
not establish usable factor-log columns, independent relations, or a yield
law. The policy-limited at-most-24-bit ladder is inapplicable to M16 exponent
inference, not a falsification of the M16 idea.

No exact symbolic upper bound is known for any of the following terms:

- generalized-root solving degree, matrix fill, memory, and time for the
  direct 64-coordinate, 65-equation system;
- complete regular-locus and exceptional-complement orchestration;
- direct-System-(4) recovery completeness and recovery multiplicity;
- independent-relation probability and rank acquisition;
- sparse linear algebra and end-to-end candidate recovery;
- preprocessing, storage, and equal-success common-unit comparison.

Therefore no function `B(p)` is available that bounds complete single-target
work and satisfies `B(p) = o(p^(1/2))`. The conjectured sparse-elimination
advantage is not an exact cost bridge. The correct TASK-029 scientific output
is a scoped blocker and zero retention, with no request for compute.

## 5. Identity, novelty, and death condition

The mechanism identity is intentionally unchanged from
`HGP-M16-SOLVER-SLOPE-001`: the transformation, non-generic information source,
fixed-target semantics, recovery class, changed cost term, precomputation, and
single-target amortization are the same. TASK-028 corrects source fidelity and
evidence bindings but does not add a new cost-changing premise.

Accordingly this package is neither new to the repository nor new to the
reviewed corpus. It makes no global novelty claim. A duplicate-mechanism or
semantic-reencoding rejection is a valid death result.

The proposal stops permanently in this cycle if review confirms any of:

- the mechanism is a duplicate without a new causal premise;
- direct-system recovery equivalence remains unproved;
- the generalized-root term has no exact cost-changing bound;
- the only safe policy regime cannot identify an M16 scaling slope;
- no independent validator can recompute the complete ledger.

Any future successor must use a new dated decision and a genuinely new,
source-grounded cost-changing premise. Renaming this mechanism is not a
successor.

## 6. Prohibited actions

This design authorizes no solver, parameter sweep, exact-target computation,
discrete logarithm, route move, candidate compilation, or experiment. It also
does not authorize a larger toy regime, an implementation budget, or reuse of
any consumed experiment authorization.
