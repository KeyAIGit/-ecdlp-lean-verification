# M16 factor-base census and regime assurance

This directory records an exact, deterministic census for the published
PKC-2016 `p-1` smooth-subgroup construction specialized to the secp256k1
base field and `D = 564522`.

The producer enumerates the subgroup through its explicit three-element GLV
orbits. It computes the quadratic-character sum for `x^3 + 7`, the number of
factor-base coordinates that lift to affine curve points, actual orbit counts,
and several exact combinatorial, explicitly conditioned null comparators. Large
integers and rationals remain exact; decimal values are derived display fields
only.

The scientific boundary is narrow:

- this is structural/applicability arithmetic, not an ECDLP experiment;
- no Semaev system is built and no solver is run;
- the conditioned comparators do not establish the actual group-sum
  distribution, independence, rank, solving degree, fill-in, recovery cost, or
  total attack cost; uncounted zero-sum configurations may remain;
- the `<=24`-bit classification applies only to the immutable proposal's
  execution regime;
- the M16 mechanism and parent route remain open and non-executable;
- no novelty, authorization, security, or secp256k1 break claim follows.

Generate and replay:

```text
python generate.py
python generate.py --check
python validate.py
python test_validate.py
```

`validate.py` intentionally uses a different subgroup construction and a full
`D`-element enumeration. Source independence remains `not_established`.
