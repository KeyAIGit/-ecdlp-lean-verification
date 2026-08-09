# Adversarial re-verification of the Weierstrass acceptance findings

Date: 2026-08-09

Reviewed object: the findings recorded in
`notes/reviews/WEIERSTRASS_ACCEPTANCE_2026_08_08.md` — thirteen from the
pin-fidelity lens and two from the mathematical-truth lens.

Status: **research note.** It changes no statement, closes no barrier, and
authorizes nothing. It is the answer to a question that record asked of itself.

## Why this exists

The acceptance record carries a section headed *"Verification standing of the
findings below — read before acting on any of them"*, which says in its own
words that each finding is *"the work of one lens"*, that *"no adversarial
verifier was run against any individual finding"*, and that a finding is
therefore *"a claim with a locator, not a verified fact"*. It then instructs:
*"Read the thirteen before drafting. A drafter who trusts the `W12` skeleton's
`Finset` product paragraph, or the `analyticOrderAt` quote in `§0`, will lose a
CI round to each."*

Six independent verifiers were run against the pin
(`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, v4.31.0), each instructed to
**refute** rather than confirm, and each required to re-open every locator and
quote what it actually read. No Lean toolchain exists in this environment, so
every judgement below is a source-text judgement; where a claim is about tactic
behaviour, the verifier read the tactic's implementation rather than running it,
and says so.

## The decision, stated first

**The ACCEPT verdict stands, and no public signature is affected.** Nothing
found here is blocking, and no verifier proposed a change to any of the 28
signatures.

**Three of the thirteen findings are mechanically wrong in a way that matters,
and their wrong reasoning has already been copied into the contract.** Findings
6, 7 and 8 each predicted a specific elaboration or tactic failure. In all three
the *directive* survives — the contract's repaired skeleton is the right
skeleton — but the *stated reason* is false, and in one case the truth is
strictly more dangerous than the prediction.

That is the shape of the whole result: the findings were reliable about **what
to do** and unreliable about **why**. A reader who takes them as explanations
will mis-predict the next failure; a reader who takes them as instructions will
be fine.

## Verdicts

| # | Lens finding | Verdict |
|---|---|---|
| 1 | `AnalyticAt.finsetProd` absent; use `Finset.analyticAt_prod` :1081 / `_fun_prod` :1073 | CONFIRMED |
| 2 | Pin ships both Pi and `_fun_` forms; add a 29th signature | CONFIRMED |
| 3 | `tprod_mul_tprod_compl` also under `[ContinuousMul α]` | CONFIRMED |
| 4 | `exp_zero` :95 / `exp_add` :109 in the `Complex` block :90–:198 | CONFIRMED |
| 5 | The "weierstrass" collision scan is false as literally written | PARTIAL — a count is wrong |
| 6 | W8 `gcongr` hits a `/`-vs-`*` node mismatch | PARTIAL — symptom refuted |
| 7 | W6 `gcongr` cannot span the chain | PARTIAL — **reason inverted** |
| 8 | W5 `▸` may unify instead of rewriting | PARTIAL — **mechanism refuted** |
| 9 | Cite `ncard_eq_toFinset_card` :644, not the primed :649 | CONFIRMED locators, rationale refuted |
| 10 | `sineTerm_bound_aux` is `private` | CONFIRMED — and a worse sibling was missed |
| 11 | The denominator elaborates as `↑k + 1`, not `↑(k+1)` | CONFIRMED |
| 12 | Two stale locators | (i) CONFIRMED, stale; (ii) **REFUTED** |
| 13 | DedekindEta range is :88–:93 | CONFIRMED |
| M2 | `hane + hsum` force `ι` countable | CONFIRMED; conclusion overstated |
| M5 | `hane` essential in W7/W11/capstone, redundant in W8–W10 | CONFIRMED with three corrections |

## The three refuted mechanisms

### Finding 7 is inverted, and the truth is a silent wrong answer

The finding says a single `gcongr` cannot relate `2 * ‖L‖` to
`4 / (p+1) * ‖z‖^(p+1)` because *"those two expressions have different `*` / `/`
node structure"*. They do not. Both are `HMul.hMul` at arity 6; the `/` sits
inside an argument, where `gcongr`'s shape gate never looks. The gate is
`lhsHead == rhsHead` on `Name`s, `Mathlib/Tactic/GCongr/Core.lean:712`, reading
heads through `constName?` (:224–:233) off sides that are explicitly not
whnf'd for `≤` (:704–:705).

So `gcongr` matches. After the higher-priority lemmas fail instance synthesis
for ℝ, it applies `mul_le_mul`
(`Mathlib/Algebra/Order/GroupWithZero/Defs.lean:352-353`), discharges both side
conditions by `positivity`, and emits two main goals — one of which is

    2 ≤ 4 / (↑p + 1)

which is **false for every `p ≥ 2`**. The tactic reports progress. A prover
chasing that goal has no signal that the decomposition was wrong.

The finding's directive (split the chain into a `calc`, apply `gcongr` only to
the middle step) is right, and its supporting claim that `gcongr` is a
single-relational-step tactic is right — its only transitivity move,
`rel_imp_rel` (:541–:558), is gated to implication goals at :720–:721. But the
contract now carries the false mechanism, and the applied `calc` fix has a
second defect the finding did not create and did not catch: its middle line
needs `‖L‖ ≤ ‖z‖^(p+1) * 2 / (p+1)` verbatim in context, while the skeleton's
steps 1 and 2 supply a different expression whose combination is exactly the
transitivity `gcongr` cannot perform. **As applied, that fix still leaves an
unsolved goal.**

### Finding 6's symptom is refuted; its instruction is not

The claim that `gcongr` will not relate a `/` node to a `*` node is correct, and
stronger than the finding argues: the `@[gcongr]` attribute *rejects at
declaration time* any lemma whose conclusion has differing heads (:266–:267), so
no bridging lemma exists or can ever be added. The normalization the finding
demands is therefore mandatory.

But "the bare `gcongr` fails" is wrong. The outer node matches, the tactic
descends, and the mismatch one level down produces `pushNewGoal; return false`
(:707–:713), whose result the parent *discards* (:732) before returning success
(:733). The observed CI symptom is **"unsolved goals"**, not a `gcongr`
diagnostic. And one of the two proposed normalizations, `rw [← div_pow]`, does
not work: it converts an HDiv/HMul mismatch into an HPow/HMul mismatch.

### Finding 8's `▸` misfire does not exist

The finding predicts that `▸`, fed into an implicit binder, *"may simply unify
`?z := 1 + -z` and leave the type unrewritten"*. No such path exists in the
elaborator. `elabSubst` begins with `tryPostponeIfHasMVars?`
(`Lean/Elab/BuiltinNotation.lean:457-458`), which returns `none` whenever the
expected type contains a metavariable
(`Lean/Elab/Term/TermElabM.lean:1366-1373`). That forces the `none` branch
(:524–:537), which ignores the expected type entirely and rewrites the
*hypothesis* type forward — yielding exactly the desired
`1 - z ∈ Complex.slitPlane`. The alternative branch would throw a loud error,
not produce a wrong type. Either way the predicted silent failure is not a
behaviour this elaborator has.

The pin's own proof at `LogBounds.lean:233-235` corroborates it: the inner
`(norm_neg z).symm ▸ hz` that the finding calls "precedented" faces the same
metavariable-containing expected type as the outer one it calls risky. By the
elaborator's branching they are the same case.

The contract's `▸`-free repair is still the better text — it mirrors the pin's
own ordering — but the S1W-LOG obligation's MEDIUM severity rests partly on a
mechanism that does not exist.

## Defects no lens caught

These are new, and two of them are the same failure class the lenses were
hunting.

**`ℂ_ℤ` cannot be written outside the file that defines it.** It is
`local notation` — `Cotangent.lean:34` and `Complex/IntegerCompl.lean:27` — over
`Complex.integerComplement` (IntegerCompl.lean:23). `open scoped Complex` does
not bring it in. The contract reproduces `ℂ_ℤ` as usable notation at five sites,
including inside two of the seven anchors finding 10 certified as clean. This is
precisely the `private`-marker hazard finding 10 exists to catch, in text that
finding blessed.

**A wrong number is live in the contract.** Finding 5 states `WeierstrassCurve`
occurs 353 times across `AlgebraicGeometry/EllipticCurve`. Six counting methods
give 371 occurrences, 349 matching lines, 19 files — never 353. The figure 353
is the whole-Mathlib *line* count; both the unit and the directory are wrong.
The finding's own recommended fix text carried the bad number into the contract
at line 161.

**A Weierstrass-named analysis file was missed by the collision scan.**
`Mathlib/Analysis/SpecialFunctions/Elliptic/Weierstrass.lean` exists at the pin
and references `analyticOrderAt` at :1021 — closer to this contract's territory
than `WeierstrassCurve` or `StoneWeierstrass`. The narrowed
`weierstrassFactor`-only claim still holds, and all nine declared names were
independently re-run at zero hits.

**Both W8 normalizations bottom out at an unstated hypothesis.** Either route
leaves `gcongr` descending to `‖x‖ ≤ R`, which its terminal discharger can only
close from the local context. The skeleton derives `K ⊆ closedBall 0 R` and
never converts it. Unstated, and it is the step the whole normalization exists
to reach.

**`‖a i‖⁻¹ ^ (p+1)` is anti-simp-normal.** `inv_pow` is `@[simp]` in the
opposite direction (`Algebra/Group/Basic.lean:414`), so the majorant, `hsum`,
and one of the two proposed fixes all sit against the global simp normal form.
Only `simp only` is safe near them.

**The record contradicts itself on finding 12(ii).** The off-by-one it alleges
in `UPSTREAM_POOL.md` is backwards — :300 is the table separator and :301 *is*
the row carrying the claim, so applying the proposed fix would have introduced
an error where none existed. The record's own disposition section already says
so, and the contract records the withdrawal; the lens body was never updated.
Separately, the pool's substantive claim at that row is itself false at the pin
(`logTaylor` **is** `noncomputable def`, split across :67–:68), and finding 12
litigates only the line number.

## Corrections to the two mathematical findings

**Countability (M2) is sharper than stated.** For any *uncountable* `ι` the pair
`hane ∧ hsum` is outright contradictory, so all twelve signatures carrying both
are **vacuously true** there. That is more useful than "ι is countable on
non-vacuous instances", and it is actionable: a prover could discharge W7–W12
over an uncountable index by deriving `False`. Countability also follows from
the package's own W7, two lines after it, without the external lemma the finding
cites. The finding's rhetorical conclusion — that "cannot even express an
enumeration" overreaches — is only partly supported: it never engages the
sentence's "of zeta zeros" qualifier, and it slides between deriving a `Prop`
and expressing an enumeration.

**The `hane` map (M5) needs three witnesses, not one.** `hane` is essential in
W7 only against an *infinite* zero fiber; in W11 against a *single* zero; in the
W12 capstone only against a *finite nonempty* fiber — because
`Nat.card_eq_zero_of_infinite` makes an infinite fiber's count `0`, which
coincides with the true order and satisfies the statement. The finding's single
bundled witness does not break W7. Two further corrections: "W8, W9 and W10 (all
three signatures)" is really **seven** signatures, and "provably redundant" is a
claim about statement truth only — the contract's own W8 route runs through W7,
which the same finding declares false without `hane`, so deleting the hypothesis
breaks the supplied proof even where it preserves the theorem. That strengthens
death condition 6 rather than weakening it.

## What this means for drafting

1. The statement surface is sound. Nothing here reopens stage one.
2. Before drafting W5, W6 or W8, read this note's mechanism section rather than
   the contract's — three of its explanations are wrong, and one of them
   predicts silence where the real behaviour is a false subgoal.
3. The W6 `calc` fix as applied does not close. It needs a pre-combined `have`
   or a fourth line.
4. `gcongr` with an explicit `?_` template turns every one of these silent
   residuals into a hard error at the exact seam. That is a free improvement
   over "insert a normalization and hope", and it is the single change most
   likely to save CI rounds.
5. Do not write `ℂ_ℤ`.

## Standing of this note itself

Each verdict above is the work of **one** verifier, and no verifier was checked
by another. That is the same evidentiary standard the record being reviewed
carries, and it is stated here for the same reason. What is stronger here is
that every verifier was instructed to refute and required to quote what it read,
and that the mechanism claims were settled against implementation source
(`Mathlib/Tactic/GCongr/Core.lean`, `Lean/Elab/BuiltinNotation.lean`,
`Lean/Elab/Term/TermElabM.lean`) rather than against intuition. What is weaker
is that no kernel ran: nothing below was elaborated, and a tactic that source
says will fire could still fail on an instance path nobody enumerated.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
Lean core read at tag v4.31.0, matching `lean-toolchain`.

## Addendum — the same treatment, applied to this note's own repairs

The `RH-018` edits written from this note were themselves put to an adversarial
verifier before merge, on the reasoning that a correction is exactly as capable
of being wrong as the thing it corrects — which is the lesson the `W6` case
teaches, and the lesson the 2026-08-08 `WeierstrassCurve` count teaches, that
number having entered the contract inside a finding's own recommended fix text.

Five load-bearing claims were attacked. The result:

| claim | verdict |
|---|---|
| `hL2 := hL.trans (by gcongr)` descends correctly | PARTIAL — descent right, terminal discharge unsecured |
| `mul_le_mul_of_nonneg_left hL2 (by norm_num)` | PARTIAL — signature right, locator off by one |
| the shorter `Set.fintypeCard_eq_ncard` card chain | **REFUTED** |
| `haveI` opaque, `letI` deletes the hop | CONFIRMED |
| `mem_closedBall_zero_iff` supplies `‖x‖ ≤ R` | CONFIRMED, two precision notes |

**The refuted one was the claim its author had already flagged as
under-specified**, which is worth recording as evidence that the flag was not
enough: a stated doubt does not repair a document, and the paragraph shipped in
a form that read as settled. Three separate defects were in it — the `@[simp]`
direction runs *into* `ncard` and never back out, so the chain does not
"continue" anywhere; the head of the chain needs three further simp lemmas the
paragraph never named; and the route only works if step 2 stops at
`tprod_fintype`, contradicting the `Finset.prod_set_coe` addition made in the
same edit. The corrected text carries all three and now tells the drafter to
pick one route in step 2 and make step 4 match it.

The two PARTIALs mattered less but would each have cost a round. The `gcongr`
terminal goal `(1 - ‖z‖)⁻¹ ≤ 2` is closed only from a **named** hypothesis whose
type is `Inv.inv`-headed; the contract's step 2 was prose, and its own cited
`div_le_iff₀` naturally produces the `HDiv`-headed `1 / (1 - ‖z‖) ≤ 2`, which
the discharger cannot use at reducible transparency. And `hKR` was consumed in
step 3 without ever being bound in step 1.

Also corrected from the same report: the forward-discharger extension set is
five, not two, so the phrase "and nothing more" was false; and
`Algebra/Order/GroupWithZero/Defs.lean:225` is the `@[gcongr]` attribute line,
the declaration being :226 — against this contract's own convention of citing
the declaration and naming the attribute line separately.

What survived is worth stating too, because an all-negative report would
misrepresent the pass: the `gcongr` shape-gate analysis, the `2 ≤ 4/(p+1)`
false-goal derivation with its lemma-priority reasoning, the "no diagnostic in
the CI log" prediction, the impossibility of a bridging `@[gcongr]` lemma, the
striking of `rw [← div_pow]`, and the whole `haveI`/`letI` argument including
the `letI` remedy — all confirmed against source, several with the pin's own
explanatory comments quoted back.

Standing of the addendum: one verifier, instructed to refute, reading
implementation source (Mathlib at the pin; Lean core at tag v4.31.0, matching
`lean-toolchain`). No kernel ran. The one thing it marked genuinely undecidable
from source is whether `positivity` discharges the two side goals in the
concrete instantiations — the extensions exist, but extension dispatch is not a
source-text fact.
