# RH-001 reproducible Mathlib search log

Status: **replay record for the draft capability map**

Audit date: 2026-08-04

## Revision identity

Repository `lake-manifest.json` and the audit checkout both resolve Mathlib to:

```text
fabf563a7c95a166b8d7b6efca11c8b4dc9d911f
```

Reproduction commands:

```bash
python3 - <<'PY'
import json
packages = json.load(open('lake-manifest.json'))['packages']
print(next(p['rev'] for p in packages if p['name'] == 'mathlib'))
PY

git -C /path/to/mathlib4 rev-parse HEAD
git -C /path/to/mathlib4 cat-file -e \
  fabf563a7c95a166b8d7b6efca11c8b4dc9d911f^{commit}
```

Both outputs must equal the revision above before interpreting any result.

## Audited source scope

The negative declaration searches were run over these pinned paths:

```text
Mathlib/NumberTheory/LSeries/
Mathlib/NumberTheory/EulerProduct/
Mathlib/NumberTheory/ArithmeticFunction/VonMangoldt.lean
Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean
Mathlib/Analysis/Analytic/
Mathlib/Analysis/Meromorphic/
Mathlib/Analysis/Complex/
Mathlib/Analysis/MellinTransform.lean
Mathlib/Analysis/MellinInversion.lean
Mathlib/Analysis/SpecialFunctions/Gamma/
Mathlib/MeasureTheory/Function/LpSpace/
Mathlib/MeasureTheory/Function/LpSeminorm/
Mathlib/MeasureTheory/Function/SimpleFuncDenseLp.lean
Mathlib/MeasureTheory/Function/L2Space.lean
Mathlib/Algebra/Order/Floor/
```

This scope covers the pinned zeta implementation and the directly relevant
generic infrastructure. A zero result means `not found in this audited source
scope`, not `mathematically impossible` and not `absent under every possible
name anywhere in Mathlib`.

## Positive declaration replay

Representative exact lookups use the Git object database rather than assuming
that a sparse working tree contains the file:

```bash
PIN=fabf563a7c95a166b8d7b6efca11c8b4dc9d911f

git show "$PIN":Mathlib/NumberTheory/LSeries/RiemannZeta.lean \
  | nl -ba \
  | rg 'RiemannHypothesis|riemannZeta|completedRiemannZeta'

git show "$PIN":Mathlib/NumberTheory/LSeries/ZetaZeros.lean \
  | nl -ba \
  | rg 'riemannZetaZeros|isDiscrete|inter_riemannZetaZeros_finite'

git grep -n -E 'riemannZeta_ne_zero_of_one_(lt|le)_re' "$PIN" -- \
  Mathlib/NumberTheory/LSeries/Dirichlet.lean \
  Mathlib/NumberTheory/LSeries/Nonvanishing.lean

git show "$PIN":Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean \
  | nl -ba \
  | rg 'Gammaℝ_eq_zero_iff|differentiable_Gammaℝ_inv'

git grep -n -E 'analyticOrderAt|meromorphicOrderAt|def divisor' "$PIN" -- \
  Mathlib/Analysis/Analytic/Order.lean \
  Mathlib/Analysis/Meromorphic/Order.lean \
  Mathlib/Analysis/Meromorphic/Divisor.lean

git show "$PIN":Mathlib/MeasureTheory/Function/L2Space.lean \
  | nl -ba \
  | rg 'instance innerProductSpace|GramMatrix'
```

Expected high-value anchors:

| declaration | pinned path and line |
|---|---|
| `completedRiemannZeta₀` | `RiemannZeta.lean:63` |
| `completedRiemannZeta_eq` | `RiemannZeta.lean:84` |
| `differentiable_completedZeta₀` | `RiemannZeta.lean:89` |
| `completedRiemannZeta₀_one_sub` | `RiemannZeta.lean:99` |
| `riemannZeta` | `RiemannZeta.lean:119` |
| `riemannZeta_neg_two_mul_nat_add_one` | `RiemannZeta.lean:171` |
| `_root_.RiemannHypothesis` | `RiemannZeta.lean:182` |
| `riemannZetaZeros` | `ZetaZeros.lean:33` |
| `isDiscrete_riemannZetaZeros` | `ZetaZeros.lean:60` |
| `IsCompact.inter_riemannZetaZeros_finite` | `ZetaZeros.lean:64` |
| `riemannZeta_ne_zero_of_one_le_re` | `Nonvanishing.lean:410` |
| `Gammaℝ_eq_zero_iff` | `Gamma/Deligne.lean:73` |
| `analyticOrderAt` | `Analysis/Analytic/Order.lean:47` |
| `meromorphicOrderAt` | `Analysis/Meromorphic/Order.lean:47` |
| `MeromorphicOn.divisor` | `Analysis/Meromorphic/Divisor.lean:39` |
| `mellin` / `HasMellin` | `Analysis/MellinTransform.lean:91/160` |
| `mellinInv_mellin_eq` | `Analysis/MellinInversion.lean:98` |
| `MeasureTheory.Lp.instCompleteSpace` | `LpSpace/Complete.lean:378` |
| `Lp.simpleFunc.isDenseEmbedding` | `SimpleFuncDenseLp.lean:648` |
| `MeasureTheory.L2.innerProductSpace` | `MeasureTheory/Function/L2Space.lean:192` |
| `Int.fract` | `Algebra/Order/Floor/Defs.lean:259` |

