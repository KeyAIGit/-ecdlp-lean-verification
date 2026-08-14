# UORC-056 execution package 001

This directory implements milestones 01-25 of the frozen UORC-056
specification. It contains exact oriented-root ground truth, bounded circuit
synthesis, divisor-aware transfer screens, a provisional subgroup
Fourier-to-divisor theorem and the resulting division-polynomial or EDS
frontier.

It does not construct a fast unknown-scalar evaluator and does not claim an
ECDLP improvement.

## Central target

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

Every preprocessing, advice, representation, memory and online cost is charged.

For an odd prime-order subgroup `H=<G>`,

```text
K_H(X)=product_{j=1}^{(n-1)/2}(X-x([j]G)),
Y_G(x([j]G))=(-1)^j y([j]G).
```

Thus

```text
Y_G(X)^2=X^3+aX+b mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k,
Y_{-G}=-Y_G.
```

The canonical normalization has `Y_G(x(G))=-y(G)`.

## Exact ground truth

The factory uses five frozen prime-order subgroups on `y^2=x^3+7`.

| Field | Generator | Order | Kernel degree |
|---:|---|---:|---:|
| 43 | `(2,12)` | 31 | 15 |
| 67 | `(2,22)` | 79 | 39 |
| 79 | `(1,18)` | 67 | 33 |
| 127 | `(1,32)` | 127 | 63 |
| 163 | `(2,34)` | 139 | 69 |

The package constructs and verifies 438 marked-generator oriented roots. It
checks every nonzero scalar, the square congruence, generator negation and the
declared CM or GLV relations. SymPy independently replays the group and
polynomial arithmetic. A SageMath 10.9 replay is also supplied.

## Finite circuit and divisor screens

The first affine-character synthesizer rediscovers a minimum weight-four
identity on `p=43`, but the unchanged formula fails transfer. The structural
profile then checks small multiples, public CM coordinates and unchanged
multi-curve formulas on an 18-curve corpus containing 7,434 nonzero points.
No exact circuit appears through product weight four.

The divisor-aware profiles retain every exceptional point and compute exact
local orders and leading coefficients.

| Profile | Atom family | Discovery vectors | Full vectors | Result |
|---|---|---:|---:|---|
| V1 | `L_num(Q)/L_den(Q)` | 103 | 21 | none through weight 4 |
| V2 | `L_num([u]Q)/L_den([u]Q)` | 406 | 78 | none through weight 4 |
| V3 | `L_num([u]Q)/L_den([v]Q)` | 1,693 | 354 | none through weight 4 |
| V4 | `(L1L2)(Q)/(L3L4)(Q)` | 1,186 | 32 | none through weight 4 |

V4 examines 64,980 unordered line products and 104,855 admissible balanced
ratios. Cross-factor cancellation creates 429 new discovery-only exceptional
vectors, but no exact circuit. Their novelty disappears on the full corpus.

The global pulled-line package checks 819,840 unordered pulled-line pairs and
769,563 semantic pair states. No exact two-numerator, two-denominator circuit
exists in that grammar.

The bounded Miller package checks 128 canonical public Miller primitives and
33,152 pair states. No exact divisor-balanced circuit appears through four
primitives.

## V8: regularized subgroup Fourier-to-divisor barrier

Let `H=<G>` be any odd cyclic subgroup of `E(F_q)` of order `n`. For a rational
function `f`, put

```text
s(f)=#{P in E(Fbar_q): ord_P(f) is odd}.
```

Suppose an evaluator agrees with the quadratic character of `f` away from the
divisor, may use unit-modulus regularized values at rational odd-support points,
and satisfies

```text
lambda_f([k]G)=(-1)^k,  1<=k<n.
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

The proof uses the exact near-half Fourier peak of parity, extension of a
subgroup character to `E(F_q)`, annihilator averaging, noncancellation of an
odd-order Lang local system by a quadratic Kummer system,
Grothendieck-Ogg-Shafarevich and Deligne's weight bound. Divisor-aware
regularization contributes at most `s(f)+1` to the trace comparison.

For the public secp256k1 parameters, exact integer arithmetic certifies

```text
s(f) >= 216543324404233567658511113820216134562,
deg(f) >= 108271662202116783829255556910108067281.
```

This is a divisor-support and rational-map-degree barrier, not an unrestricted
arithmetic-circuit lower bound. Independent specialist review and formalization
remain pending.

## V9: division-polynomial and all-index Miller frontier

V9 resolves the first degree-to-cost question left by V8.

### Classical terminal Miller functions

For every positive index `m`,

```text
div(f_(m,P))=m[P]-[mP]-(m-1)[O].
```

Modulo two, its odd divisor support contains at most two points. Therefore V8
excludes a single terminal Miller function for every index, not merely the
bounded small-Miller grammar. An explicit product needs at least

```text
108271662202116783829255556910108067281
```

terminal factors before it can meet the secp256k1 support requirement. This
statement does not cover a recursively shared representation that is not an
explicit product list.

### Division polynomials separate support from circuit cost

When the characteristic does not divide `m`,

```text
div(psi_m)=sum_{T in E[m]-{O}}[T]-(m^2-1)[O].
```

Thus the odd support is `m^2-1` for odd `m` and `m^2` for even `m`. Yet the
standard binary recurrences evaluate `psi_m(Q)` through an `O(log m)` dependency
DAG at a non-2-torsion point.

The smallest even index whose support reaches the V8 secp256k1 threshold is

```text
m_min=14715411119103453974.
```

The exact replay finds only

```text
483 dependency indices,
479 nonbase recurrence nodes,
<=2906 field multiplications,
<=495 additions or subtractions,
1 reusable inversion.
```

Therefore a general implication

```text
large odd divisor support => large straight-line evaluation cost
```

is false. This is a counterexample to that proof strategy, not a parity
evaluator.

### Covariance and EDS reduction

Division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1)psi_m(Q).
```

