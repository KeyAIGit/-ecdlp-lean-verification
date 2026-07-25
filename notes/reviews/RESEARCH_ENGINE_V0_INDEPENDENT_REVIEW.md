# Independent scientific review — Research Engine v0

**Reviewed:** `agent/research-engine-v0` @ `805e61e` (Codex)
**Base:** `origin/main` @ `1a1b5dd` · **Comparison only:** `claude/research-engine-v0` @ `b1bc926`
**Reviewer:** independent; not the author of `agent/research-engine-v0`.

No merge performed. No ECDLP-progress claim. No secp256k1 experiment run. Every check below was
executed against the branch **as pushed**; where a diagnostic modified a file, it was reverted and
the finding re-confirmed on the pristine tree.

---

## 0. Headline

The conservative disposition is **correct and should be kept**: `0 selected / 0 ready`, promotion
disabled, `RE0-001/002/003` at intake. My independent audit **confirms 7 of 8** historical labels
and finds **one definitional mismatch** (§4, event 004). Task A resolves to a **precise obstruction,
not a construction** — and the obstruction is sharper than "not yet specified": the specific
`u = x³` quotient is *provably not faithful*, with a measured spurious-solution inflation of exactly
**3.000×** at `m = 2` (§2).

The architecture is sound. My main structural criticism of an earlier design — that a `supported`
label could inflate a route toward the attack — **does not apply here**, because the three axes are
genuinely separated (§1.4).

---

## 1. Findings, severity-ranked

### P1 — `check_research_engine.py` fails on the branch as pushed

```
$ git checkout 805e61e && python3 scripts/check_research_engine.py
research-engine check FAILED:
  - data/research_engine_state.json is stale
```

`data/research_engine_state.json` was not regenerated before the push. Regenerating with
`scripts/build_research_engine_state.py` produces a 1-line diff and the check then passes:

```
research-engine check OK: 9 hypotheses, 8 retained outcomes, selected sequence [], 0 ready,
promotion remains disabled.
```

Not scientific, but it is a red gate on the reviewed head, and a reviewer cannot distinguish
"stale artifact" from "the engine disagrees with its inputs" without running the generator. Fix
before merge.

### P2 — `supported` is applied outside its own stated precondition (event 004)

`repo/RESEARCH_ENGINE_V0.json`, `outcome_taxonomy`:

> `supported`: "A **preregistered** positive empirical prediction survived the tested scope and
> independent validation."

`experiments/engine/outcomes/REO-2026-07-24-004.json`:

- `"outcome": "supported"`
- `"provenance": {"source_kind": "historical_migration", ...}`
- `"summary": "... supporting the **preregistered** torsion identity only ..."`

But P2 has no preregistration. `experiments/p2_ward_eds/README.md` contains no predicted
observable, threshold, or prior — its single occurrence of "prior" (line 16) refers to a *prior
experiment*, not a prior belief. And `experiments/p2_ward_eds/RESULTS.md:6` states the experiment

> "**CONFIRMS the known `psi_n`-torsion equivalence numerically; it does not test any attack.**"

So the event asserts a preregistration that does not exist in the source, and applies a label whose
definition requires one. Two clean remedies:

1. add an explicit `historical_exemption: true` and widen the `supported` definition to cover
   retrospectively-labelled historical confirmations; **or**
2. drop the word "preregistered" from the summary and record the confirmation as scope-only.

I do **not** recommend relabelling to `bounded_negative` or `inconclusive` — see §4.

### P3 — `validation.independent: true` conflates three different independence claims

Every event carries a single boolean. The underlying validators support a much finer statement, and
collapsing it loses the distinction the promotion gate will eventually need. See §3.1 for the
decomposition. This is a schema/wording defect, not a false claim: the validators I inspected are
genuinely path-independent (§3.2).

### P3 — `research_engine_lib.py` is 3647 lines in one module

Independent audit cost scales with module size. No scientific consequence; flagged only because a
review of this kind is meant to be repeatable by someone else.

---

## 2. Task A — exact quotient, or the obstruction

**Verdict: precise obstruction. `RE0-002` is correctly classified as mechanism-development intake,
and the specific published direction (`u = x³`) is not merely unspecified — it is not faithful.**

