# TASK-025 infinity-propagation certificate

This directory binds a non-run certificate to:

```text
Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean
```

The source propagates the affine coordinates forced next to isolated infinity
slots. Under explicit nonvanishing assumptions, the exact logical mask counts
are:

```text
377 -> 129 -> 69
         \-> 60
combined -> 36
```

The 129 masks forbid infinity pairs at distance two. The 69 masks also forbid
pairs at distance three. The independent 60-mask branch starts from 129 and
removes boundary-near slots 1 and 12. Combining both refinements leaves 36
logical masks.

The source also proves one-way frozen-resultant propagation over the original
base field. Twelve prefix obstructions can conditionally remove all internal
infinity slots. A balanced form uses six prefix and six suffix obstructions,
all at frozen stages zero through five. Together with the two endpoint
determinant assumptions, their nonvanishing makes the exact chart cover and
literal chart-polynomial cover equivalent to the one empty-mask affine chart.

The final source-stage bridge uses the existing injective map into an
algebraically closed target `K`. Its affine-input, endpoint, and balanced
regularity assumptions are assumptions about the mapped inputs and target in
`K`. A source-field computation is not claimed to establish those mapped
regularity assumptions automatically, and target witnesses are not claimed
to descend to the source field.

This is a conditional representation theorem. It does not prove that the
regular locus is nonempty or generic, that any retained nonempty mask is
realizable, or that the affine chart has a unique witness. It does not run a
solver, enumerate the production mask family, estimate relation yield or
rank, price solving or recovery, search a target, or change ECDLP complexity.

The independent validator:

- derives 377, 129, 69, 60, and 36 by a gap recurrence without materializing
  the production mask family;
- exhausts the distance-two, distance-three, and two boundary implications
  over `F5`, `F7`, and `F11`;
- exhausts reduced stage-one prefix and suffix implications and
  first/third `HValue` symmetry over those fields;
- checks the balanced six-plus-six slot partition and stage bound;
- binds the exact source and upstream SHA-256 digests;
- rejects semantic mutations and forbidden proof placeholders.

`F7` is used only as a raw `HValue` polynomial identity fixture:
characteristic seven is singular for the curve `y^2 = x^3 + 7`. The `F5` and
`F11` checks are the nonsingular finite-field structural fixtures. None of
these bounded fixtures proves symbolic nonzeroness, nonemptiness of the full
regular locus, or genericity.

Run:

```text
python3 experiments/engine/pkc_smooth_m16_infinity_propagation/validate.py \
  --require-final-source-binding
python3 experiments/engine/pkc_smooth_m16_infinity_propagation/test_validate.py
(cd experiments/engine/pkc_smooth_m16_infinity_propagation && \
  sha256sum -c artifact.sha256)
```
