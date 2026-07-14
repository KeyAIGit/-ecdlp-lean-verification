# Setup

Machine-checked Lean 4 + Mathlib layer for the ECDLP / secp256k1 knowledge graph.
CI is the authoritative verifier; a local Lean toolchain is optional. The one
invariant: **a green build means every built theorem is fully proved** — the Lean
kernel is the only judge. Never `sorry`/`admit`, weaken a proof, or add an axiom.

## Prerequisites
- **git** and **Python 3** (the stats/doc scripts use the standard library only —
  no pip installs).
- **To build Lean locally (optional):** `elan` (the Lean toolchain manager). It
  installs the pinned **Lean v4.31.0** from `lean-toolchain`. You do **not** need a
  local Lean install to contribute — CI verifies every push.
- **Disk:** ~5–7 GB for the prebuilt Mathlib `.olean` cache.
- The toolchain is pinned (`lean-toolchain` → Lean v4.31.0), the Mathlib revision in
  `lakefile.toml`, and exact deps in `lake-manifest.json`. Do not bump without intent.

## Build (`lake build`)
```sh
# one-off: install elan (Lean toolchain manager)
curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain none

# from the repo root:
lake exe cache get     # pull prebuilt Mathlib oleans (~5–7 GB) — nothing recompiles
lake build             # build AND kernel-verify every proof (defaultTarget: Ecdlp)
```
The core secp256k1 file is proved on Lean core alone (no Mathlib) and can be checked
directly:
```sh
lake env lean Ecdlp/Secp256k1Verified.lean   # exits 0 with no output
```
Open conjecture stems live in `Ecdlp/Targets/` — one `sorry` each, intentionally
**not** imported and **not** built, so they never touch the build gate.

## How CI verifies (`.github/workflows/ci.yml`, on every push / PR / dispatch)
The "Verify Lean proofs" job is the sole correctness signal. In order:
1. **Count-consistency gate** — `python3 scripts/check_counts.py` fails on headline
   count drift between `VERIFIED.md` and the derived docs.
2. **No-`sorry` gate** — greps `*.lean` under `Ecdlp/` (excluding `Targets/` and the
   `AxiomAudit.lean` meta-harness); any `sorry` in a built file fails the run.
3. **No-leak gate** — fails if any built file does `import Ecdlp.Targets` (which would
   pull a `sorry` into the build graph).
4. **Build** — install elan → `lake exe cache get` → restore cached `.lake/build` →
   `lake build`. The kernel verifies every theorem.
5. **Axiom audit** — elaborates `Ecdlp/AxiomAudit.lean`, then `scripts/check_axioms.py`
   asserts no result depends on `sorryAx` or any axiom outside the allowed base
   `{propext, Classical.choice, Quot.sound, Lean.ofReduceBool}`. This is what makes
   "0 custom axioms" machine-enforced, not just documented.
6. **Non-blocking** — typecheck the open stems, a Featherless smoke test, a prover
   attempt. None of these can fail the build.

Green build ⇒ every built theorem fully proved, 0 `sorry`, 0 custom axioms.

## Run the warm-server loop
A warm **Hetzner** node keeps a local Lean+Mathlib cache so `lake env lean <file>`
verifies a single file in seconds instead of a ~10-minute CI round-trip. It is a
**fast search accelerator, not a trust root** — every candidate still returns through
a reviewed PR and the CI gate. The dev sandbox cannot reach the box; all server work
goes through GitHub Actions runners (which have network).

**One-time (human — see `notes/SERVER_RUNBOOK.md`, `notes/SERVER_CONNECT.md`):**
- Bring up the box, clone the repo, run `bash scripts/server-setup.sh`
  (elan + Lean v4.31.0 + `lake exe cache get` + build).
- Add repo secrets (Settings → Secrets and variables → Actions):
  `SSH_PRIVATE_KEY`, `SERVER_HOST`, optional `SERVER_USER` (defaults `root`).

**Run it:** GitHub → **Actions → "Run on server (warm Lean + CAS)" → Run workflow**
(`server-run.yml`, `workflow_dispatch` — manual only, never auto-runs, does not touch
the build gate). Keep the default Lean + sympy smoke test or type a command, e.g.
`lake env lean Ecdlp/Proved/EmbeddingDegree.lean`. Output lands in the run log and the
`server-output` artifact.

**Tactic ladder on the box (optional, no API key):**
```sh
python3 scripts/prover_loop.py --tier0-only   # Tier-0: rfl/decide/native_decide/simp/omega/ring/aesop
```
The model tiers (Featherless) are currently idle — see the INFRA note below.

## Regenerate docs (all derived artifacts; Python 3 stdlib only; run from repo root)
```sh
python3 scripts/gen_stats.py             # data/stats.json + badges/theorems.json  (from VERIFIED.md)
python3 scripts/build_frontier_map.py    # data/frontier_map.json  (per-claim corpus status)
python3 scripts/build_knowledge_graph.py # data/knowledge_graph.json + .md
python3 scripts/build_dashboard.py       # dashboard.html + index.html
python3 scripts/coverage_report.py       # COVERAGE.md
python3 scripts/gen_status.py            # STATUS.md  (from stats.json + frontier_map.json)
```
`VERIFIED.md` is the source of truth for counts; **STATUS.md is the canonical human
snapshot — never hand-edit its numbers.** Every headline count in the derived docs is
read from `data/stats.json`, never recomputed, so they cannot disagree. The
**`docs-sync.yml`** workflow runs all of the above plus `scripts/check_counts.py` on
every push/PR that touches `VERIFIED.md` or `scripts/`; on a PR it **fails** if any
regenerated artifact is stale (drift caught in review), and on `main` it regenerates
and commits them with `[skip ci]`.

## Operational reality (infra)
The **durable source of truth is GitHub**: all code, proofs, `VERIFIED.md`, the
knowledge graph, scripts, and workflows live in the repo, and a green `ci.yml` is the
sole proof of correctness. The only persistent compute is a **warm Hetzner
verification node** — a box holding a warm Lean + Mathlib cache so a single file
verifies in seconds — reached exclusively through the **`server-run.yml` GitHub Actions
bridge** (manual `workflow_dispatch`; a runner SSHes in, runs a command, returns a log
+ artifact). The sandbox has no route to the box, so the Actions runner is the only
path. The server merely **accelerates search**; nothing it finds is trusted until CI
re-verifies it, and `main` changes only via reviewed PRs. **Google Drive is not in the
active pipeline** — the claim corpus it once held now lives in `data/`, and nothing
writes back to it. The **Featherless model tiers are idle**: the subscription plan
returns a permanent **HTTP 403** for inference, so Tier-0 (the zero-cost tactic ladder)
plus hand-written proofs carry all the work. There is **no GCP in the active loop**.
The everything-else layer — CI runners and the dev sandbox — is ephemeral by design.
