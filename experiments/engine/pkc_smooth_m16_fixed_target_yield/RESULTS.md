# HYP-M16-FIXED-TARGET-YIELD-001 result

Recorded: 2026-07-31

Decision model: classical representation-aware, synthetic toy data only.

Validator terminal:
`CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION`

Epistemic status:
`[REPRODUCED]` within the three frozen toy `E_7` subgroup rows and the
preregistered residual-sampling experiment. The result is not a secp256k1
attack, a faithful PKC factor-base experiment, a solver result, a scaling
law, or an asymptotic claim.

## Decision

The TASK-025 endpoint and `BalancedPropagatedRegular` conditions were
available in the frozen fixed-target toy relation sample. This clears only
the local availability question and opens one separately reviewed proposal
for `HYP-M16-SOLVER-SLOPE-001`.

The GLV-specific `H_NEW` explanation is **not retained**. The orbit-closed
and matched-plain arms had nearly identical regularity fractions, their
Wilson intervals overlapped at every size, and no size satisfied the
preregistered new-mechanism controls. The parent route remains parked and no
solver execution, route promotion, rerun, secp256k1 target, or complexity
claim is authorized.

## Frozen run

- authorization:
  `AUTH-HYP-M16-FIXED-TARGET-YIELD-001-20260730-01`;
- readiness source:
  `0b1b36851aa0f82c3a1bd587d385775923153d9c`;
- three synthetic `E_7` subgroups with `m = 19, 21, 23`;
- two matched arms, five seeds, thirty cells;
- primary trials: **3,000,000**;
- accepted exact relations: **911**;
- affine-regular accepted relations: **907**;
- resource cap reached: **no**;
- wall time: **244.78 seconds**;
- CPU time: **244.74 seconds**;
- peak RSS: **0.02395 GiB**;
- producer operation receipt: 80,178,323 curve additions,
  143,834 curve doublings, 80,317,759 field inversions, and
  3,407,960 identity shortcuts.

## Decisive measurements

| m | arm | trials | accepted | affine regular | theta | 95% Wilson interval |
|---:|---|---:|---:|---:|---:|---|
| 19 | GLV orbit closed | 50,000 | 146 | 144 | 0.986301 | [0.951433, 0.996235] |
| 19 | plain matched | 50,000 | 149 | 148 | 0.993289 | [0.962967, 0.998814] |
| 21 | GLV orbit closed | 200,000 | 158 | 157 | 0.993671 | [0.965024, 0.998882] |
| 21 | plain matched | 200,000 | 134 | 134 | 1.000000 | [0.972131, 1.000000] |
| 23 | GLV orbit closed | 1,250,000 | 174 | 174 | 1.000000 | [0.978400, 1.000000] |
| 23 | plain matched | 1,250,000 | 150 | 150 | 1.000000 | [0.975030, 1.000000] |

The pooled orbit-minus-plain theta differences were `-0.006987`,
`-0.006329`, and `0.000000` at `m = 19, 21, 23`. All pooled intervals
overlapped. The set of sizes qualifying for the preregistered `H_NEW`
signal was empty.

## Competing explanations

- `H_NEW`: **not retained**. No preregistered orbit-over-plain effect
  survived.
- `H_KNOWN`: **selected in this bounded scope**. TASK-025 supplies a useful
  local representation simplification, and both arms exhibit it.
- `H_ARTIFACT`: **not supported by the replay**. The independent validator
  reconstructed the curves, bases, paired targets, chronology, exact
  relations, obstruction labels, controls, hashes, and decision.
- `H_NULL`: **not rejected as a 256-bit scaling statement**. Three toy sizes
  cannot establish persistence at 256 bits; only collapse inside the frozen
  toy grid was ruled out.

## Independent validation

The independent standard-library validator imported no producer code and
reported `PASS` after **6,186,769** checks across eleven check families.

- raw transcript:
  `c37427bb2ad43ba573393f27656ad9611bb1c94b9d944238992cfc3f7bc21175`;
- run manifest:
  `1b1a056fb3566c1869ae0c10ffbe43200c32d030878900e6a5dd22281509c31c`;
- summary:
  `aea4309fd420244ddda6e506750c261ad40c0f53fa3bb361e7eab0d1045912d7`;
- validated artifact:
  `21a95ea4ea71c02d0199c331e549ca2e4ec2fbf7c1d8d70fe6651bea292d6413`.

The producer bundle was hash-identical before and after both independent
replays. The validator fault suite passed 40 tests after its pre-execution
fixture was isolated from the now-present canonical outcome bundle.

## What this changes

The fixed-target nonemptiness/usability blocker is reduced from unknown to a
bounded positive observation on the three frozen toy rows. The
GLV-specific advantage hypothesis is reduced to a bounded negative result.
The remaining cost barrier is still relation-family fidelity, independence
and rank, solver degree and memory growth, recovery, and end-to-end work as
`m` increases.

The only admissible next action is to formulate and preregister one
source-faithful solver-slope proposal. Executing that proposal requires a
new hypothesis review and a new dated authorization.
