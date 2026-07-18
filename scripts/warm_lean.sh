#!/usr/bin/env bash
# warm_lean.sh — bring up a local Lean+Mathlib toolchain for seconds-fast, in-container
# proof checking (`lake env lean File.lean`), removing the CI round trip from the inner loop.
#
# WHY: without this, every proof is written blind and judged only by GitHub CI (~2–15 min
# cold Mathlib build per attempt). With a warm toolchain + Mathlib olean cache, a single
# file typechecks locally in seconds — the ~10× lever (see AUTONOMY.md §Speed).
#
# PREREQUISITE (one-time, maintainer-only — the container cannot do this itself): the
# environment's Network access must allow the Lean toolchain + Mathlib cache hosts. In the
# Claude Code environment settings: Network access → Custom → Allowed domains (keep the
# default package-manager list checked), add:
#     *.lean-lang.org
#     lakecache.blob.core.windows.net
# github.com / objects.githubusercontent.com / raw.githubusercontent.com are already in the
# default Trusted list. Until those two are allowed, the toolchain step below 403s and this
# script no-ops with a clear message (it never fails the session).
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

# 0. Reachability preflight — fail fast with a precise message if egress is still closed.
if ! curl -fsS -o /dev/null --max-time 12 https://release.lean-lang.org 2>/dev/null; then
  say "release.lean-lang.org is NOT reachable (egress still blocked). Add '*.lean-lang.org'"
  say "and 'lakecache.blob.core.windows.net' to the environment's Network access → Custom"
  say "allowlist, then re-run. No changes made."
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
