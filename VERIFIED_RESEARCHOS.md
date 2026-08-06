# VERIFIED_RESEARCHOS.md — result ledger for non-ECDLP (ResearchOS) domains

The ResearchOS-wide result ledger required by barrier `S0-TRUST`
(`domains/riemann-hypothesis/S0_TRUST_DESIGN.md`). One row per claim; a row
may exist **only** for a declaration the Lean kernel has checked in the built
`ResearchOS` library. Machine gates: `scripts/gen_researchos_registry.py
--check` (resolution, anchors, inverse coverage "built ⇒ ledgered ⇒
audited"), the generated `ResearchOS/LedgerAxiomAudit.lean` +
`scripts/check_axioms.py` (per-row axiom base), and
`scripts/check_ledger_isolation.py` (this ledger never feeds the ECDLP
headline counts in `VERIFIED.md` / `data/stats.json`).

Parsing contract (`ledger_utils.parse_researchos_ledger`): every data row has
**exactly 12 cells**; a literal `|` inside a cell is forbidden. The
`statement_anchor` cell is `file:line@sha256:<12hex>` over the declaration's
statement slice (declaration line through the first `:=`, lines rstripped);
rows citing several declarations carry one anchor per declaration in citation
order, space-separated. `axiom_base` is `standard` (⊆ {propext,
Classical.choice, Quot.sound}) or `standard+native_decide` (compiler-trust
disclosed per row). Domain prefixes: `nt-` → `number-theory-elementary`,
`RH-` → `riemann-hypothesis` (RH rows must cite files under
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`).

| claim_id | domain | declaration | file | statement_anchor | source_contract | review_record | axiom_base | method | date | status | claim_scope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nt-prime-2017 | number-theory-elementary | `ResearchOS.NumberTheory.prime_2017` | ResearchOS/NumberTheory/Elementary.lean | ResearchOS/NumberTheory/Elementary.lean:22@sha256:ec11f2f4623e | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | A single primality fact; implies nothing beyond 2017 being prime. |
| nt-mersenne-m13 | number-theory-elementary | `ResearchOS.NumberTheory.mersenne_M13_prime` | ResearchOS/NumberTheory/Elementary.lean | ResearchOS/NumberTheory/Elementary.lean:26@sha256:eb24f7243824 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Primality of 8191 only; no statement about Mersenne primes in general. |
| nt-carmichael-561-composite | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_561_not_prime` | ResearchOS/NumberTheory/Elementary.lean | ResearchOS/NumberTheory/Elementary.lean:30@sha256:b4bead1872bf | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Compositeness of 561 only; Carmichael property itself is not formalized. |
| nt-carmichael-561-korselt | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_561_factorization` | ResearchOS/NumberTheory/Elementary.lean | ResearchOS/NumberTheory/Elementary.lean:34@sha256:3acdc80793c9 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | The arithmetic identity 561 = 3·11·17 only; Korselt's criterion is not formalized. |
| nt-mersenne-m17 | number-theory-elementary | `ResearchOS.NumberTheory.mersenne_M17_prime` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:23@sha256:8cb349683e9b | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Primality of 131071 only. |
| nt-mersenne-m19 | number-theory-elementary | `ResearchOS.NumberTheory.mersenne_M19_prime` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:26@sha256:b82156df3a60 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Primality of 524287 only. |
| nt-carmichael-1105-composite | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_1105_not_prime` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:29@sha256:eee042c70faf | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Compositeness of 1105 only. |
| nt-carmichael-1105-korselt | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_1105_factorization` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:33@sha256:9dbd4969ea42 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | The arithmetic identity 1105 = 5·13·17 only. |
| nt-carmichael-1729-composite | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_1729_not_prime` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:38@sha256:0c8c6135c9f3 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Compositeness of 1729 only. |
| nt-carmichael-1729-korselt | number-theory-elementary | `ResearchOS.NumberTheory.carmichael_1729_factorization` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:42@sha256:9eeefd242cc5 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | The arithmetic identity 1729 = 7·13·19 only. |
| nt-twin-10007-10009 | number-theory-elementary | `ResearchOS.NumberTheory.prime_10007` `ResearchOS.NumberTheory.prime_10009` | ResearchOS/NumberTheory/MoreFacts.lean | ResearchOS/NumberTheory/MoreFacts.lean:45@sha256:b1aca2326739 ResearchOS/NumberTheory/MoreFacts.lean:48@sha256:b120feaab434 | — | notes/reviews/RESEARCHOS_NT_BACKFILL_REVIEW_2026_08_05.md | standard | norm_num | 2026-08-05 | proved | Two primality facts; the twin-pair framing is descriptive, not a formalized twin-prime statement. |
