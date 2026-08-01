# Opus ECDLP Screen Atlas: Quarantined Intake Review

Date: 2026-08-01
Input snapshot date: 2026-07-26
Base commit: `773932223d5584f65cbd0a581c602dc415b0b93c`

## Disposition

The atlas is retained as an immutable, untrusted external snapshot. It is useful
as a source of property candidates, mechanism descriptions, source-reading
queues, and adversarial questions. It is not a verified evidence join and does
not update the canonical scientific state.

Safety result:

- direct canonical imports: **0**;
- scientific outcomes: **0**;
- ranker labels: **0**;
- route closures: **0**;
- authorizations: **0**.

The original files are preserved byte-for-byte under
`archive/untrusted_intake/OPUS-ECDLP-SCREEN-ATLAS-2026-07-26/`. The generated
index in `data/untrusted_evidence_intake/` contains JSON pointers and hashes,
not upgraded claims. Each source is bound by both SHA-256 and its Git blob ID.
After the first protected-main acceptance, the reviewed source fields are
compared with the `origin/main` receipt and cannot be silently rewritten.

The intake gate also scans code, policy, generated-data, and workflow roots for
quarantine references. Only the builder, its tests, artifact registry,
fixpoint gate, generated quarantine output, and invoking workflows are allowed
to name this layer. A ranker, selector, canonical claim builder, or other
scientific consumer that starts reading it makes the gate fail closed.

## Reproduced Structure

The strict parser found:

| Observation | Count |
|---|---:|
| Mechanism rows | 35 |
| Property rows | 223 |
| Requirement strings | 122 |
| Requirement strings containing a TP-like reference | 12 |
| Unique TP-like references | 6 |
| Unique orphan TP-like references | 6 |
| Machine-verifiable join rows | 0 |

The remaining 110 requirements are free prose. All 15 TP-like reference
occurrences point to six IDs absent from `all_properties.json`. The source also
contains neither a machine-readable screen matrix nor a verdict field. The
report's mechanism-to-verdict labels therefore remain manual judgments.

## Data-Quality Findings

All 223 property values are physically JSON strings even when `value_type`
declares an integer or boolean. The intake never coerces them. It records:

- 81 declared integers, of which 16 are not standalone integer lexemes;
- 62 declared booleans, of which 4 contain text beyond a boolean lexeme;
- 20 declared-type parse violations in total.

The mechanisms file contains 19 rows marked `full_text_read`; the Markdown
report says 20. Neither number proves that a primary artifact was obtained or
read because the snapshot supplies no artifact hash and exact claim locator.
Every `source_verified` value is retained only as an untrusted annotation.

## Scientific Risks Retained, Not Promoted

The review identified examples that require separate producer/replay work:

- the PKC `p-1` row overstates `564522` as the largest smooth divisor for any
  smoothness bound, while the canonical engine distinguishes the inapplicable
  M4 regime from the still-open M16 desk-cost question;
- assurance labels mix Lean-kernel, certificate, computed, and documented
  structural arguments;
- EDS equivalence is presented as a no-gain result, which does not exclude a
  future algorithm expressed through EDS;
- the isogeny discussion exceeds what the conditional within-level reduction
  and current evidence establish;
- global prior-art and novelty language is unsafe while the named CANS 2018
  primary source remains full-text unread.

These are audit annotations, not canonical corrections made by this intake.

## Promotion Path

An individual atlas row may enter canonical evidence only through a separate
change that supplies the missing authority: exact source/artifact provenance,
a typed statement, a producer, an algorithmically independent replay where
applicable, scoped assurance, and review against current canonical registries.
Bulk promotion is forbidden.

Run:

```text
python3 scripts/build_untrusted_evidence_intake.py --check
python3 scripts/test_untrusted_evidence_intake.py
```
