# CLAUDE.md — working conventions for this repository

Machine-checked layer for the ECDLP knowledge graph (Lean 4 + Mathlib). This file
is guidance for automated/assisted runs. The authoritative protocol is `AGENT.md`.

## The one invariant
**A green build means every built theorem is fully proved.** The Lean kernel is the
only judge of correctness. Never weaken, delete, or `sorry`/`admit` a proof to make
CI pass. Never add axioms.

## Directory map
| Path | Role | Built by `lake build`? | no-`sorry` gate? |
|---|---|---|---|
| `Ecdlp/Secp256k1Verified.lean`, `Lagrange.lean`, `Statements.lean` | existing proved base | yes | yes |
| `Ecdlp/Ontology.lean` | ECDLP objects the stems build on (planned, Stage C) | yes | yes |
| `Ecdlp/Proved/*.lean` | promoted proofs | yes (import in `Ecdlp.lean`) | yes |
| `Ecdlp/Targets/*.lean` | open conjecture stems (one `sorry` each) | **no** (not imported) | **no** (excluded) |
| `targets/*.json` | prover-loop registry (status, budget) | — | — |
| `data/KG_CLAIM_FORMALIZATION_v1.csv` | read-only claim corpus | — | — |

The no-`sorry` gate in `.github/workflows/ci.yml` scans `*.lean` under `Ecdlp/`
**excluding `Targets/`**. Open stems must never be imported from `Ecdlp.lean`.

## Layers
1. **Generator (Layer 3)** — `scripts/generator.py` reads the corpus and writes
   open stems into `Ecdlp/Targets/`. It only *proposes* statements; it never asserts
   a proof.
2. **Prover loop (Layer 2)** — tries each open target: first a zero-cost tactic
   ladder (`rfl`, `decide`, `native_decide`, `simp`, `omega`, `ring`, `aesop`), then
   Featherless models (Pythagoras-Prover-4B → Goedel-Prover-V2-32B).
3. **Verifier (Layer 1)** — `lake build` / `lake env lean`. Accepts only if Lean
   verifies with no `sorry`.

## Promotion
Targets → Proved only when Lean accepts the proof. Then: add the import to
`Ecdlp.lean`, append a row to `VERIFIED.md`, set the `targets/*.json` status to
`verified`. The promotion bot (`prove.yml`, Stage B) commits this via a **PR**, not
a direct push to `main`; a human merges.

## Hard rules
- No secrets in the repo. The Featherless key is only a GitHub Actions secret
  (`FEATHERLESS_API_KEY`). Never print API keys.
- Reproducibility: Mathlib is pinned via `lake-manifest.json` / `lakefile.toml`
  (Lean v4.31.0). Do not bump without intent.
- No local Lean toolchain is assumed in dev containers; CI is the verifier.
- The generator proposes statements; truth is decided only by the kernel.
