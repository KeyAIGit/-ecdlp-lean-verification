# ECDLP corpus manifest

`corpus_manifest.json` is the repository-side bridge to the external ECDLP source corpus.

It currently records 52 sources: the preserved 49-source June snapshot plus a three-source July literature delta. One April preprint remains in history but is marked superseded by its July replacement. The manifest also separates classical plain ECDLP, implementation or auxiliary-input routes, and fault-tolerant quantum resource estimates.

Run:

```bash
python3 scripts/check_corpus_manifest.py
```

The checker validates counts, source IDs, storage and threat-model vocabularies, artifact hashes, relation targets, reciprocal supersession, audit deltas, and the domain-registry link.
