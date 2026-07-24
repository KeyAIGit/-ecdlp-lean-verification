# ECDLP decision layer (`engine/`)

A candidate-selection layer for ECDLP research: which work is *admissible*, which is
*worth doing next*, and what the record must retain when it resolves.

**What it is not.** It does not discover attack mechanisms, and calling it a
"discovery engine" would overstate it. It decides what to spend effort on and
refuses to let inadmissible work be counted as progress. The mechanism gap
identified in the substrate — no proposal-level non-generic mechanism exists — is
untouched by anything here.

Run it:

```
python3 -m engine.report          # ranked candidates + recommendation
python3 -m engine.retro           # retrospective validation, JSON
python3 scripts/check_engine.py   # the CI gate (retro + report + unit tests)
python3 -m engine.test_engine     # 36 unit tests
```

---

## The problem this exists to solve

`repo/ECDLP_DECISION_SUBSTRATE.json` records decision `RS-2026-07-22-001`:
seventeen routes evaluated, **zero** selected, `experiments_authorized: false`, and
`forbidden_work[0]` prohibits starting an experiment without a route-selection
decision. The gate is right to be strict — but as a *single* gate it deadlocks:

> A route may not be experimentally probed until it has a convincing mechanism and
> scaling argument. A convincing mechanism and scaling argument usually cannot be
> obtained without preliminary toy experiments.

So the layer splits the gate in two. **Exploration** deliberately does *not* require
a mechanism — requiring one there is precisely what causes the deadlock. It requires
only that the work be cheap, bounded, honest and falsifiable. **Promotion** keeps
the full strictness of the existing gate and adds nothing to the project's standards
for claiming a result.

| | exploration | promotion |
|---|---|---|
| threat model is the primary one | required | required |
| pre-registered prediction + threshold | required | required |
| likelihoods, prior, baseline, budget, stop condition, toy scale | required | required |
| exact non-generic mechanism | **not required** | required |
| full cost model (relation generation + recovery) | not required | required |
| measurements at ≥ 3 sizes | not required | required |
| no hidden precomputation / conditioned input | not required | required |
| independent reproduction | not required | required |

---

## Three design decisions that could have gone the other way

### 1. Gates are boolean; value is continuous; they are never multiplied

A score of the shape `relevance × plausibility × falsifiability × info_gain ×
reproducibility / cost` conflates *may we do this* with *how much is it worth*. Two
failure modes follow: a candidate can pass by being mediocre at everything, and one
zero silently annihilates an otherwise decisive proposal.

Here a gate failure makes a candidate **inadmissible**, and inadmissible candidates
are absent from the ranking rather than ranked low. Only survivors get a number.

This is not academic. `PRE-MULTITARGET-PRECOMP-PROBE` in
`engine/preregistrations.yaml` carries the **highest prior (0.20)** and the **lowest
cost (1)** of any candidate on file. Under a multiplicative score it would rank
first. It is shelved before scoring, because it changes the input model.

### 2. Information gain is computed, not asserted

`expected_information_gain` as a hand-set 0..1 dial is unfalsifiable and rewards
optimism. Instead a proposer must commit, **before** running, to `P(outcome | route
live)` and `P(outcome | route dead)` for every pre-registered outcome. Mutual
information between outcome and liveness then follows by arithmetic:

```
EIG = H(prior) − E_outcome[ H(posterior | outcome) ]
```

The priors are subjective and that is fine; what matters is that the commitment
precedes the data and is auditable afterwards (`brier_score`). An experiment whose
outcome is independent of liveness scores **exactly 0 bits**, however interesting or
cheap it looks — there is a test for this.

**A consequence to accept deliberately:** every honest prior here is small, and with
a small prior the gain is dominated by outcomes that would decisively *falsify*. The
layer therefore prefers cheap sharply-falsifying probes over expensive confirmatory
ones. That is not a parameter to tune away; it matches what this project's own
experiment history actually did.

### 3. Threat model is checked first, and mechanically

The dominant self-deception in ECDLP is threat-model drift: leakage, an interval
promise, many targets, or reusable precomputation quietly replaces the plain
single-target problem and the result reads as a break. This check runs before
everything else, and shelving is explicitly *not* a judgement on the work's quality
— it says the work answers a different question.

---

## Retrospective validation, as a hard CI gate

A selector nobody has checked against known outcomes is a number generator with a
schema. `engine/retro.py` replays the gates over the project's *existing* route
dispositions — reached by hand, independently, before this layer existed — and CI
fails if they disagree.

