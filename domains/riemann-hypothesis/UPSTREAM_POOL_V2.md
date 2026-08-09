# UPSTREAM POOL v2 — reconnaissance of 2026-08-08

Status: **research note, no authorization.** Nothing here is a task, a
commitment, or a route. `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP
lane; the RH queue `tasks/RIEMANN_HYPOTHESIS.md` governs this one. Read
`UPSTREAM_POOL.md` (v1, items 1-8) first — this note is its successor, not its
replacement.

Method: four independent scouts over pinned Mathlib
(`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, v4.31.0) by four different
modalities — directory sweep, downstream need, classical checklist, adjacency
to the built shelf — followed by a completeness critic over the union. No Lean
toolchain exists in this environment; nothing below was elaborated. Every day
count is a proving-time estimate and a **lower bound on wall clock**.

## The three findings that change what to do next

These came from the critic, not the scouts, and each overturns something the
scouts asserted.

### 1. The probe battery does not reference the analysis shelf at all

`grep` of `PROBE_BATTERY_DESIGN.md` for `MellinBound|HarnackDisc|PolyLiouville|
ThreeCircles|GrowthOrder|maxModulus|sSupNormCircle` returns **zero hits**. That
document's own scope line restricts probes to the three RH modules
(`TargetBridge`, `Xi`, `Conj`). So the eleven generic pillars promoted on
2026-08-08 are, today, not reachable by any probe.

This matters because the stated goal of the pillar programme is hundreds of
small automatically-checkable questions that run *without* building a new
pillar each time. Under the current battery design, building more pillars does
not move that goal at all. The cheapest thing that does is a new section of
`PROBE_BATTERY_DESIGN.md` covering the five shelf modules — **zero Lean days**,
and it is the only item that raises the value of every other item below.

Recorded honestly: the "downstream need" scout reported working backwards from
`PROBE_BATTERY_DESIGN.md` §A-§D. Those sections reference no generic pillar, so
that backward-chaining was reconstructed rather than read off. Its candidates
are still good; its stated provenance for them was not.

### 2. One candidate duplicates in-flight upstream work

**Poisson-Jensen** (directory scout, 12d) is an OPEN Mathlib PR: **#42475**,
created 2026-08-05, updated 2026-08-06 — three days before this note. Both its
dependencies (#40191, #41496) are already merged, and its stated consumer is
Project VD's value-distribution formalization.

No scout checked the upstream PR queue; three of the four said so explicitly.
The directory scout had itself written that duplicating in-flight upstream work
is "the worst possible use of this pool" — as its reason for rejecting a
different candidate — and then proposed exactly that. **Add an upstream-PR check
to the scouting method.**

**Update 2026-08-09 — the check now exists and is HALF of what this asked for.**
`UPSTREAM_DUPLICATION_CHECK_2026_08_09.md` records its first run against the
Weierstrass package. It compares current Mathlib `master` to the pin through
`raw.githubusercontent.com` — nine `curl`s, no credential of any kind — and
answers "has this LANDED upstream?" completely, at module, file and declaration
granularity. For that package the answer was a clean no.

It does **not** answer "is someone proving this right now?", which is the
question that actually caught Poisson–Jensen. The session's GitHub credential is
scoped to this repository, so every REST and Search read of
`leanprover-community/mathlib4` returns 403; anonymous git reads and raw file
reads are served, and neither exposes pull requests. Treat the scouting method
as improved, not fixed: a candidate can still be duplicated work in flight, and
nothing available here will say so.

Negative results from the same search, and therefore safe: no open PR matching
Montel, normal family, Rouché, Hurwitz, Casorati, Mellin, Phragmén, harmonic
Liouville, or Harnack.

### 3. A present area nobody opened, and it is the one that matters

`Mathlib/Analysis/Complex/ValueDistribution/` carries substantial Nevanlinna
theory at the pin, including `characteristic` (CharacteristicFunction.lean:53),
`logCounting` (LogCounting/Basic.lean:96, :272) with monotonicity and bounds,
`logCounting_isBigO_one_iff_analyticOnNhd` (Asymptotic.lean:108), and a First
Main Theorem (FirstMainTheorem.lean:97, :109).

`logCounting` is a zero-counting function. `S1-GLOBAL-ZEROS` is the barrier
asking for global zero counting. **No claim is made here that this closes,
advances, or partially closes that barrier** — deciding that requires reading
the barrier row against the actual statements, which nobody has done. What is
established is only that the `S1-GLOBAL-ZEROS` reconnaissance was performed
without examining a directory that contains a counting function, so its cost
assessment should be treated as unverified until someone checks. That check is
route-neutral and is the strongest candidate for a queue task in this note.

## Candidates, ranked

Tier 1 — cheap, absence grep-verified, no open upstream PR.

| # | candidate | days | note |
|---|---|---|---|
| 1 | Minimum modulus principle, global/frontier form | 1 | Best ratio in the union, and a stepping stone to Hurwitz. Take the classical scout's 1-day formulation, not the 2.5-day one — see the false absence below. |
| 2 | Explicit global majorants for `sin`, `cos`, `sinh`, `cosh`, and two polynomial bounds | 1 | Highest fan-out per day: every probe wanting a concrete function bounded needs one of these six. **Conditional**: `bound`/`gcongr`/`positivity` may already close some, and no toolchain here can check. If automation closes them, this drops to zero value. |
| 3 | Eventual-to-global norm-bound upgrade (cobounded ⇒ global on a proper space) | 2 | The step every hypothesis-shaped bound probe must cross. Pairs with #2 in one change. |

Tier 2 — defensible, but only after Tier 1 and only with a named consumer.

| # | candidate | days | note |
|---|---|---|---|
| 4 | Casorati-Weierstrass | 4 | The missing third leaf of a trichotomy Mathlib has the other two of. Most clearly route-innocent item in the union — which is both its virtue and why its probe value is small. |
| 5 | One-sided harmonic Liouville (nonnegative ⇒ constant) | 2 | Genuinely stronger than the pinned two-sided form (Harmonic/Liouville.lean:47). Its "adjacency" to the Harnack shelf module is decorative; the scout said so itself. |
| 6 | rpow growth-scale comparison at `atTop` | 1 | Library hygiene with an excellent ratio and, honestly, no probe that needs it today. |
| 7 | Phragmén-Lindelöf in a sector | 6-8 | Mathlib has strip, quadrant and half-plane forms but no sector. |

Priced but not recommended now: Schwarz reflection (14d), Montel/normal
families (25d — both scouts priced it without citing Arzelà-Ascoli, which is
the engine and is present, so the estimate is unreliable in both directions),
Cauchy integral formula on an annulus with Laurent expansion (28d).

## A false absence, caught by the critic

The "downstream need" scout proposed proving `DiffContOnCl.inv` as a
prerequisite of its minimum-modulus candidate. **It exists at the pin**:
`Mathlib/Analysis/Calculus/DiffContOnCl.lean:117`. Half of that candidate's 2.5
days is work already done, which is why the classical scout's independent
1-day price for the same theorem is the correct one. Two scouts pricing the
same item is what surfaced this; a single scout would have carried the error.

## What the day counts do not include

No estimate here includes the cost of landing. Upstream, review latency is
weeks to months of calendar time regardless of the proving days, and the
repository gains nothing until a pin bump, which `CLAUDE.md` forbids without
intent. In-repo, every public declaration needs a `VERIFIED_RESEARCHOS.md`
ledger row and must pass inverse coverage, plus a contract document — the
existing ones run 750-1650 lines each. Treat every number above as proving time
only.
