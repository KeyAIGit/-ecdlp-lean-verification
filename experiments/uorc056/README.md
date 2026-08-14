# UORC-056 execution package 001

This directory implements milestones 01-23 of the frozen UORC-056
specification. It contains exact oriented-root ground truth, bounded circuit
synthesis, divisor-aware transfer screens, small Miller experiments and a
provisional theorem-level Fourier-to-divisor barrier.

It does not construct a fast unknown-scalar evaluator and does not claim an
ECDLP improvement.

The central target is unchanged:

```text
A(E,G,Q) = Y_G(x(Q))/y(Q) = (-1)^k,
Q = [k]G,
```

with preprocessing, advice, representation, memory and online cost all
charged.

## Canonical oriented root

For `H=<G>` of odd prime order `n`, let

```text
K_H(X) = product_{j=1}^{(n-1)/2} (X - x([j]G)).
```

The canonical oriented root is the unique polynomial of degree below
`(n-1)/2` satisfying

```text
Y_G(x([j]G)) = (-1)^j y([j]G).
```

Therefore

```text
Y_G(X)^2 = X^3 + aX + b mod K_H(X),
Y_G(x([k]G))/y([k]G) = (-1)^k,
Y_{-G} = -Y_G.
```

In particular, `Y_G(x(G))=-y(G)`. The opposite sign at `G` would use the
opposite global normalization.

## Exact ground truth

The exact factory uses five frozen prime-order subgroups on `y^2=x^3+7`.

| Field | Generator | Prime order | Kernel degree |
|---:|---|---:|---:|
| 43 | `(2,12)` | 31 | 15 |
| 67 | `(2,22)` | 79 | 39 |
| 79 | `(1,18)` | 67 | 33 |
| 127 | `(1,32)` | 127 | 63 |
| 163 | `(2,34)` | 139 | 69 |

For every nonzero marked generator `[u]G`, the factory constructs the exact
oriented root and verifies the square congruence, all parity ratios, generator
negation and the declared CM/GLV relations. This gives 438 checked oriented
roots. SymPy independently replays the group and polynomial arithmetic. A
SageMath 10.9 replay is also supplied.

## Bounded circuit screens

The first affine-character synthesizer rediscovers a minimum weight-four finite
identity on `p=43`, but the unchanged formula is undefined on the other four
frozen orbits. It is a finite interpolation seed, not a uniform evaluator.

The structural transfer grammar admits public coordinates of `[u]Q` for
`u in {1,2,3,4}`, both canonical CM roots, public generator-derived
coefficients, affine combinations and a uniform output phase. On the five
frozen curves it gives 605 semantic vectors and no exact product through weight
four. On the extended 18-curve corpus with 7,434 nonzero points it gives 129
semantic vectors and again no exact product through weight four.

## Divisor-aware screens

These profiles retain every exceptional point. They compute exact local orders
and leading coefficients and admit a ratio only after symbolic cancellation.
No zero is dropped and no target-indexed patch value is allowed.

| Stage | Atom family | Discovery semantic vectors | Full semantic vectors | Exact circuit |
|---|---|---:|---:|---|
| V1 | `L_num(Q)/L_den(Q)` | 103 | 21 | none through weight 4 |
| V2 | `L_num([u]Q)/L_den([u]Q)` | 406 | 78 | none through weight 4 |
| V3 | `L_num([u]Q)/L_den([v]Q)` | 1,693 | 354 | none through weight 4 |
| V4 | `(L1L2)(Q)/(L3L4)(Q)` | 1,186 | 32 | none through weight 4 |

V4 permits aggregate cancellation across two line factors. Its exact discovery
catalog contains 64,980 unordered line products, 31,375 valuation signatures,
48,204 semantic product profiles and 104,855 admissible balanced ratios. It
introduces 429 discovery-only exceptional sign vectors, but no exact parity
circuit. On all 18 curves, exceptional novelty falls to zero.

## Global pulled-line balance

The global balance package permits cancellation across four independently
pulled affine lines:

```text
chi((L1([u1]Q)*L2([u2]Q))/(L3([u3]Q)*L4([u4]Q))).
```

