# HYP-TORUS-001 independent audit

- **Date:** 2026-07-31
- **Reviewed item:** draft PR #270, head `b55e3b2c29d1e4015b430ec4826d3f7df4791c94`
- **Threat model:** classical, plain, single target
- **Disposition:** reject the submitted candidate; retain a narrower non-executable research-question seed.

## Executive result

PR #270 contains a useful structural observation but does not contain an
admissible Petit mechanism.

The observation that a subgroup of the norm-one torus can be mapped to `F_p`
through `alpha + alpha^-1` is confirmed prior art, not a new mechanism.
Yokota, Kudo and Yasuda already give the `p+1` root-of-unity trace construction
in WCC 2017 Section 4.1, equations (9)-(10). Their low-degree experimental
specialization uses `N=2^r` and `m=2`. The missing step in PR #270 is a
source-checked extension from that construction to its large-prime orders,
including a faithful low-degree presentation, recovery and cost.

The proposed `m=6,7` window chooses a subgroup of order
`45422601869677`. That number is prime. Under PKC 2016 Section 3.3's direct
factor-chain construction, it forces one map of degree `45422601869677`.
Calling the subgroup large is correct; calling the resulting presentation a
smooth low-degree mechanism is not supported.

## Findings

### P0: the mechanism is confirmed prior art

Current `main` already contains the full-text claim
`SC-WCC2017-PPLUS1-TRACE-EXTENSION` and its source extract. The source builds a
factor-base coordinate set from roots of unity in the quadratic extension and
the field trace when `p+1` has a suitable smooth factor. Therefore the memo's
"never examined" classification is false, and absence from its original
branch context cannot be treated as novelty.

What remains potentially new is only a precise secp256k1 large-prime,
arity-specific delta that survives the source's low-degree and recovery
requirements. PR #270 does not provide that delta.

### P0: the low-degree mechanism is absent

The source requires both a sufficiently large root set and a decomposition of
the defining map into low-degree maps. PR #270 checks only the first property.
Its selected order is a 46-bit prime, so the source's factor-chain construction
has a 46-bit prime-degree step. No alternative arithmetic circuit, rational
map, branch accounting or recovery map is specified.

Therefore the claimed `size leg cleared` conclusion is retracted. The correct
state is `rejected_missing_exact_low_degree_mechanism`.

### P1: the arity enumeration is incomplete

Using the memo's own paper-balance predicate

```text
|Tr(H)| >= ceil((m! p)^(1/m))
```

and the exact trace-orbit count, the known divisors produce candidates for
every `m` from 6 through 20 under the memo's size and nominal linear-algebra
screens. The minimum orders are:

| `m` | minimum `|H|` | distinct trace values | largest prime step |
|---:|---:|---:|---:|
| 6-10 | 45422601869677 | 22711300934839 | 45422601869677 |
| 11 | 117154192 | 58577097 | 7322137 |
| 12 | 29288548 | 14644275 | 7322137 |
| 13 | 14644274 | 7322138 | 7322137 |
| 14-20 | 7322137 | 3661069 | 7322137 |

This correction does not improve the candidate: every row still has an
unpriced 23-bit or 46-bit prime-degree step. It does show that the statement
"the window is `m in {6,7}`" was not an exhaustive arithmetic conclusion.

### P1: polynomial degree and distinct-root count were conflated

The trace set is described set-theoretically by the Dickson equation

```text
D_d(x,1) - 2 = 0.
```

For `d=|H|`, this polynomial has degree `d` but only
`(d+gcd(d,2))/2` distinct trace roots. Non-endpoint roots occur with
multiplicity. The factor-base cardinality can use the distinct-root count, but
the polynomial-system cost cannot silently replace the degree-`d`
non-radical equation by a squarefree polynomial of half the degree. Radical,
saturation and recovery semantics must be explicit.

### P2: the classification sentence was too broad

`G_a`, `G_m` and the nonsplit one-dimensional torus classify connected
one-dimensional **affine linear** algebraic groups over a finite field. They do
not classify all connected one-dimensional algebraic groups; elliptic curves
are the missing proper case. This wording cannot support the claim that the
entire mechanism sector has been exhausted.

## Scoped conclusion

Closed:

- PR #270's exact claim that the displayed `p+1` divisor immediately supplies
  a faithful low-degree Petit factor base at `m=6,7`;
- the submitted arithmetic table as an exhaustive window;
- authorization of the proposed solving-degree experiment.

Still open:

- whether a Dickson/Lucas arithmetic circuit can be converted into a faithful
  low-degree relation system with bounded branch growth;
- squarefree or saturated handling of the trace fibers;
- complete point recovery and exceptional components;
- end-to-end relation, linear-algebra and preprocessing cost;
- a concrete large-prime extension and its source-checked delta beyond the
  known WCC 2017 trace construction.

The parent route `R-PETIT-COMPOSED-MAPS` remains `open_parked`. No solver run,
secp256k1 relation search, route promotion, security claim or novelty claim is
authorized.

## Evidence

- `experiments/engine/pkc_nonsplit_torus_desk_screen/artifact.json`
- `experiments/engine/pkc_nonsplit_torus_desk_screen/generate.py`
- `experiments/engine/pkc_nonsplit_torus_desk_screen/validate.py`
- `experiments/engine/pkc_nonsplit_torus_desk_screen/test_validate.py`
- `data/source_claim_extracts/petit_kosters_messeng2016.json`
- `data/source_claim_extracts/yokota_kudo_yasuda2017_wcc.json`

The artifact and replay intentionally leave the 184-bit remaining cofactor's
primality unclaimed; the decisive findings require only the exact product
identity and the independently checked primality of the 23-bit and 46-bit
factors.
