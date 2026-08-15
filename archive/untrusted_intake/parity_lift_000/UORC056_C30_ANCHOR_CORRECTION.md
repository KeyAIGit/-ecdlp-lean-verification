# UORC-056 C30 correction: the oriented anchor is public

The canonical normalization already supplies one public branch-sensitive anchor:

```text
Y_G(x(G))=-y(G).
```

Therefore the unresolved problem after C30 is not creation of the first oriented seed. It is nonlocal propagation of this known anchor to an arbitrary public query `Q=[k]G` without an orbit walk, dense branch table, hidden scalar index, full dual phase, or square-root-width state.

The C30 local normal-form theorem remains unchanged:

```text
C=E+O*Y_G.
```

A nonunit `O` loses the branch on a component; a unit `O` makes `C` locally equivalent to the already selected branch. The theorem classifies local re-encodings. It does not erase or deny the canonical anchor at `G`.

Accordingly, interpret the earlier machine flag

```text
public_oriented_seed_found=false
```

as the narrower statement

```text
subroot_nonlocal_anchor_propagation_found=false.
```

The corrected successor is:

```text
PUBLIC-ANCHOR-NONLOCAL-PROPAGATION-081.
```

No parity evaluator or sub-square-root ECDLP algorithm is claimed.