`repo/RESEARCH_ENGINE_V0.json` already records `RE0-002` honestly
(`"mechanism": "Unresolved concept only."`, `gap_class: genuinely_open_question`). The following
strengthens that from "not yet written down" to "cannot be written down this way".

### 2.1 The symmetry is diagonal, not coordinatewise

For a j = 0 curve over `𝔽_p` with `3 | p−1`, fix `β` with `β³ = 1`, `β ≠ 1`. The GLV endomorphism
is `(x, y) ↦ (βx, y)`, acting on the group as `[λ]`. Verified numerically for `p = 1009`,
`b = 11`: `x ↦ βx` preserves the curve on all 966 affine points.

The Semaev relation set at index `m` is `{(P₁,…,P_m) : P₁ + … + P_m = O}`. Because

```
λ(P₁ + … + P_m) = λP₁ + … + λP_m ,
```

the relation set is preserved **only** by the *diagonal* action `x_i ↦ β x_i` applied to **all**
`i` simultaneously — a group of order **3**. It is *not* preserved coordinatewise: scaling a single
`x₁ ↦ βx₁` replaces `P₁` by `λP₁`, and `λP₁ + P₂ + … + P_m ≠ O` in general.

### 2.2 `u_i = x_i³` quotients by the wrong group

Substituting `u_i = x_i³` is exactly the ring of invariants of `(ℤ/3)^m` acting coordinatewise —
order `3^m`. The actual symmetry has order `3`. The substitution therefore **over-quotients by a
factor `3^{m−1}`**, identifying tuples that are not in the same orbit and admitting solutions that
are not relations.

**Minimal counterexample, `m = 2`, measured.** `P₁ + P₂ = O ⟺ x₂ = x₁`. In `u`-coordinates the
condition becomes `u₁ = u₂ ⟺ x₂ ∈ {x₁, βx₁, β²x₁}`. Over `p = 1009`, `y² = x³ + 11`:

| set | count |
|---|---|
| genuine relations (`x₂ = x₁`) | 483 |
| `u`-level solutions (`u₁ = u₂`) | 1449 |
| **inflation** | **3.000×** |

matching the predicted `3^{m−1} = 3`. Two thirds of the `u`-system's solutions are spurious. A
quotient that must then be re-saturated to remove them recovers no advantage; one that does not is
unsound.

### 2.3 The faithful quotient is larger, not smaller

Invariants of the *diagonal* `ℤ/3` on `𝔽_p[x₁,…,x_m]` are spanned by monomials of total degree
`≡ 0 (mod 3)`; minimally generated by the degree-3 monomials, `C(m+2, 3)` of them — for `m = 2`,
four generators (`x₁³, x₁²x₂, x₁x₂², x₂³`) versus two original variables — subject to a non-trivial
toric ideal. So the faithful quotient ring is **not polynomial**, and elimination happens in a ring
with **more** generators and **added** relations.

This is a mechanistic explanation of what P3 and P4 measured empirically:
`experiments/p4_petit/RESULTS.md` — any drop in the `d_reg` *number* is "accompanied by a
`3m`-variable ring, larger Macaulay matrices, and larger wall time".

### 2.4 The required scaling-vs-constant prediction, answered a priori

The handoff requires a prediction separating a scaling mechanism from a fixed orbit-size constant.
It can be answered without running anything: the exploitable symmetry group has order **3**,
independent of `|F|` and of `m`. Any faithful quotient by it removes at most a factor 3 from the
search space. **A fixed constant, not a scaling gain — by group order alone.**

A `u`-substitution *appears* to do better only by over-quotienting, i.e. by counting spurious
solutions as progress.

**Consequence.** `RE0-002` and `RE0-003` must remain intake. Any future packet claiming a
nonredundant invariant quotient must first exhibit a symmetry group whose order grows with `|F|` or
`m`; the GLV `ℤ/3` cannot supply one.

---

## 3. Task B — raw-artifact validator

### 3.1 Independence must be recorded as three separate claims

