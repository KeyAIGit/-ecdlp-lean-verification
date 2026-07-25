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
target. The special slice `xT=0` is fixed by diagonal scaling and is recorded
separately from the generic statement.

The producer first works in `Z[b,beta]/(beta^3-1)`, as requested, and then
independently reduces the same tables in the primitive component
`Z[b,beta]/(beta^2+beta+1)`. This prevents the `beta=1` component from hiding a
primitive-root identity. It also checks every scaling after exact
specialization to secp256k1's `p`, `b=7`, and GLV `beta`.

For the elliptic GLV interpretation, `beta` is primitive, `b != 0`, and the
field characteristic is neither 2 nor 3. These are the nondegeneracy
assumptions for the short Weierstrass family. The positive diagonal polynomial
identities themselves need only `beta^3=1` in a commutative ring.

## Frozen result

| Polynomial | Coordinatewise scalings | Primitive-root semi-invariants | Generic fixed-target scalar covariances | Rejected scalar covariances |
|---|---:|---:|---:|---:|
| `S3` | 27 | 3 diagonal | 1 (identity) | 24 |
| `S4` | 81 | 3 diagonal | 1 (identity) | 78 |

For `S3`, diagonal exponents `0`, `1`, and `2` have unit characters
`1`, `beta`, and `beta^2`, respectively. For resultant-defined `S4`, all three
diagonal actions leave the polynomial exactly equal. In both cases the two
nonidentity diagonal actions move the generic target fiber.

For `F_r(x1,x2,x3) = S4(x1,x2,x3,r)`, the exact transport law is

```text
F_r(beta^t*x1,beta^t*x2,beta^t*x3) = F_(beta^(-t)*r)(x1,x2,x3).
```

Equivalently, diagonal scaling maps the fiber for `r` to the fiber for
`beta^t*r`. It preserves a single generic target only for `t=0`; when `r=0`,
the full diagonal `C3` preserves the slice.

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

This package exactly classifies the requested groups `H3` and `H4`, whose
definition requires scalar polynomial covariance. A rejected scaling is not a
certified scalar covariance. That statement alone does not classify every
possible automorphism of the geometric zero variety; such a stronger claim
would need a radical or absolute-irreducibility bridge not proved here.

This is a polynomial identity and target-fiber transport certificate. It does
not test an attack, establish a relation-generation speedup, measure Groebner
complexity, or make any claim about solving secp256k1 ECDLP.
