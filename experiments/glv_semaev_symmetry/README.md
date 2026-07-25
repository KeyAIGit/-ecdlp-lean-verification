# GLV/Semaev symbolic symmetry certificate

This package is the exact symbolic certificate for `GLV-SEMAEV-ITER-001`.
It classifies every coordinatewise order-three scaling of the third and
fourth Semaev summation polynomials for

```text
E_b: y^2 = x^3 + b
```

The curve parameter `b` remains symbolic throughout.

## Certified objects

The exact third summation polynomial is

```text
S3(x1,x2,x3) =
  (x1-x2)^2*x3^2
  - 2*((x1+x2)*x1*x2+2*b)*x3
  + (x1*x2)^2
  - 4*b*(x1+x2).
```

The fourth polynomial is defined, rather than copied from a formula:

```text
S4(x1,x2,x3,x4) =
  Resultant_z(S3(x1,x2,z), S3(x3,x4,z)).
```

For `S3`, the producer enumerates all `3^3 = 27` substitutions
`xi -> beta^ei*xi`. For `S4`, it enumerates all `3^4 = 81`. Every transformed
polynomial is reduced in

```text
Z[b,beta,x1,...]/(beta^3-1)
```

and compared exactly with `beta^k*Sj` for each `k` in `{0,1,2}`.

The final x-coordinate is designated as the target coordinate. A unit-scalar
polynomial equality with target exponent zero preserves a generic fixed-target
fiber. A full diagonal equality with a nonzero target exponent transports that
fiber to the target's GLV image; it is not a symmetry of one generic fixed
target.

For the geometric GLV interpretation, `beta` is a nontrivial cube root of
unity, the field characteristic is not three, and `b != 0` so the curve is
nonsingular. The polynomial identities themselves are certified over the
displayed integer quotient ring and do not require a numerical field.

## Frozen result

| Polynomial | Coordinatewise scalings | Unit-scalar symmetries | Generic fixed-target symmetries | Rejected |
|---|---:|---:|---:|---:|
| `S3` | 27 | 3 diagonal | 1 (identity) | 24 |
| `S4` | 81 | 3 diagonal | 1 (identity) | 78 |

For `S3`, diagonal exponents `0`, `1`, and `2` have unit characters
`1`, `beta`, and `beta^2`, respectively. For resultant-defined `S4`, all three
diagonal actions leave the polynomial exactly equal. In both cases the two
nonidentity diagonal actions move the generic target fiber.

## Independent replay

`generate.py` uses pinned SymPy for expansion and the defining resultant.
`validate.py` uses only the Python standard library. It reconstructs `S3` with
sparse integer polynomial arithmetic and reconstructs `S4` independently as
the determinant of the quadratic Sylvester matrix. It then recomputes all 108
scaling hashes and classifications.

```bash
python3 -m pip install -r experiments/glv_semaev_symmetry/requirements.txt
python3 experiments/glv_semaev_symmetry/generate.py --check
python3 experiments/glv_semaev_symmetry/validate.py
```

To intentionally regenerate the frozen artifact:

```bash
python3 experiments/glv_semaev_symmetry/generate.py
```

## Claim boundary

This is a polynomial identity and target-fiber classification certificate. It
does not test an attack, establish a relation-generation speedup, measure
Groebner complexity, or make any claim about solving secp256k1 ECDLP.
