# HYP-SGGM-MODEL-MAP-001 — structured generic-group boundary

Date: 2026-07-30

Type: `BARRIER`

Status: `SCREENED / NON-EXECUTABLE`

Novelty: `NOVELTY UNVERIFIED`. The published model is known; the
repository-specific operation map is a scoped derivation.

## Decision

[DERIVED] The naive identification of the current x-only M16 interface with
the Structured Generic-Group Model (SGGM) of Corrigan-Gibbs, Henzinger, and
Wu fails at its first two proposed assignments:

1. the candidate labeling
   `sigma(a) = pointX([a]G)` is not injective: the distinct points
   `G != -G` have the same `pointX`;
2. the local `S3`/projective-`H` relation is generically two-valued on Kummer
   coordinates, while the published model requires a partial single-valued
   binary operation `star`.

Accordingly, the specific claim “identify `Z/qZ` with the subgroup generated
by `G`, take `sigma(a) = pointX([a]G)`, take the
`S3`/projective-`H` output relation as `star`, and apply the published SGGM
lower bound” is `[REFUTED]`. Whether some other injective labels and partial
operation faithfully simulate every M16 primitive is `[UNKNOWN]`. This is
not evidence for the attack line; it identifies the simulation theorem that
is still missing.

The machine-readable operation audit is
`experiments/engine/sggm_model_boundary/SGGM_APPLICABILITY_MATRIX.json`.

## Primary-source boundary

[KNOWN] The paper defines:

- a finite structured label space `(L, star)`;
- an injective structured labeling `sigma : Z_n -> L`;
- a partial binary `star` that agrees with the group oracle wherever
  defined;
- associativity, commutativity, identity, and unique factorization;
- a lower bound of the form
  `Omega(min(sqrt(q), 1/delta))` in the prime-order case, under its precise
  distributional assumptions.

Primary source:
[Corrigan-Gibbs, Henzinger, and Wu, *The Structured Generic-Group
Model*](https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf), Definitions
2.2–2.4 and Theorem 3.2.

[KNOWN] Section 5.3 says that the authors have not yet attempted to model
special-case elliptic-curve DLP algorithms. The abstract's reference to
elliptic-curve points must therefore not be read as a theorem about this
fixed secp256k1 coordinate pipeline.

## Repository bridge

[REPRODUCED] The following checked results are relevant:

- `Ecdlp.Curve.secp256k1_pointX_neg`:
  `pointX(-P) = pointX(P)`;
- `Ecdlp.Curve.secp256k1_pointX_not_injective`, with the distinct witnesses
  `G` and `-G`;
- `Ecdlp.Curve.secp256k1_G_ne_zero`;
- `Ecdlp.Curve.secp256k1_no_nonzero_two_torsion`;
- the exact M16 exceptional-fiber and projective bridge artifacts, which
  retain the two possible Kummer outputs corresponding to `P + Q` and
  `P - Q`;
- `Ecdlp.Curve.secp256k1_glvPoint_eq_lam_on_zmultiples`, which records that
  GLV acts as known scalar multiplication on the target subgroup.

[DERIVED] Full signed point labels avoid the particular `pointX`
noninjectivity witness, but do not by themselves supply a partial
single-valued `star`, a unique-factorization structure, or a simulation
theorem. The existence of multiple ECDLP decompositions is not, by itself, a
proof that the SGGM unique-factorization axiom fails: such a claim would
first require a defined `star` and a proof that the proposed leaves are
`star`-primes.

[DERIVED] Group addition remains a charged group-oracle query in the SGGM.
Negation and known-scalar multiplication are derived from charged oracle
queries rather than being free primitives; only `star` and local
computation are free. Any alternative simulation that declares extra
coordinate operations local must explicitly recompute the constrained-label
density `delta`.

## Strongest case for

If the M16 primitives can be simulated by a finite `(L, star)` with a
nontrivial constrained-label density `delta(m_q)`, the SGGM theorem could
turn a vague generic-group objection into a precise barrier for an entire
class of relation algorithms.

## Strongest case against

The exact M16 interface is relational, multivalued at the proposed Kummer
output, and topology-sensitive. No faithful SGGM simulation has been given.
Conversely, these facts do not prove that every possible injective label
space or partial `star` fails.

## Decisive test and disposition

The bounded test is complete only for the naive operation map:

- `sigma(a) = pointX([a]G)` fails injectivity;
- `star =` the Kummer output relation encoded by `S3/H` fails
  single-valuedness;
- no alternative injective labels, partial `star`, algebraic axioms,
  concrete-label simulation, or nontrivial `delta(m_q)` proof have been
  supplied.

That specific subgroup-label map is therefore killed. Broader applicability of the
published theorem remains `[UNKNOWN]`, not refuted.

Reopen only with all of:

1. an explicit finite label space `L`;
2. an injective `sigma`;
3. a partial single-valued `star`;
4. proofs of the SGGM algebraic axioms;
5. a simulation theorem for every M16 primitive;
6. a nontrivial `delta(m_q)` bound for the relevant concrete encoding;
7. an explanation of how multiple relation decompositions are represented
   without assuming the desired discrete log.

## Claim boundary

This review does not prove that M16 escapes generic barriers, does not prove
that a suitable SGGM simulation or extension is impossible, and does not
establish a lower bound for concrete secp256k1. It closes only the naive
assignment `sigma(a) = pointX([a]G)`,
`star =` Kummer-output `S3/H`; applicability
under any other faithful operation map remains open.
