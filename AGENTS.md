# AGENTS.md — orientation for any Claude instance (web or server)

Single source of truth for "what this is, what's done, what to run next". Read this
together with `VERIFIED.md` (the proved-theorem ledger) and `BARRIERS.md` (what's
blocked and why). Authoritative protocol: `AGENT.md`; conventions: `CLAUDE.md`.

## What this project actually is (read this first)
A **machine-checked formalization** of the mathematics of ECDLP / elliptic-curve
discrete-log cryptography in **Lean 4 + Mathlib**. It is a *verified knowledge
asset*, NOT an attempt to break secp256k1. Breaking ECDLP on secp256k1 (~2^128
work) is infeasible; no "higher problem" gives a shortcut. The valuable, achievable
program is: **a verified formal library of EC/DL cryptography** — which subsumes the
ECDLP formalization and yields surplus (protocol library, hardness foundations,
barriers map, potential upstream Mathlib contributions).

## The one invariant
Green build = every built theorem fully proved (Lean kernel). Never weaken/`sorry`/
`admit`/add axioms. Conditional theorems may use hypotheses like `[Fact p.Prime]`
(a hypothesis, NOT an axiom).

## Current state (keep updated)
- `main`: **58 theorems**, 14 files under `Ecdlp/Proved/`, 0 sorry, 0 axioms.
- Pillars: (1) Shoup/Nechaev generic-group `Ω(√p)` + BSGS/rho `O(√n)` ⇒ `Θ(√n)`,
  secp256k1 ≥128-bit generic security; (2) verified DL-crypto library (Schnorr,
  Pedersen, DH, ElGamal, Okamoto, Chaum–Pedersen, MuSig2/Taproot, Feldman VSS,
  adaptor, blind Schnorr, threshold ElGamal); (3) secp256k1 grounded in Mathlib EC
  (`EllipticCurve`, `j=0`, β/λ order 3, generator on curve & nonsingular).

## How to verify
- **CI-only (web sandbox)**: push to a branch → GitHub Actions `lake build` + no-sorry
  gate (~5 min/cycle). The web sandbox's egress blocks the Lean toolchain, so no
  local Lean here.
- **Local (server)**: run `scripts/server-setup.sh` → `lake build` / `lake env lean`
  in seconds. 10–50× faster. Use this on the rented server.

## Workflow
1. Branch from `main` (`claude/admiring-darwin-uouep1`). 2. Add theorem(s), grep the
local Mathlib source for exact API. 3. Push → CI (or local build). 4. On green: add a
`VERIFIED.md` row, open a PR, squash-merge to `main`. 5. Reset branch to `main`, repeat.

## Next high-value targets
- **Primality certificates** for `p` and `n` (`Nat.lucas_primality`) → removes all
  `[Fact p.Prime]/[Fact n.Prime]` hypotheses, making ~10 theorems unconditional.
  Factorizations are in `notes/PRIMALITY.md`. Deep (recursive Pratt) — best done with
  local Lean on the server.
- Other standard curves (P-256, Curve25519) via the same machinery.
- Drafting missing Mathlib foundations (Weil pairing, Semaev polynomials, cost model)
  for upstream contribution.
