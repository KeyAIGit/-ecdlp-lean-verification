#!/usr/bin/env bash
# 24/7 warm prover daemon for the Hetzner CPU node (Layer 2).
#
# Loop: pull the latest dev branch -> run the prover loop (Tier-0 tactic ladder +
# Featherless Pythagoras-4B / Goedel-32B) on every open target -> if the Lean kernel
# accepted any candidate, push the candidates + report to the `server/candidates`
# branch for review. The verified base (main / Ecdlp/Proved) is NEVER touched here;
# promotion stays a reviewed PR. The Lean kernel is the only judge.
#
# Why the server: warm `lake env lean` verifies a candidate in ~30s vs ~5min on CI,
# so the prover loop runs an order of magnitude faster here and can run continuously.
#
# Prereqs (done once by scripts/server-setup.sh + the Console bootstrap):
#   - elan + Lean v4.31.0 installed, project built (`lake build`)
#   - ~/.featherless_key   (0600, the Featherless API key)
#   - ~/.git-credentials   (0600, a GitHub PAT with Contents:read/write on this repo)
#
# Run under tmux so it survives a Console disconnect:
#   tmux new -d -s prover 'bash scripts/prover_daemon.sh >> ~/prover-daemon.log 2>&1'
set -uo pipefail   # deliberately NOT -e: one bad iteration must not kill the daemon

REPO_URL="https://github.com/KeyAIGit/-ecdlp-lean-verification.git"
DEV_BRANCH="claude/admiring-darwin-uouep1"
RESULTS_BRANCH="server/candidates"
SLEEP_SECS="${SLEEP_SECS:-300}"

export PATH="$HOME/.elan/bin:$PATH"
[ -f "$HOME/.featherless_key" ] && export FEATHERLESS_API_KEY="$(cat "$HOME/.featherless_key")"

log(){ echo "[$(date -u +%FT%TZ)] $*"; }

while true; do
  log "=== iteration start ==="

  # --- self-heal git (the server lost .git twice in earlier runs) ---
  if [ ! -d .git ]; then
    log "no .git here; cloning fresh"
    git clone "$REPO_URL" . || { log "clone FAILED; retrying in 30s"; sleep 30; continue; }
  fi
  git fetch -q origin "$DEV_BRANCH" || { log "fetch FAILED; retrying in 30s"; sleep 30; continue; }
  git checkout -q "$DEV_BRANCH" 2>/dev/null || git checkout -qB "$DEV_BRANCH" "origin/$DEV_BRANCH"
  git reset -q --hard "origin/$DEV_BRANCH"

  # --- keep Mathlib oleans + project build fresh (cheap when unchanged) ---
  lake exe cache get >/dev/null 2>&1 || true
  lake build >/dev/null 2>&1 || log "warning: lake build had issues (stems may still verify standalone)"

  # --- run the prover loop (Tier-0 ladder + Featherless models) ---
  rm -rf candidates; mkdir -p candidates
  log "running prover loop over open targets..."
  python3 scripts/prover_loop.py 2>&1 | tail -25

  # --- surface any Lean-accepted candidates for review ---
  if [ -n "$(ls -A candidates 2>/dev/null)" ]; then
    n="$(ls -1 candidates | wc -l | tr -d ' ')"
    log "FOUND $n candidate(s) -> pushing to $RESULTS_BRANCH"
    git checkout -qB "$RESULTS_BRANCH"
    git add -f candidates/ prover-loop-report.md 2>/dev/null
    git -c user.email="prover@keyai.local" -c user.name="prover-daemon" \
        commit -q -m "server prover candidates $(date -u +%FT%TZ)" || true
    git push -fq origin "$RESULTS_BRANCH" 2>&1 | tail -1 || log "push FAILED (check ~/.git-credentials PAT)"
    git checkout -q "$DEV_BRANCH"
  else
    log "no candidates this iteration"
  fi

  log "sleeping ${SLEEP_SECS}s"
  sleep "$SLEEP_SECS"
done
