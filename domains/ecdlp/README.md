# ECDLP corpus manifest

`corpus_manifest.json` is the repository-side index that bridges the external ECDLP source corpus to the decision substrate.

It currently records 56 sources: the preserved 49-source June baseline, a three-source July current-literature delta, and a four-source coverage-gap delta. One April preprint remains in history but is marked superseded by its July replacement. The manifest separates classical plain ECDLP, implementation or auxiliary-input routes, and fault-tolerant quantum resource estimates.

The v1.1 layout keeps the index small and stores immutable history under `corpus_snapshots/`. New audits append a new delta file rather than rewriting prior snapshots.

Run:

```bash
python3 scripts/check_corpus_manifest.py
```

The checker validates registered snapshot paths, counts, source IDs, storage and threat-model vocabularies, artifact hashes, relation targets, reciprocal supersession, provenance links, audit deltas, and the domain-registry link.
