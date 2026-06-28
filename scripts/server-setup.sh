#!/usr/bin/env bash
# One-command setup for a fresh Ubuntu server: Lean v4.31.0 + Mathlib cache (+ optional CAS).
# Usage:  bash scripts/server-setup.sh         (Lean only)
#         WITH_CAS=1 bash scripts/server-setup.sh   (also PARI/sympy)
set -euo pipefail

# Non-interactive apt: prevents the needrestart service-restart prompt from hanging
# a non-tty SSH session (the classic "stuck forever" on Ubuntu 22.04/24.04).
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
export NEEDRESTART_SUSPEND=1
APT="apt-get -y -o Dpkg::Options::=--force-confold -o Dpkg::Options::=--force-confdef"

echo "== packages =="
$APT update
$APT install curl git build-essential

echo "== elan + Lean toolchain =="
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
fi
export PATH="$HOME/.elan/bin:$PATH"

echo "== build project with Mathlib cache =="
# Run from the repository root (clone/rsync it first).
if [ -f lakefile.toml ] || [ -f lakefile.lean ]; then
  lake exe cache get        # download prebuilt Mathlib oleans (~5-7 GB) instead of compiling
  lake build
else
  echo "Run this from the repo root (the lakefile must be present)."
fi

if [ "${WITH_CAS:-0}" = "1" ]; then
  echo "== optional CAS (scratchpad for number theory: factorizations, witnesses) =="
  # sympy via apt avoids PEP-668 'externally-managed-environment' pip errors on 24.04.
  $APT install pari-gp python3-sympy
  # SageMath is large; install only if desired: $APT install sagemath
fi
echo "== done. Verify with: lake env lean Ecdlp/Proved/CubeRoot.lean =="
