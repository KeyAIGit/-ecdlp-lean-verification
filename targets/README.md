# Formal target queue

This directory describes targets for the proof-search agent.

A target is not a vague idea. A target is an atomic theorem/lemma candidate with:

- name
- Lean statement/stem
- why it matters
- difficulty
- default attempt budget
- current status

## Status values

- `todo`: not attempted yet
- `searching`: model attempts are being run
- `candidate_found`: Lean accepted a candidate in an artifact, but it has not been promoted
- `verified`: merged into `Ecdlp/*.lean`, `lake build` green, listed in `VERIFIED.md`
- `blocked`: target likely needs decomposition or statement revision

## Promotion rule

A target becomes `verified` only after:

1. candidate proof appears in an artifact
2. proof is reviewed
3. proof is moved into the verified proof base
4. `lake build` is green
5. `VERIFIED.md` is updated

## Model roles

- Pythagoras-Prover-4B: cheap first-pass generator
- Goedel-Prover-V2-32B: heavy repair / difficult proof attempts
- DeepSeek: optional planner and theorem decomposition assistant
- GPT-5.5: chief engineer / proof review / strategy