| level | question | mechanically checkable |
|---|---|---|
| **path independence** | does the validator share derivation code with the producer? | yes — import/callgraph analysis |
| **artifact independence** | does it recompute from raw inputs, or read the producer's claimed value? | yes — capability restriction |
| **source independence** | is the author/toolchain different from the producer's? | **no** — human obligation |

The current single `validation.independent: true` cannot express "path- and artifact-independent,
but same author". Recommended: replace with the three booleans plus a
`source_independence: human_attested | not_established` field. Source independence is the one that
**cannot** be removed mechanically and must stay a review obligation.

### 3.2 The existing validators are better than the handoff's framing implies

The warning "do not call a comparison of two fields in one producer-authored JSON independent
validation" applies to the demoted RE0-001 comparator — **not** to the experiment validators.
`experiments/p4_petit/validate.py` (module docstring, lines 3–21) states, and the code confirms,
that its relation-deriving core `brute_force_tuples` and `rebuild_base_independent` call **no**
function from the Gröbner/Macaulay path (`variety_from_system`, `degree_of_regularity`,
`search_relations_petit`); they use only `ec_add`, a local modular square root, and direct
evaluation from recorded parameters. It **recomputes** (`:129` compares a recomputed count against
the claim; `:140` replays each relation by actual `ec_add`) and cross-checks on **fresh** configs.

That is path- and artifact-independent. Only source independence is missing.

### 3.3 Minimum raw-artifact contract

A validator must receive **only**: the ideal/generator artifact (canonical sparse exponent-vector
form, sorted, `sha256`); the raw solver transcript (basis or certificate, not a summary); curve and
factor-base parameters; and provenance (tool, version, argv, seed, source commit, input hashes). It
must **never** receive the producer's claimed value, result digest, supported value, or outcome
label. Enforcement is by capability restriction — the pure validator gets a whitelisted evaluator
and no filesystem or network — so "did not read the claim" is structural, not promised.

Verifiable by a pure validator: hash agreement; ideal membership of each claimed relation via
cofactor certificate; EC replay of every relation by independent group arithmetic; factor-base
membership and on-curve checks; completeness against brute force at sizes where brute force is
feasible; determinism under a fixed seed.

**Not** verifiable and therefore human obligations: that the solver implements the algorithm it
names; that the toolchain is untampered; that the author of the validator is independent of the
producer; that the toy scale is representative.

### 3.4 Exhaustive terminal-outcome classifier

Applied to validated instance results and resource states, in this fixed precedence, so no
post-hoc choice is possible:

| # | condition (first match wins) | outcome |
|---|---|---|
| 1 | kernel/logical verifier accepted the formal statement | `proved` |
| 2 | scope, threat model, or required structure differs from the declared question | `inapplicable` |
| 3 | resource bound reached before the prediction could be evaluated | `resource_exhausted` |
| 4 | decisive measurement not independently validated | `inconclusive` |
| 5 | validated, prediction's threshold crossed in the predicted direction | `supported` |
| 6 | validated, threshold crossed against the prediction | `falsified` |
| 7 | validated, no advantage beyond the declared bound | `bounded_negative` |
| 8 | validated but competing explanations not separated | `inconclusive` |

Rule 2 must precede 3 and 4: an inapplicable run's resource state is irrelevant. Rule 4 must
precede 5–7: an unvalidated decisive measurement can never yield a directional label — this is the
rule that makes event 007 `inconclusive` mechanically rather than by judgement.

---

## 4. Task C — eight historical labels

Independently derived from each event's cited sources, then compared with the branch.

| event | source | my label | branch | agree |
|---|---|---|---|---|
| 001 | p0 — plain/GLV/u=x³ follow the same `B²/p` yield law | `bounded_negative` | `bounded_negative` | ✓ |
| 002 | p1 — S₃ solving reproduced the enumerated set, zero spurious | `bounded_negative` | `bounded_negative` | ✓ |
| 003 | p1-m3 — validation paths shared finite-field code | `inconclusive` | `inconclusive` | ✓ |
| 004 | p2 — confirms known `ψₙ`-torsion equivalence; tests no attack | `supported` **(scope-only; see below)** | `supported` | ✓ with correction |
| 005 | p3 — decisive proxy stopping criterion not validated | `inconclusive` | `inconclusive` | ✓ |
| 006 | p3 — no validated full m=3 solving degree within the ceiling | `resource_exhausted` | `resource_exhausted` | ✓ |
| 007 | p4 — decisive claim not validated; construction not faithful | `inconclusive` | `inconclusive` | ✓ |
| 008 | legacy 24-bit rows: cofactor-3 curve, ambient-group sampling | `inapplicable` | `inapplicable` | ✓ |