## Replayed negative search matrix

The following command shape was used for each row. Searching the pinned tree
with `git grep` makes the result independent of sparse-checkout contents and
uncommitted working-tree files:

```bash
git grep -i -n -E '<pattern>' "$PIN" -- <audited-source-scope>
```

| pattern | hit count |
|---|---:|
| `riemannXi|Riemann[[:space:]_-]*(xi|ξ)` | 0 |
| `Li coefficient|Li criterion|Keiper` | 0 |
| `Nyman|Beurling|Báez-Duarte|Baez-Duarte` | 0 |
| `Riemann-von Mangoldt|zero counting` | 0 |
| `Hadamard product|canonical product` | 0 |
| `nontrivial zero|critical strip` | 0 |
| `analyticOrderAt[[:space:]]+riemannZeta` | 0 |
| `meromorphicOrderAt[[:space:]]+riemannZeta` | 0 |
| `divisor[[:space:]]+riemannZeta` | 0 |
| `riemannZeta.*(conj|star)|(conj|star).*riemannZeta|completedRiemannZeta.*(conj|star)|(conj|star).*completedRiemannZeta` | 0 |
| `(riemannZeta|completedRiemannZeta).*(vertical|growth|order|isOfOrder)|(vertical|growth|order|isOfOrder).*(riemannZeta|completedRiemannZeta)` | 0 |
| `isBigO.*(riemannZeta|completedRiemannZeta)|(riemannZeta|completedRiemannZeta).*isBigO` | 2 local hits |
| `Riemann.*explicit formula|explicit formula.*(Riemann|zero|prime)|Weil.*explicit formula|Guinand` | 0 |

The two `isBigO` hits are
`isBigO_riemannZeta_sub_one_div` and its proof term in `ZetaAsymp.lean:365-368`.
They describe the local Laurent remainder at `s = 1`, not vertical or
finite-order growth. The broader phrase search `explicit formula` returned six
unrelated hits: one Gauss-Lucas coefficient formula, one beta-function formula,
two Hurwitz-zeta special-value formulae, and two finite-Fourier `ZMod`
L-function formulae. Semantic inspection found arithmetic `vonMangoldt` and
the right-half-plane zeta logarithmic derivative, but no Riemann-Weil
prime-zero explicit formula.

The line-oriented conjugation regex was supplemented by the broader core-file
token check below so that a declaration split across lines could not evade the
replay:

```bash
git grep -i -n -E 'conj|star' "$PIN" -- \
  Mathlib/NumberTheory/LSeries/RiemannZeta.lean \
  Mathlib/NumberTheory/LSeries/ZetaZeros.lean \
  Mathlib/NumberTheory/LSeries/Nonvanishing.lean
```

It also returned zero hits. This strengthens the scoped API search; it remains
an audited-scope claim rather than a claim about every possible equivalent
theorem name in Mathlib.

## Source-code sign trap replay

Inspect both the module header and the proved relation:

```bash
git show "$PIN":Mathlib/NumberTheory/LSeries/RiemannZeta.lean \
  | sed -n '10,26p;58,90p'
```

The top module comment gives the pole correction with the opposite sign from
the inline definition comment. The theorem at line 84 proves:

```text
completedRiemannZeta s
  = completedRiemannZeta₀ s - 1/s - 1/(1-s).
```

Every xi derivation must start from that theorem. Copying the top prose formula
creates the wrong normalized entire function.

## Reviewer replay checklist

An independent reviewer should:

1. verify the repository pin and audit checkout SHA independently;
2. reproduce every positive anchor used by the capability map;
3. rerun the negative matrix over the stated paths;
4. inspect any unexpected hit semantically rather than by filename only;
5. recompute the xi algebra from `completedRiemannZeta_eq`;
6. verify that the proposed zero bridge uses `Gammaℝ_eq_zero_iff` and the exact
   exclusions in `_root_.RiemannHypothesis`;
7. reject any absence claim that is stronger than the audited scope supports.
