# READ_FIRST

A short orientation for an AI (or human) with limited context. Read this before
quoting numbers or making claims about this repo.

## What this is
A **machine-checked Lean 4 + Mathlib layer** for the ECDLP / secp256k1 knowledge
graph. Each theorem here is verified by the Lean kernel. It is a **verified substrate
for research**, plus an honest "no-go" map of what is provable now vs blocked. It is
*not* a solution to any hard problem.

## The one invariant (never violate)
**A green build means every built theorem is fully proved.** The Lean kernel is the
only judge of correctness. Never `sorry`/`admit`, weaken/delete a proof to pass CI, or
add an axiom. Open conjecture stems live in `Ecdlp/Targets/` (one `sorry` each) and are
intentionally never built or imported, so the invariant holds.

## Where the canonical numbers are
**`STATUS.md`** — the single generated snapshot (ledger rows, distinct results, proved
modules, `sorry`=0, axioms=0, corpus coverage). It is produced by
`scripts/gen_status.py` from the machine sources `data/stats.json` and
`data/frontier_map.json`; `VERIFIED.md` is the underlying ledger. **Do not quote a
count from any other doc** — prose files may be stale. If in doubt, cite STATUS.md.

## What NOT to claim
- It does **not** solve ECDLP on secp256k1 and offers **no shortcut**. secp256k1's
  concrete hardness is an **open conjecture**, not a theorem here.
- The generic-group `Ω(√n)` lower bound constrains **black-box** algorithms only; it
  says nothing about non-generic attacks. It is **classical** — Shor breaks ECDLP
  quantumly.
- The protocol library is **verified protocol algebra** (abstract identities), **not**
  proven security of any deployed protocol.
- The GLV object has its **homomorphism half** proved; the `[λ]` eigenvalue is still
  open (gated on point counting `#E(𝔽_p) = n`).
- External model-provers were attempted with **0 accepted**; real progress is the
  tactic ladder + human/assistant formalization. Do not present the autonomous engine
  as having produced the proofs.
- Never claim more than the kernel verifies. When unsure, state the limit plainly.

## Where to go next
For repository ownership and cleanup boundaries, read
`REPOSITORY_ARCHITECTURE.md` before moving or deleting files.

`STATUS.md` (canonical snapshot) · `PUBLISHABLE_UNITS.md` (the 3 standalone results) ·
`VERIFIED.md` (the ledger) · `BARRIERS.md` (the no-go map) · `TRUST_REPORT.md` (what
"verified" rests on) · `SETUP.md` (build + CI + regen) · `ROADMAP.md` (the
strategy & program).
