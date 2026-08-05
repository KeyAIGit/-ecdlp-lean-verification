# ResearchOS nt- ledger backfill review

Date: 2026-08-05

Scope: the dated backfill review required by
`domains/riemann-hypothesis/S0_TRUST_DESIGN.md` §5 Phase 1 for the twelve
pre-existing `ResearchOS.NumberTheory` declarations entering
`VERIFIED_RESEARCHOS.md` as `nt-*` rows. These declarations were already
built and kernel-checked (default lake target since their merge); what was
missing — per verified finding F2 of the design — was a ledger row and a
CI-executed axiom audit. This backfill adds the accounting, not new
mathematics.

## Row-by-row verification

For each of the 11 rows (12 declarations; the twin-prime row cites two):

1. **Statement match**: the ledger claim text matches the Lean statement and
   the corresponding `domains/number-theory/corpus.md` row (ids reused
   verbatim: `nt-prime-2017` … `nt-twin-10007-10009`).
2. **Kernel check**: `lake build` builds `ResearchOS` (default target,
   `lakefile.toml:2`); all twelve proofs are `by norm_num`.
3. **Axiom base**: declared `standard` for every row, consistent with the
   corpus promise (`domains/number-theory/corpus.md:11-12`, no
   `native_decide`); now machine-enforced per row by
   `ResearchOS/LedgerAxiomAudit.lean` + `scripts/check_axioms.py` (the
   audit output must show no axiom outside {propext, Classical.choice,
   Quot.sound} for these names).
4. **Anchors**: `statement_anchor` cells generated from source by
   `scripts/gen_researchos_registry.py` and re-verified on every `--check`
   run; any statement edit invalidates the row until re-reviewed.
5. **Claim scope**: each row's scope sentence states what the theorem does
   NOT claim (e.g. the Carmichael property and the twin-prime notion are not
   formalized — only primality/compositeness/factorization identities are).

## What this review is not

- Not an independent mathematical review of new results — there are none;
  every fact is elementary and was already kernel-checked.
- Not a change to any headline count: `VERIFIED.md`, `data/stats.json`, and
  `badges/theorems.json` are untouched, and
  `scripts/check_ledger_isolation.py` enforces that permanently.
- Not an RH artifact: no `RH-` row exists yet; the first one requires its
  own independent review record per `domains/riemann-hypothesis/README.md`.
