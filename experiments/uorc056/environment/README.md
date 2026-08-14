# Optional SageMath environment

This environment is for discovery and independent replay, not the proof trust
root.  Create it only on a machine with enough disk space:

```bash
mamba env create -f experiments/uorc056/environment/environment.yml
mamba activate uorc056-sage
sage experiments/uorc056/sage/uorc056_replay.sage
```

The repository does not vendor SageMath binaries.  Lean remains the formal
verification layer; the required lightweight second backend for this package is
SymPy.
