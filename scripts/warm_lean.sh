#!/usr/bin/env bash
# warm_lean.sh — bring up a local Lean+Mathlib toolchain for seconds-fast, in-container
# proof checking (`lake env lean File.lean`), removing the CI round trip from the inner loop.
#
# WHY: without this, every proof is written blind and judged only by GitHub CI (~2–15 min
# cold Mathlib build per attempt). With a warm toolchain + Mathlib olean cache, a single
# file typechecks locally in seconds — the ~10× lever (see AUTONOMY.md §Speed).
#
# KNOWN BLOCKER IN THE CLAUDE-CODE CLOUD SANDBOX (verified 2026-07-18): opening the
# environment Network access (even to **Full**) is NOT sufficient here. The Lean toolchain
# and all Mathlib source repos live on `github.com` under `leanprover*`, and github.com is
# gated by a SEPARATE Anthropic proxy to this session's repo scope — independent of the
# Network-access setting (the docs state GitHub uses a separate proxy). Downloading the
# toolchain returns, verbatim: "GitHub access to this repository is not enabled for this
# session. Use add_repo to request access." There is no non-github mirror of the toolchain
# (`*.lean-lang.org` only redirects to github releases). The container cannot add upstream
# `leanprover/*` repos to session scope, so **local Lean is not achievable in this sandbox**.
#   → The working ~10× path is the ALREADY-BUILT server bridge `.github/workflows/server-run.yml`
#     (a GitHub runner SSHes to the maintainer's server — whose own IP is NOT github-gated —
#     and runs `lake env lean File.lean` on a warm toolchain). It needs repo secrets
#     SERVER_HOST + SSH_PRIVATE_KEY. See notes/SERVER_RUNBOOK.md and AUTONOMY.md §Speed.
# This script is kept for environments WITHOUT the github-scope gate (e.g. a terminal
# `--teleport` session or a self-managed box), where allowing the toolchain + cache hosts
# does suffice.
#
# USAGE:
#   bash scripts/warm_lean.sh          # run once per session (or from the env Setup script)
# Then check a file in seconds:
#   lake env lean Ecdlp/Proved/SomeFile.lean
#
# NOTE ON THE SETUP-SCRIPT 5-MIN LIMIT: `lake exe cache get` pulls ~5 GB and may exceed the
# environment Setup-script build limit. If so, run this manually in the first interactive
# session (sessions persist), or background the cache step from a SessionStart hook.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say() { printf '\n\033[1m[warm_lean]\033[0m %s\n' "$*"; }

# 0. Preflight — probe the ACTUAL toolchain asset (not just the redirector root), so the
#    github-scope gate is detected instead of a false "looks reachable". The asset lives on
#    github releases; a 403 body mentioning "not enabled for this session" is the gate.
TC_ASSET="https://github.com/leanprover/lean4/releases/download/$(cut -d: -f2 lean-toolchain)/lean-$(cut -d: -f2 lean-toolchain | tr -d 'v')-linux.tar.zst"
PRE="$(curl -sSL --max-time 15 "$TC_ASSET" 2>/dev/null | head -c 200 || true)"
if printf '%s' "$PRE" | grep -q "not enabled for this session"; then
  say "BLOCKED by the Anthropic github-scope proxy (not the network policy): the Lean"
  say "toolchain on github.com/leanprover is out of this session's repo scope. Local Lean"
  say "is not achievable in this sandbox — use the server bridge .github/workflows/server-run.yml"
  say "(set SERVER_HOST + SSH_PRIVATE_KEY repo secrets). No changes made."
  exit 0
fi
if ! curl -fsS -o /dev/null --max-time 12 https://release.lean-lang.org 2>/dev/null; then
  say "release.lean-lang.org is NOT reachable (egress closed in this environment). If you"
  say "control the network policy, allow '*.lean-lang.org' + 'lakecache.blob.core.windows.net'"
  say "and re-run. No changes made."
  exit 0
fi

TOOLCHAIN="$(cut -d: -f2 lean-toolchain 2>/dev/null)"
say "pinned toolchain: ${TOOLCHAIN:-<unknown>}"

# 1. Toolchain (elan shims are already present; this fetches the pinned Lean).
say "installing Lean toolchain via elan…"
elan toolchain install "$TOOLCHAIN" || { say "toolchain install failed"; exit 0; }

# 2. Prebuilt Mathlib oleans (~5 GB) — the difference between seconds and a ~1 h from-source build.
say "fetching Mathlib olean cache (lake exe cache get)… this can take several minutes"
lake exe cache get || say "cache get incomplete — 'lake build' will compile the remainder"

# 3. Build the project (fast once the cache is warm; compiles only this repo's deltas).
say "building the project…"
if lake build; then
  say "READY. Check a single file in seconds with:  lake env lean <path/to/File.lean>"
else
  say "lake build reported errors — inspect above; the toolchain/cache are still usable for single-file checks."
fi