It quotients 1,440 raw pulled-line templates to 1,280 exact local semantics,
checks 819,840 unordered pairs and records 769,563 unique pair semantic states.
No exact two-by-two globally balanced parity circuit exists in the declared
family. The best balanced one-by-one result matches 256/438 points.

## Small Miller balance

The small Miller package uses canonical public addition factors

```text
g_(a,b)([u]Q)
 = ell_([a]G,[b]G)([u]Q) / v_([a+b]G)([u]Q),
```

with signed marks from `{-4,-3,-2,-1,1,2,3,4}`, pullbacks
`u in {1,2,3,4}`, exponents `+1,-1`, at most four primitives and one public
phase.

The quotient contains 128 Miller primitives, 256 signed atoms and 33,152 pair
states. No exact divisor-balanced parity circuit exists through four
primitives. The best regular result through two factors matches 237/438.

This closes bounded small Miller products, not long index-growing Miller or EDS
chains.

## Fourier barrier history

V7 proved the exact parity Fourier peak and isolated a Kummer-Lang hybrid trace
bound, called FDB-1, as a proof obligation. Its conditional checkpoint remains
in the repository for audit history.

V8 resolves that obligation under the standard rank-one sheaf framework and
also removes the cofactor-one restriction.

## V8: regularized subgroup Fourier-to-divisor barrier

Let `E/F_q` be an elliptic curve over an odd finite field and let

```text
H=<G> subset E(F_q),     |H|=n,
```

where `n>=3` is odd. For `f in F_q(E)^*`, define

```text
S_odd(f)={P in E(Fbar_q): ord_P(f) is odd},
s(f)=#S_odd(f).
```

Assume an evaluator agrees with the quadratic character of `f` away from the
divisor, may use arbitrary unit-modulus regularized values at rational odd
support points, and satisfies

```text
lambda_f([k]G)=(-1)^k,     1<=k<n.
```

The provisional theorem gives

```text
cot(pi/(2n)) <= s(f)*sqrt(q)+s(f)+1,
```

hence

```text
s(f) >= (cot(pi/(2n))-1)/(sqrt(q)+1),
deg(f:E->P^1) >= ceil(s(f)/2).
```

When `n` is comparable to `q`, both odd divisor support and rational-map degree
are `Omega(sqrt(n))`.

### Proof kernel

1. Canonical parity has a Fourier coefficient of exact magnitude
   `cot(pi/(2n))` at either near-half frequency.
2. Every character of `H` extends to `E(F_q)`.
3. The indicator of `H` is the average over its annihilator `H^perp`, reducing
   the subgroup sum to complete elliptic sums.
4. Every extended peak character remains faithful of odd order on `H`.
5. Its Lang local system therefore cannot be cancelled by the order-at-most-two
   quadratic Kummer local system.
6. On `U=E-S_odd(f)`, the tensor is rank one, tame, pure of weight zero and
   geometrically nontrivial.
7. Grothendieck-Ogg-Shafarevich gives `dim H_c^1=s(f)`.
8. The trace formula and Deligne weights give the sharp complete-sum bound
   `s(f)*sqrt(q)`.
9. Divisor-aware replacement changes at most `s(f)` rational odd-support terms,
   and omission of the identity contributes at most one more.

Products and quotients of quadratic-character atoms collapse to one rational
function, including exact local regularization. V8 therefore subsumes the
bounded affine, pulled-line, reducible-conic, global-balance and small-Miller
character families at the level of odd divisor support.

### Certified secp256k1 consequence

The machine artifact uses the elementary rational inequality

```text
cot(pi/(2n)) > (98*n^2-121)/(154*n)
```

and exact integer square comparisons. For the public secp256k1 parameters it
certifies

```text
s(f) >= 216543324404233567658511113820216134562,

deg(f) >= 108271662202116783829255556910108067281.
```

The support lower bound has binary size 127.

### Claim boundary

V8 is a provisional theorem-level result assembled from standard sheaf
results, with executable arithmetic checks. Independent specialist review and
formalization remain pending.

