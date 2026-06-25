#!/usr/bin/env bash
# One-command setup for a fresh Ubuntu server: Lean v4.31.0 + Mathlib cache (+ optional CAS).
# Usage:  bash scripts/server-setup.sh         (Lean only)
#         WITH_CAS=1 bash scripts/server-setup.sh   (also SageMath/PARI/sympy)
set -euo pipefail

echo "== packages =="
apt-get update -y
apt-get install -y curl git build-essential

echo "== elan + Lean toolchain =="
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
export PATH="$HOME/.elan/bin:$PATH"

echo "== build project with Mathlib cache =="
# Run from the repository root (clone it first if needed).
if [ -f lakefile.toml ] || [ -f lakefile.lean ]; then
  lake exe cache get        # download prebuilt Mathlib oleans (~5-7 GB) instead of compiling
  lake build
else
  echo "Run this from the cloned repo root (git clone the repository first)."
fi

if [ "${WITH_CAS:-0}" = "1" ]; then
  echo "== optional CAS (scratchpad for number theory: factorizations, witnesses) =="
  apt-get install -y pari-gp python3-pip
  pip3 install --quiet sympy
  # SageMath is large; install only if desired: apt-get install -y sagemath
fi
echo "== done. Verify with: lake env lean Ecdlp/Proved/CubeRoot.lean =="
