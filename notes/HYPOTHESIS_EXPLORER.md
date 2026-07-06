# Hypothesis explorer — disciplined, non-monotonous idea search (DeepSeek breadth tier)

## Honest purpose
DeepSeek is the **breadth / exploration tier**, not a breakthrough machine. It will *not* crack
ECDLP. Its job is to **map the hypothesis space systematically and without repetition**, and for
every idea produce a **concrete, machine-checkable sub-claim** that either fails fast (→ grows the
honest no-go map) or, rarely, survives (→ a lead for the depth tier, Fable, to deepen). The main
product of this tier is a **growing, machine-checked no-go map + a short list of live leads** —
that is exactly the honest north-star search, not a promise of a break.

The failure mode we engineer against: ask a model "how might one solve ECDLP?" and it returns the
same standard list every run (Semaev, Weil descent, isogeny-to-weak-curve, Smart, Gröbner…). That
is monotonous and low-value. Below is how we force diversity and discipline.

## Anti-monotony design (six mechanisms)

1. **Persistent hypothesis ledger + explicit novelty pressure.** `notes/HYPOTHESIS_LEDGER.md`
   records every hypothesis ever generated with a short canonical signature and its outcome. Each
   new prompt is fed the full list of already-seen signatures with the instruction *"these are
   already explored — do NOT restate them; propose directions orthogonal to all of them."* This
   memory-across-runs is the core anti-repetition mechanism.

2. **Axis-structured coverage.** The search space is partitioned into explicit axes; each run
   targets the *least-explored* axis (tracked in the ledger), so the search cannot collapse into
   one corner:
   - algebraic (endomorphism ring / CM, isogeny graph, torsion structure `E[n]`),
   - index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases),
   - analytic / p-adic (formal groups, canonical heights, Frobenius/`L`-functions),
   - geometric (higher genus, abelian varieties, moduli, covers),
   - cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory),
   - reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants).

3. **"Avoid the known" grounding.** Every prompt is given (a) our **machine-checked no-go facts**
   (secp256k1 resists MOV — embedding degree > 100; anti-Smart/anomalous — trace of Frobenius;
   Semaev is prime-field-irrelevant) and (b) the standard *failed* approaches, with the constraint:
   propose ideas that are **not restatements** of these. A **novelty-critic** second pass rejects
   near-duplicates before anything is recorded.

4. **Force a checkable sub-claim (the discipline that separates signal from vibes).** A hypothesis
   is accepted into the pipeline **only if** it names a concrete, small, **kernel- or
   sympy-checkable** consequence (e.g. a polynomial identity, a coprimality/resultant fact, a
   torsion/degree count, an explicit map). No checkable sub-claim ⇒ vacuous ⇒ discarded. This is
   what turns "an idea" into a testable structural claim.

5. **Diversity sampling.** High temperature + `N` independent samples per axis + semantic dedup on
   the canonical signatures, so a single run yields varied ideas rather than one repeated.

6. **Outcome loop, recorded.** Each surviving sub-claim is verified/refuted (kernel via the server,
   or sympy for algebraic identities) and filed:
   - **refuted** → append to the no-go map (a *result*, not a failure),
   - **inconclusive / needs foundation** → parked with the missing dependency named,
   - **supported** → promoted to a **lead** for Fable + the Lean corpus to deepen.
   The ledger grows monotonically; no run repeats a prior signature.

## Tiers (who does what)
- **Breadth (DeepSeek):** wide, diverse hypothesis generation + checkable sub-claim extraction.
- **Verifier (Lean kernel / sympy):** the only judge — refutes or confirms each sub-claim.
- **Depth (Fable):** takes a *supported lead* or a hard narrow rung and does the deep reasoning.
- **Director (charter):** schedules runs, rotates axes, curates the ledger, escalates a genuine
  breakthrough per charter §4 (freeze + verify + human before any external mention).

## Honest expected output
Overwhelmingly: a **precise, machine-checked no-go map** — which *is* the deliverable of the
honest search and a publishable contribution. Occasionally: a lead worth deep work. Essentially
never (but not provably never): the break itself. We state these odds plainly and do not inflate
them.

## Tiering & token economics (why this saves Fable spend)
DeepSeek is the **cheap wide front-end**; Fable is the **expensive narrow back-end**. The explorer
makes each DeepSeek agent do the token-heavy work — broad generation **and** writing a
self-contained sympy script that checks its own sub-claim — and then we RUN that script offline
(the judge). ~most ideas are refuted for free and become no-go entries; only the sympy-**supported**
survivors are written to `notes/HYPOTHESIS_LEADS.md` (with the verified certificate) and handed to
Fable. So Fable is never spent on the wide search or on unverified ideas — only on pre-chewed,
already-checked narrow targets. DeepSeek is dirt-cheap (~sub-cent per hypothesis), so the fleet can
run 10–20+ agents per cycle; concurrency is capped by `--workers`, not by cost.

## Status
`scripts/hypothesis_explorer.py` is **v1 — parallel and self-verifying**: a `ThreadPoolExecutor`
fleet of axis-pinned DeepSeek agents (`--agents`, `--workers`), each returning a hypothesis +
sub-claim + a sympy script that is executed offline (`run_sympy` → supported/refuted/parked),
ledger dedup by canonical signature, and a leads file for the depth tier. Locally verified: the
module compiles, no-ops with zero spend when `DEEPSEEK_API_KEY` is absent, and the sympy verifier
correctly returns supported/refuted/parked on known inputs. The DeepSeek calls run only where the
key lives — GitHub Actions: `.github/workflows/hypothesis-explore.yml` (dispatch + weekly cron,
draft-PR only, `DEEPSEEK_API_KEY` secret). Not yet exercised against the live DeepSeek API.
