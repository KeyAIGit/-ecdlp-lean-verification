# KeyAI research verification workspace

![Verified theorems](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json)

KeyAI is a verification workspace for long-horizon AI research. This repository
is its public reference deployment: a Lean 4 + Mathlib proof base for
secp256k1, an evidence-gated ECDLP route map, a separate ResearchOS verification
surface, and the provenance contracts that keep all of them honest.

It is a verified research substrate and decision record. It is not an ECDLP
solution, an RH proof, or a self-serve hosted product.

## Start here

| Question | Source |
|---|---|
| What is true right now? | [`STATUS.md`](STATUS.md) |
| Where can I browse every verified surface? | [`VERIFIED_ALL.md`](VERIFIED_ALL.md) or the [results page](https://keyai.org/results.html) |
| Which ECDLP theorem was checked? | [`VERIFIED.md`](VERIFIED.md) |
| Which non-ECDLP ResearchOS theorem was checked? | [`VERIFIED_RESEARCHOS.md`](VERIFIED_RESEARCHOS.md) |
| Which ECDLP routes are selected, parked, or ruled out for the target? | [`repo/ECDLP_DECISION_SUBSTRATE.json`](repo/ECDLP_DECISION_SUBSTRATE.json) and [`explore.html`](https://keyai.org/explore.html) |
| What should be worked on next? | [`tasks/NEXT.md`](tasks/NEXT.md) |
| How is the repository organized? | [`REPOSITORY_ARCHITECTURE.md`](REPOSITORY_ARCHITECTURE.md) |
| How do the generators and checks fit together? | [`scripts/README.md`](scripts/README.md) |
| Which machine contract owns a decision? | [`repo/README.md`](repo/README.md) |

## The central invariant

A green build means every theorem in a built library is accepted by the Lean
kernel. The built surface contains no `sorry`, `admit`, or custom axiom.
Open conjecture stems live under `Ecdlp/Targets/` and are intentionally excluded
from the built proof graph.

Results proved with `native_decide` additionally trust the Lean compiler. The
per-result trust boundary is documented in [`TRUST_REPORT.md`](TRUST_REPORT.md)
and enforced by generated axiom audits.

## Why there are two verified ledgers

The ledgers are intentionally separate:

- [`VERIFIED.md`](VERIFIED.md) owns ECDLP and secp256k1 theorem rows and the
  ECDLP headline counters.
- [`VERIFIED_RESEARCHOS.md`](VERIFIED_RESEARCHOS.md) owns non-ECDLP ResearchOS
  rows and uses a stricter provenance schema with statement anchors, source
  contracts, review records, dates, axiom bases, and claim scope.

[`VERIFIED_ALL.md`](VERIFIED_ALL.md) is a generated navigation index over both.
It does not merge schemas or invent a shared distinct-theorem denominator.

## Repository layers

| Layer | Primary paths | Role |
|---|---|---|
| Kernel-verified proofs | `Ecdlp/`, `ResearchOS/`, `Ecdlp.lean`, `ResearchOS.lean` | Built Lean declarations and imports. |
| Open targets | `Ecdlp/Targets/`, `targets/` | Unproved target stems, never imported into the proved surface. |
| Verified result ledgers | `VERIFIED.md`, `VERIFIED_RESEARCHOS.md`, `VERIFIED_ALL.md` | Canonical theorem rows plus one generated cross-ledger index. |
| Live generated state | `STATUS.md`, `data/`, `badges/` | Counts, registries, frontier maps, graphs, and engine state. |
| Decision contracts | `repo/` | Route, evidence, lifecycle, product, pilot, and ownership contracts. |
| Active work | `tasks/`, `experiments/engine/` | Routed tasks and bounded, review-gated execution. |
| Research memory | `notes/`, `docs/`, `domains/` | Curated explanations, reviews, and domain programs. |
| Public site | `index.html`, `results.html`, `dashboard.html`, `explore.html`, `pilot.html`, `sitemap.xml`, `robots.txt`, `assets/` | Generated public and operator-facing views. |
| Frozen history | `archive/` | Superseded or exploratory material retained for provenance. |

The exhaustive ownership and edit-policy map is
[`repo/ARTIFACTS.yaml`](repo/ARTIFACTS.yaml).

## Current research programs

### ECDLP reference deployment

The ECDLP program formalizes secp256k1 arithmetic, generic-group boundaries,
protocol algebra, GLV structure, Semaev and division-polynomial results, attack
applicability, and exact route decisions. The repository does not claim a
shortcut for the plain single-target secp256k1 discrete logarithm problem.

The current route decision is machine-readable in
[`repo/ECDLP_DECISION_SUBSTRATE.json`](repo/ECDLP_DECISION_SUBSTRATE.json).
Do not infer route priority from theorem volume or from a missing Mathlib module.

### ResearchOS and RH Stage 0

ResearchOS is a separate Lean target for non-ECDLP verification and portability.
The Riemann Hypothesis lane is a Stage 0 specification, foundation-audit, and
route-triage program. It claims no RH proof candidate and no progress on the
conjecture itself.

Its authority is [`tasks/RIEMANN_HYPOTHESIS.md`](tasks/RIEMANN_HYPOTHESIS.md)
and its verified rows live in
[`VERIFIED_RESEARCHOS.md`](VERIFIED_RESEARCHOS.md).

## Build and regeneration

Install the pinned Lean toolchain, then run:

```bash
lake exe cache get
lake build
```

Regenerate the public site and verified-results index:

```bash
python scripts/build_dashboard.py
```

Run the full generated-artifact freshness check:

```bash
python scripts/check_generated_fixpoint.py --check
```

The toolchain is pinned in `lean-toolchain` and `lakefile.toml`. CI is the
verifier of record for the build, no-sorry gate, axiom audits, generated
registries, cross-surface consistency, and artifact ownership.

## Contribution rules

1. Put proved declarations in the built proof surface and ledger them in the
   appropriate canonical ledger.
2. Keep open statements outside the built import graph.
3. Change generated artifacts through their generators.
4. Link to `STATUS.md` instead of copying live counts into prose.
5. Preserve the difference between formal proof, empirical support, route
   disposition, and owner authorization.
6. Do not move or delete high-risk files without a reference scan, provenance
   review, and rollback path.

Agents begin with [`AGENTS.md`](AGENTS.md). Human contributors should also read
[`SETUP.md`](SETUP.md), [`TRUST_REPORT.md`](TRUST_REPORT.md), and
[`ABSTRACT_SCOPE.md`](ABSTRACT_SCOPE.md).

## Authorship and AI disclosure

The human maintainer bears intellectual responsibility for every claim of
novelty and significance. AI systems have assisted with formalization, code,
proof search, testing, and organization. They are tools, not authors. The Lean
kernel establishes acceptance of the declared proof terms; it does not validate
surrounding scientific significance, security claims, or product-market claims.