**Event 004 — why `supported` and not something else.** The measured identity (rank of apparition =
point order; zero set = order multiples) genuinely held and was independently replayed. It must not
become `bounded_negative`: `RESULTS.md:5-6` explicitly draws **no** advantage/no-advantage
conclusion, and recording a negative would manufacture attack evidence the source refuses to claim.
Nor `inconclusive`: the measurement was decisive *for the identity* and was validated. The correct
reading is the branch's own — `supported` **for the torsion identity only** — with the P2 finding
that computing `ρ(P)` is `Θ(ord P)`, the same order as the DLP, recorded as scope, not as a
negative result. The only defect is the unsupported word "preregistered" (§1, P2).

**Event 006 — a note.** `validation.status: not_available` with outcome `resource_exhausted` is
consistent: by classifier rule 3, the resource bound preempts the validation question. Correct.

---

## 5. Selectable or ready?

**None.** `0 selected / 0 ready` is the right state, and each blocker is independently confirmed:

- `RE0-001` — no independent raw-artifact validator; the former comparator is correctly demoted to
  a framework fixture.
- `RE0-002` — no exact mechanism, **and** §2 shows the published `u = x³` direction cannot become
  one; additionally no scaling gain is available from a group of order 3.
- `RE0-003` — depends on `RE0-002`; inherits the obstruction.
- Promotion and direct secp256k1 work: correctly closed.

The exploration tier remains empty **for the right reason** — not because the gate is too strict,
but because no candidate yet has both an exact mechanism and a raw-artifact validator.

---

## 6. Residual scientific risks (not mechanically removable)

1. **Source independence.** Every validator shares an author and a repository with its producer. No
   check inside the repository can establish otherwise.
2. **Toy-scale representativeness.** All measurements are at `|F| ≤ 20` bits. Nothing in the record
   licenses extrapolation, and the engine correctly refuses to; but the *absence* of a scaling law
   is not evidence of its absence at scale.
3. **Descriptive fits read as laws.** `d_reg = 2|F|+1` is a fit over `|F| ∈ 4..12`. It is used as a
   validator cross-check (`p4_petit/validate.py`, criterion 3). If it is a coincidence of small
   sizes, a correct future run could be rejected by it.
4. **Priors are subjective.** Information gain is computed, but from committed beliefs. Calibration
   cannot begin until genuinely preregistered runs resolve; the historical record is excluded by
   construction and correctly so.
5. **Absence of an entry is not an open window.** The map classifies a bounded corpus. A gap in the
   registry is not evidence of an unexplored research direction.

---

## 7. Comparison note (`claude/research-engine-v0` @ `b1bc926`)

Recorded for completeness; I am the author of that branch and it is not the subject of this review.

`agent/research-engine-v0` is the stronger base and should be the one carried forward. It contains
what the comparison branch lacks: queue separation (ECDLP vs product), the five-type gap taxonomy,
route evidence state across all 17 routes, an execution queue with dependency and validator states,
and a feedback contract.

Two points where the comparison branch's formulation is preferable, both cheap to port:

- **`supported` definition.** `agent/`'s is stricter and better — it explicitly denies proof,
  asymptotic, **route-promotion**, and secp256k1 semantics. Keep `agent/`'s. *(This reverses the
  comparison branch's wording, which said `supported` "earns the right to be evaluated at the
  promotion tier" — that upgrade semantics is wrong and should not be carried over.)*
- **Fault injection as a gate-development practice.** The comparison branch's gates were validated
  by deliberately corrupting them; that found a circular check that ordinary testing missed. The
  same discipline applied to `check_research_engine.py` would be worth the hour.

One convergent result worth recording: the two engines were written independently and both classify
exactly **6 of 17** routes as answering a non-primary threat-model question. Weak evidence, but
independent.