It is a divisor-support and rational-map-degree barrier, not a general
arithmetic-circuit lower bound. A short program may define a high-degree
function with square-root-scale support.

## Files

- `uorc056_contract.json`: frozen target and all-in cost model.
- `closed_classes.json`: scoped no-go registry.
- `execution_status.json`: machine-readable milestone state.
- `expected_fixture_manifest.json`: deterministic fixture hashes.
- `circuit_*`, `structural_transfer_*`: bounded affine and structural screens.
- `divisor_aware_*`: exact V1-V4 local-regularization screens.
- `global_divisor_balance_*`: independently pulled global cancellation.
- `small_miller_balance_*`: bounded public Miller factors.
- `fourier_divisor_barrier_*`: historical V7 conditional checkpoint.
- `parity_spectrum_barrier_*`: independent full-group spectral replay.
- `regularized_fourier_divisor_barrier_results.json`: canonical V8 arithmetic artifact.
- `../../scripts/uorc056_regularized_fourier_divisor_barrier.py`: V8 generator.
- `../../notes/reviews/UORC056_REGULARIZED_FOURIER_DIVISOR_BARRIER_V8.md`: V8 proof note.
- `sage/uorc056_replay.sage`: optional Sage replay.

## Reproduce

From the repository root:

```bash
rm -rf /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures --check
cmp /tmp/uorc056-fixtures/manifest.json experiments/uorc056/expected_fixture_manifest.json

PYTHONPATH=scripts python3 -m unittest -v \
  scripts/test_uorc056_toy_factory.py \
  scripts/test_uorc056_circuit_synth.py \
  scripts/test_uorc056_structural_transfer.py \
  scripts/test_uorc056_divisor_aware_rational.py \
  scripts/test_uorc056_divisor_aware_pullback.py \
  scripts/test_uorc056_divisor_aware_mixed_pullback.py \
  scripts/test_uorc056_divisor_aware_balanced_product.py \
  scripts/test_uorc056_global_divisor_balance.py \
  scripts/test_uorc056_small_miller_balance.py \
  scripts/test_uorc056_fourier_divisor_barrier.py \
  scripts/test_uorc056_parity_spectrum_barrier.py \
  scripts/test_uorc056_regularized_fourier_divisor_barrier.py

python3 scripts/uorc056_sympy_replay.py /tmp/uorc056-fixtures
python3 scripts/uorc056_circuit_synth.py --check
python3 scripts/uorc056_structural_transfer.py --check
python3 scripts/uorc056_divisor_aware_rational.py --check
python3 scripts/uorc056_divisor_aware_pullback.py --check
python3 scripts/uorc056_divisor_aware_mixed_pullback.py --check
python3 scripts/uorc056_divisor_aware_balanced_product.py --check
python3 scripts/uorc056_global_divisor_balance.py --check
python3 scripts/uorc056_small_miller_balance.py --check
python3 scripts/uorc056_fourier_divisor_barrier.py --check
python3 scripts/uorc056_parity_spectrum_barrier.py --check
python3 scripts/uorc056_regularized_fourier_divisor_barrier.py --check
```

## Current frontier

The central remaining gap is now degree-to-cost, not another bounded divisor
dictionary.

A surviving evaluator must either:

1. build a rational function with square-root-scale odd divisor support from a
   sub-square-root straight-line program;
2. evaluate `Y_G(x(Q))/y(Q)` directly without reducing to one quadratic
   character;
3. use a compact high-degree Miller, EDS, theta or elliptic-unit representation;
4. use transposed or modular-composition machinery that avoids materializing
   the divisor;
5. use branching or another non-character output model.

The next high-leverage task is to prove a degree-growth versus all-in circuit
cost theorem for pullbacks, Miller chains and division-polynomial recurrences,
or to construct a counterexample that produces square-root divisor support
with genuinely sub-square-root representation and evaluation cost.

## Scientific boundary

The package now contains exact finite ground truth, bounded mechanism closures
and a provisional asymptotic divisor-support theorem. It does not contain a
uniform parity evaluator, a general circuit lower bound or a sub-square-root
ECDLP algorithm.
