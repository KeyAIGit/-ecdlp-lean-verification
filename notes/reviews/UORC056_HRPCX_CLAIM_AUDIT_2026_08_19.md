# UORC-056 H-RPCX claim audit — 2026-08-19

## Reason for audit

The V1-V5 campaign was re-read against the actual Lean sources, Python code, and GitHub Actions logs after the explanatory summary overstated the significance of the odd-cycle seam identity and repeated an uncompleted eight-gate search as a certified result.

## Central correction

No classical polynomial-time parity algorithm, no practically fast evaluator, and no nonconstructive proof of their existence has been obtained.

The equation

`(I+T)f=2*delta_O`

is a correct but elementary implicit characterization of canonical parity on an odd cycle. It is essentially the alternating-sign definition plus the unique wrap edge. It supplies no random-access algorithm at `Q=[k]G`; direct evaluation still requires the hidden generator distance or an equivalent global solve.

Accordingly, V4 is not positive evidence for H-PCX by itself.

## Audited claims

### V1 — valid, narrowly scoped

The paper proof that exact odd-cycle parity has full cyclic-shift span over characteristic not two is correct. Therefore a linear state with a position-independent linear translation update and linear exact readout needs dimension at least `n`.

Lean checks the algebraic ingredients: the seam identity, an abstract span lemma, and the alternating-geometric inverse identity. The repository does not currently package every prose-level specialization into one single end-to-end theorem statement, so the correct wording is `Lean-checked algebraic core`, not `the complete application is fully formalized`.

### V2 — valid paper proof, not Lean-formalized

For a nonconstant rational function taking only `+1` and `-1` on `N` rational points, `f^2-1` has at least `N` zeros and pole degree at most twice that of `f`; hence the pole degree of `f` is at least `N/2`.

This is a correct standard divisor argument under the stated smooth-projective-curve and characteristic-not-two assumptions. The current repository contains a replay and prose proof, not a Lean formalization of the function-field theorem.

### V3 — valid paper proof with field assumptions, not Lean-formalized

Over a splitting field of characteristic not dividing `2n`, canonical parity on an odd cycle has nonzero Fourier coefficient at every cyclic frequency. A polynomial decoder of degree `d` from a state supported on `r` frequencies can use at most `binomial(r+d,d)` resulting frequencies. Therefore exact parity requires `binomial(r+d,d)>=n`.

The argument is correct for the declared spectral model. The current repository contains finite replays and a prose proof, not a Lean formalization.

### V4 — correct but elementary and algorithmically empty by itself

The local equation uniquely defines parity. This is a short specification, not computational compression. It proves no upper bound on random-access evaluation, circuit size, memory, or runtime.

### V5 — previous claim invalid; corrected

The previous statement `exhaustive eight-gate SLP/circuit census` was false.

The GitHub Actions run aborted at cost 5 after exceeding the semantic cap, with per-level counts

`[8,82,959,13073,193404,2991347]`.

Levels 6 through 8 were never searched and no result artifact was produced.

Additionally, the enumerator charges repeated subexpressions repeatedly, so it enumerates formula trees, not straight-line programs or DAG circuits.

The corrected CI certificate is limited to formula trees with at most four internal arithmetic nodes in the tiny declared grammar on five toy curves.

## Current trustworthy conclusion

What is known:

- several narrow linear, low-pole, and low-spectral-complexity representation classes are ruled out;
- the odd-cycle parity word has an elementary short implicit equation;
- exact parity remains polynomial-time equivalent to ECDLP by bit peeling.

What is not known:

- whether a classical polynomial-time parity evaluator exists;
- whether a practically fast evaluator exists;
- whether parity has a short secp256k1-specific arithmetic circuit;
- whether the remaining CM, Miller, theta, p-adic, or modular-composition mechanisms yield such an evaluator.

## Reporting rule

Every future summary must distinguish four levels explicitly:

1. elementary identity;
2. scoped paper theorem;
3. machine replay on finite instances;
4. end-to-end Lean-formalized theorem.

No finite replay or partial search may be called exhaustive beyond the largest completed and certified level. No formula-tree enumerator may be called an SLP/circuit census unless shared intermediate values are represented and charged once.