| check | what it asserts | gated |
|---|---|---|
| **R0** | every filed pre-registration is well-formed | yes |
| **R1a** | the layer's `PRIMARY_THREAT_MODEL` equals the substrate's own `primary: true` declaration | yes |
| **R1** | no route declaring a non-primary threat model escapes shelving, **and** no primary-threat-model route is shelved | yes |
| **R2** | the gates neither admit everything nor nothing, and agree with `select_none` | yes |
| **R3** | Brier calibration over resolved pre-registrations | **reported, not gated** |

R3 is deliberately not gated: with a handful of resolved items, gating would punish
honest uncertainty rather than overconfidence.

### Two findings from running it

**The substrate's `status` field is doing two orthogonal jobs.** The mechanical gate
shelves **6** of 17 routes as answering a different question; the status vocabulary
tags only **3** as `separate_threat_model`. The other three are labelled `guardrail`
(`R-GENERIC-LOWER-BOUND`) and `conditional_only` (`R-MULTI-TARGET-PRECOMPUTATION`,
`R-INTERVAL-AUXILIARY-INPUT`) — yet all three genuinely declare a non-primary threat
model, and the decision's own *rationale text* groups them with the shelved ones.
So `status` mixes **threat-model scope** (which question is being answered) with
**evidential status** (how good the evidence is). `ruled_out_for_target` is a third
thing again: primary model, examined, found inapplicable. Suggested follow-up — split
`status` into `threat_model_scope` (derivable) and `evidential_status`.

**The existing experimental record cannot calibrate anything.** All five historical
experiments (P0–P4) predate pre-registration, so any likelihood attached to them now
would be written after seeing the result — the exact failure this layer exists to
prevent. They are recorded with resolutions and reopening conditions but are
**excluded from the calibration score by construction**, and `check_calibration`
reports the exclusion count rather than hiding it. Calibration begins with the first
genuinely pre-registered run.

---

## Memory: resolutions and reopening

| resolution | meaning |
|---|---|
| `proved` | kernel-verified in Lean; the only state that may enter the ledger |
| `supported` | the prediction survived at the scale tested — **not** an attack, not a complexity claim; earns evaluation at the promotion tier |
| `falsified` | the pre-registered prediction was contradicted |
| `bounded_negative` | no effect within the stated bound; says nothing outside it |
| `inapplicable` | screened out before measurement; **not evidence** |
| `inconclusive` | ran, but the observable did not separate the hypotheses |
| `resource_exhausted` | stopped on budget; **not evidence** about the mechanism |

`falsified` and `bounded_negative` are **rejected by validation unless they carry
`reopening_conditions`**. A negative that cannot be reopened is not reusable
knowledge, and for this project negatives are the main product — so the record has
to say what would change the answer. The historical entries take their reopening
conditions from each experiment's own "What this does NOT establish" section rather
than from anything invented here.

`supported` exists because without it a positive toy outcome had nowhere to go,
which would have made every pre-registration a bet on failure by construction. That
gap was found by writing the first pre-registration, not by review.

---

## Decision delta

Every report ends in `authorize`, `close`, or `no_change`. `no_change` is a
legitimate answer; a *run* of them means the layer has become bookkeeping, so the
count is printed rather than left implicit.

Nothing here authorises anything. `phase_policy` in the substrate remains the sole
authority, and the report says so in its own output: the recommendation names the
blocking policy field and states that acting on it requires owner ratification of
the prior and likelihoods plus a dated policy edit.

---

## Fault injection

The gates were tested by deliberately breaking them. This found a real defect: the
first version of R1 passed whenever no labelled-separate route slipped through, so
corrupting `PRIMARY_THREAT_MODEL` shelved 15 of 17 routes and the gate still
reported OK — the check was **circular**, using the same constant to define both
what must be shelved and what shelving is wrong. R1a (the independent anchor against
the substrate's own `primary: true`) exists because of that, and both faults now
fail loudly. Any future change to the gates should be re-verified the same way.

---

## Scope, honestly

This layer improves *search discipline*. It does not reduce the computational
difficulty of ECDLP, does not supply the missing non-generic mechanism, and cannot
make a route live. Its measurable value is negative work avoided and self-deception
made harder — and if the ranked candidates all score a few hundredths of a bit, that
is the layer reporting accurately that there is currently very little to learn
cheaply, not a defect in the scoring.
