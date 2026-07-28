# TASK-021 frozen projective witness-chain kernel certificate

This directory records a narrow, deterministic, non-run certificate for the
universal projective witness-chain theorem in
`Ecdlp.Proved.FrozenRecursiveProjectiveWitness`.

The Lean kernel checks:

- exact output homogeneity of every actual frozen member `C_(s+2)` at the
  declared degree `2^(s+1)`;
- equality between the declared-degree homogenized predecessor slice and the
  actual universal binary output form;
- exact projective evaluation bridges for the predecessor and local `H`
  operands, including affine representatives and `[1:0]`;
- an all-stage equivalence between vanishing of `frozenC k s` after an
  explicit coefficient map and a left-associated chain of valid projective
  intermediate witnesses;
- the stage-14 `C16` corollary, whose chain has fourteen intermediate
  projective-pair slots and uses leaves `q 0` through `q 15`.

Every intermediate has type `ProjectivePair`, so `[0:0]` is excluded while
`[1:0]` remains permitted. The chain lives in the algebraically closed target
field. No descent to a smaller or base field is asserted.

## Independent replay

`validate.py` uses only the Python standard library. It verifies exact source
and predecessor-certificate digests, declaration bindings, the chain index
schedule, the projective-domain contract, the affine and infinity fixtures,
the non-execution boundary, and the absence of `sorry`, `admit`, custom
`axiom`, or `unsafe` declarations in the new Lean source.

`test_validate.py` rehashes semantic mutations. It changes stage and witness
counts, removes infinity, permits `[0:0]`, changes theorem names or source
digests, removes algebraic closure, and attempts solver/cost promotion. Every
mutation must be rejected.

The Python checks bind and replay the certificate. The universal mathematics
comes from Lean, not from finite fixtures or Python testing.

## Honest boundary

This closes the exact frozen-family `C16` to `C2` projective-chain extraction
left by TASK-020. It does not establish a direct `RecS17 iff GeoCat` theorem,
base-field rationality, `RatCat`, `Recover`, S17 materialization, relation
yield, rank, solving degree, memory, recovery cost, total work, route
promotion, or experiment authorization.

## Verification

```text
lake build Ecdlp.Proved.FrozenRecursiveProjectiveWitness
python3 experiments/engine/pkc_smooth_m16_frozen_projective_witness/validate.py
python3 experiments/engine/pkc_smooth_m16_frozen_projective_witness/test_validate.py
cd experiments/engine/pkc_smooth_m16_frozen_projective_witness
sha256sum -c artifact.sha256
```