Consequently:

- odd-index characters are invariant and cannot equal canonical parity;
- even-index characters over `q=1 mod 4` are also invariant and cannot equal
  parity;
- only even indices over `q=3 mod 4` pass the negation gate.

The composition identity

```text
psi_(mk)(G)=psi_m([k]G)*psi_k(G)^(m^2)
```

and `rho_j=chi(psi_j(G))` give

```text
m odd:  chi(psi_m([k]G))=rho_(mk)rho_k,
m even: chi(psi_m([k]G))=rho_(mk).
```

The surviving secp256k1 pure division-polynomial route is therefore exactly

```text
m even,
m >= 14715411119103453974,
k -> rho_(m*k).
```

It is an EDS decimation problem, not an independent Miller mechanism.

### Bounded replay

The exact discovery replay tests all 2,048 even indices through `m=4096` on
438 nonzero points. Of these, 1,897 indices are defined everywhere. No exact
candidate appears. The best result is `m=884`, matching `272/438` points. Each
individual discovery curve also has no exact candidate through `8n`.

This finite result is supporting evidence only. The structural reduction is the
main result.

## Current frontier

The central rational-character problem is now:

```text
Can an even EDS decimation k -> rho_(m*k)
be exactly equal to (-1)^k on a prime-order cycle?
```

The next focused tasks are:

1. derive exact quadratic-character quasi-periodicity of
   `rho_j=chi(psi_j(G))` modulo the order `n`;
2. identify the Ward, elliptic-net or metaplectic cocycle under index
   multiplication by an even `m`;
3. prove or refute the existence of an exceptional `m` on `q=3 mod 4` curves;
4. charge all construction and evaluation costs if a candidate survives;
5. keep direct field-valued `Y_G`, theta, elliptic-unit and non-character
   branches separate.

The frontier is no longer another affine coefficient sweep, a bounded Miller
search or a generic degree lower bound.

## Main files

- `uorc056_contract.json`: target and all-in cost model.
- `execution_status.json`: machine-readable milestone status.
- `expected_fixture_manifest.json`: deterministic fixture hashes.
- `circuit_*`, `structural_transfer_*`: finite circuit screens.
- `divisor_aware_*`, `global_divisor_balance_*`: exact divisor screens.
- `small_miller_balance_*`: bounded Miller screen.
- `regularized_fourier_divisor_barrier_results.json`: V8 arithmetic artifact.
- `division_polynomial_frontier_results.json`: V9 result artifact.
- `../../scripts/uorc056_regularized_fourier_divisor_barrier.py`: V8 generator.
- `../../scripts/uorc056_division_polynomial_frontier.py`: V9 generator.
- `../../notes/reviews/UORC056_REGULARIZED_FOURIER_DIVISOR_BARRIER_V8.md`: V8 proof note.
- `../../notes/reviews/UORC056_FDB1_KUMMER_LANG_PROOF_V8.md`: source-locked V8 sheaf note.
- `../../notes/reviews/UORC056_DIVISION_POLYNOMIAL_FRONTIER_V9.md`: V9 proof note.

## Reproduce

```bash
PYTHONPATH=scripts python -m unittest -v \
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
  scripts/test_uorc056_regularized_fourier_divisor_barrier.py \
  scripts/test_uorc056_division_polynomial_frontier.py

python scripts/uorc056_regularized_fourier_divisor_barrier.py --check
python scripts/uorc056_division_polynomial_frontier.py --check
```

## Scientific boundary

The package contains exact finite ground truth, scoped mechanism closures and
provisional theorem-level barriers. It does not contain a uniform parity
evaluator, recover an unknown scalar, prove a general circuit lower bound or
claim a sub-square-root ECDLP algorithm.
