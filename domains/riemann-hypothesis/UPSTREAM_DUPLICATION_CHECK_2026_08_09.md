# Upstream duplication check for the Weierstrass package — 2026-08-09

Landed under `RH-018`, whose exit criteria require this check to be recorded —
and to be described as HALF closed, which is what it is.

## Why

`UPSTREAM_POOL_V2.md` finding 2 records that no scout checked the Mathlib PR
queue, that three of four said so explicitly, and that one candidate
(Poisson–Jensen) turned out to be an open upstream PR — caught by accident. The
note's own remedy: *"Add an upstream-PR check to the scouting method."* This is
the first run of that check.

## What could and could not be checked

**Could not: the in-flight PR queue.** This session's GitHub credential is scoped
to `KeyAIGit/-ecdlp-lean-verification`; every REST or Search read of
`leanprover-community/mathlib4` returns 403. Anonymous git reads (clone/fetch)
are served, and `raw.githubusercontent.com` is reachable, but neither exposes
pull requests. Attaching mathlib4 with write credentials would expose the API
and is the wrong instrument for a read-only reconnaissance. **So the in-flight
check remains unavailable and the gap `UPSTREAM_POOL_V2` names is only half
closed.**

**Could: everything that has LANDED.** Current `master` was compared against the
pin `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0, 2026-06-15) through
`raw.githubusercontent.com`, which needs no API.

## Result — no duplication, at module, file, or declaration granularity

**Module level.** `Mathlib.lean` at master lists 8308 modules against the pin's
8169: **160 new, 21 removed or renamed.** A deliberately broad regex
(`Weierstrass|Hadamard|Product|Genus|Nevanlinna|ValueDistribution|Rouche|Hurwitz|
Montel|Casorati|Jensen|ArgumentPrinciple|Multipliable`) matches 7 of the 160, and
all 7 are false positives on inspection — `LinearAlgebra.Matrix.HadamardMatrix`,
three `PiTensorProduct` modules, `InnerProductSpace.ExteriorPower`,
`InnerProductSpace.NormDet`, and one genuine but unrelated Nevanlinna module (see
below). **No elementary-factor, canonical-product or Hadamard-factorization
module has landed.**

**Declaration level.** All nine names the contract declares were re-run against
current master in the eight files the package depends on: **zero hits for every
one.** The contract's collision-freedom claim therefore holds not only at the pin
but two months downstream of it — a stronger statement than the contract makes.

**The `[GEN]` lemma still fills a real gap.** A verifier established this session
that no `analyticOrderAt` Finset-product lemma exists anywhere at the pin. Master
has not closed it either: `Analysis/Analytic/Order.lean` grew from 700 to 718
lines, and its three new declarations are
`codiscreteWithin_setOfPred_analyticOrderAt_eq_zero_or_top`,
`codiscrete_setOfPred_analyticOrderAt_eq_zero_or_top` and
`isClopen_setOfPred_analyticOrderAt_eq_top` — none about products. Grepping
master's Order.lean for any product token returns nothing. **Two months of
upstream work have not produced the lemma, which is evidence the gap is real
rather than an artifact of an old pin.**

## What did move, and why it matters anyway

**`Mathlib.Analysis.Complex.ValueDistribution.Proximity.IntegralPresentation` is
new since the pin.** That is in the directory `UPSTREAM_POOL_V2` finding 3 named
as *"a present area nobody opened, and it is the one that matters"*, and which
`RH-014` then examined and returned a null result on (107 declarations, zero
mention of ζ or ξ). The null result stands — this is one more generic
Nevanlinna module, not a zeta application — but it shows the upstream Nevanlinna
programme is actively advancing. Anything the RH lane plans in that direction
should assume it will be overtaken.

**Seven of the eight dependency files changed since the pin.**

| file | pin → master |
|---|---|
| `SpecialFunctions/Complex/LogBounds.lean` | 446 → 451 lines |
| `Analysis/Complex/LocallyUniformLimit.lean` | 209 → 209, content differs |
| `Analysis/Analytic/Order.lean` | 700 → 718 |
| `Analysis/Analytic/Constructions.lean` | 1226 → 1284 |
| `Topology/Algebra/InfiniteSum/Basic.lean` | 789 → 803 |
| `Normed/Module/MultipliableUniformlyOn.lean` | 157 → 157, content differs |
| `Trigonometric/Cotangent.lean` | 411 → 411, content differs |
| `NumberTheory/ModularForms/DedekindEta.lean` | unchanged |

This changes nothing today — the repository is pinned and `CLAUDE.md` forbids
bumping without intent — but it prices a future bump honestly: every locator in
the Weierstrass contract would need re-opening, since seven of eight source
files have moved. The contract's ~90 line-number citations are pin-specific
by construction.

## Method note, for the next scout

The check that worked costs eight `curl`s against `raw.githubusercontent.com`
plus one for `Mathlib.lean`, and needs no credential of any kind. It answers
"has this landed upstream?" completely. It does **not** answer "is someone
proving this right now?", which is the question that actually caught
Poisson–Jensen, and which stays unanswerable from this session.
