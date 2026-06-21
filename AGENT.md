# Lean Proof Agent Protocol

This repository uses a layered proof-search system. The agent is not the final authority. Lean is the final authority.

## Mission

Close formal Lean targets without `sorry`, preserve a verified ledger, and never let model output enter the proof base without Lean verification.

## Layers

1. **Chief engineer / planner**
   - Chooses the target theorem.
   - Splits hard targets into smaller lemmas.
   - Selects attempt budgets.
   - Reads Lean errors and decides repair strategy.
   - May use GPT-5.5 or DeepSeek API for planning and code review.

2. **Prover models**
   - Pythagoras-Prover-4B: fast, cheap first-pass proof generation.
   - Goedel-Prover-V2-32B: heavier repair/escalation model.
   - DeepSeek: optional planner/reasoner, useful for lemma decomposition, prompt rewriting, and error analysis.

3. **Verifier**
   - Lean + Mathlib via `lake build` or `lake env lean`.
   - A theorem is accepted only if Lean verifies it and no `sorry` remains.

4. **Ledger**
   - `VERIFIED.md` records accepted claims.
   - Model attempts that fail are not failures of the theorem; they are failed searches.

## Hard rules

- Never commit model-generated proof code directly into verified files unless Lean accepts it.
- Never use `sorry`, `admit`, or placeholder axioms.
- Never print API keys.
- Prefer artifact/report output before changing `Ecdlp/*.lean`.
- If a proof fails, pass the exact Lean error to the next repair attempt.
- If repeated attempts fail, split the theorem into smaller lemmas instead of brute forcing indefinitely.

## Default attempt policy

1. Pythagoras-Prover-4B: 8 attempts.
2. Pythagoras-Prover-4B: increase to 32 attempts if target is important.
3. Goedel-Prover-V2-32B: 8 repair attempts with Lean errors.
4. Goedel-Prover-V2-32B: increase to 32 attempts for high-value targets.
5. DeepSeek/GPT-5.5 planning: use when theorem statement may be poorly decomposed or model attempts repeat the same failure.

## Promotion process

1. Candidate proof found in artifact.
2. Human/GPT review checks that the proof is clean and not overfitted.
3. Candidate is moved into the proper `Ecdlp/*.lean` file.
4. `lake build` runs green.
5. The claim is added to `VERIFIED.md`.

## Current priority

Build a reliable pipeline before scaling attempts:

- stable prompts
- target queue
- artifact-only proof search
- clear attempt budgets
- manual promotion into verified files
