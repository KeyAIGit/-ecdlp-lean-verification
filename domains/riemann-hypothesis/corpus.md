# Riemann Hypothesis research corpus

Status: **active exploratory research lane** as of 2026-08-04.

This corpus defines what KeyAI may investigate under the Riemann Hypothesis
program. It does not contain a proof, a claimed proof, or evidence that a proof
is close. The exact formal target already exists in the repository's pinned
Mathlib dependency as `_root_.RiemannHypothesis`.

The owning queue is `tasks/RIEMANN_HYPOTHESIS.md`. Existing ECDLP results,
decisions, ledgers, and experiment authorizations are separate and unchanged.

## Exact target and pinned formal baseline

The project pins Mathlib v4.31.0 at commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. At that exact revision:

| capability | declaration or module | current use |
|---|---|---|
| Riemann zeta function | `riemannZeta` | canonical function |
| completed zeta and pole-removed completion | `completedRiemannZeta`, `completedRiemannZeta₀` | analytic baseline |
| functional equation | `completedRiemannZeta₀_one_sub`, `completedRiemannZeta_one_sub`, `riemannZeta_one_sub` | symmetry baseline |
| trivial zeros | `riemannZeta_neg_two_mul_nat_add_one` | excluded-zero baseline |
| exact RH proposition | `_root_.RiemannHypothesis` | canonical target, open |
| zero set | `riemannZetaZeros` | canonical zero-set object |
| closed and discrete zero set | `isClosed_riemannZetaZeros`, `isDiscrete_riemannZetaZeros` | local finiteness baseline |
| compact sets contain finitely many zeros | `IsCompact.inter_riemannZetaZeros_finite` | finite-window bridge |
| no zeros when `1 ≤ re(s)` | `riemannZeta_ne_zero_of_one_le_re` | right half-plane baseline |

Pinned sources:

- `Mathlib/NumberTheory/LSeries/RiemannZeta.lean` at the pinned commit:
  <https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/RiemannZeta.lean>
- `Mathlib/NumberTheory/LSeries/ZetaZeros.lean` at the pinned commit:
  <https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/ZetaZeros.lean>
- `Mathlib/NumberTheory/LSeries/Nonvanishing.lean` at the pinned commit:
  <https://github.com/leanprover-community/mathlib4/blob/fabf563a7c95a166b8d7b6efca11c8b4dc9d911f/Mathlib/NumberTheory/LSeries/Nonvanishing.lean>

Before adding any local RH definition, an agent must show why the Mathlib
declaration is insufficient. Parallel definitions with subtly different zero,
pole, or critical-strip conventions are prohibited.

## Primary-source register

| id | source | role | read state |
|---|---|---|---|
| `RH-SRC-001` | Clay Mathematics Institute, [Riemann Hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/) and Bombieri's [official problem description](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf) | official target, history, significance, classical routes | full official description available |
| `RH-SRC-002` | Clay collection of [Riemann's 1859 manuscript](https://www.claymath.org/collections/riemanns-1859-manuscript/) | original formulation and explicit-formula context | collection and translation available |
| `RH-SRC-003` | Xian-Jin Li, [The Positivity of a Sequence of Numbers and the Riemann Hypothesis](https://www.sciencedirect.com/science/article/pii/S0022314X97921375), 1997 | Li positivity criterion | publisher record available; exact theorem extraction required |
| `RH-SRC-004` | Enrico Bombieri and Jeffrey Lagarias, [Complements to Li's Criterion](https://www.sciencedirect.com/science/article/pii/S0022314X99923922), 1999 | abstract multiset criterion and link to the explicit formula | publisher record available; exact theorem extraction required |
| `RH-SRC-005` | Luis Báez-Duarte, [A strengthening of the Nyman-Beurling criterion](https://arxiv.org/abs/math/0202141), 2002 | Hilbert-space closure criterion | primary preprint available |
| `RH-SRC-006` | Brad Rodgers and Terence Tao, [The de Bruijn-Newman constant is non-negative](https://arxiv.org/abs/1801.05914), 2018 | heat-flow deformation and the lower bound `Λ ≥ 0` | primary preprint available |
| `RH-SRC-007` | Dave Platt and Tim Trudgian, [The Riemann hypothesis is true up to 3·10^12](https://arxiv.org/abs/2004.09765), 2020 | rigorous bounded-height computation | primary preprint available; computational evidence only |
| `RH-SRC-008` | David Loeffler and Michael Stoll, [The Riemann zeta function in Lean](https://arxiv.org/abs/2503.00959), 2025 | formalization conventions, totalization at exceptional points, and exact Mathlib construction | primary preprint available; verify against the pinned code |

Prior formal code to inspect before creating a competing zero-multiplicity,
finite-height, or explicit-formula API:

- [PrimeNumberTheoremAnd](https://github.com/AlexKontorovich/PrimeNumberTheoremAnd),
  especially its zeta definitions and any multiplicity-aware zero objects;
- [Google DeepMind formal-conjectures](https://github.com/google-deepmind/formal-conjectures),
  as a statement comparison only. An open stem or `sorry` is not evidence.

Metadata, abstracts, surveys, and search-result snippets do not count as theorem
extraction. A track may cite a source as mechanistic evidence only after recording
the exact theorem, assumptions, normalization, convergence convention, and page or
section locator.

## Initial claim map

| claim id | statement | status | assurance |
|---|---|---|---|
| `RH-C000` | Every nontrivial zero of the Riemann zeta function has real part `1/2`, using Mathlib's exact exclusions | open target | formal proposition exists; no proof |
| `RH-C001` | The pole-removed completed zeta function is entire and symmetric under `s ↦ 1 - s` | available baseline | pinned Mathlib theorem |
| `RH-C002` | Negative even integers are zeros of `riemannZeta` | available baseline | pinned Mathlib theorem |
| `RH-C003` | `riemannZeta` has no zeros in the closed half-plane `re(s) ≥ 1` | available baseline | pinned Mathlib theorem |
| `RH-C004` | The zeta zero set is discrete and finite in every compact window | available baseline | pinned Mathlib theorem |
| `RH-C010` | RH is equivalent to positivity of all Li coefficients under the source's exact definitions and convergence conditions | source-grounded, not formalized here | primary-source extraction pending |
| `RH-C011` | A Weil-type positivity criterion gives an equivalent test under an exact test-function class and explicit formula | source-grounded, not formalized here | primary-source extraction pending |
| `RH-C012` | RH is equivalent to a Nyman-Beurling or Báez-Duarte closure statement in a specified Hilbert space | source-grounded, not formalized here | primary-source extraction pending |
| `RH-C013` | RH is equivalent to `Λ ≤ 0` for the de Bruijn-Newman constant; known work gives `Λ ≥ 0` | source-grounded, not formalized here | primary-source extraction pending |
| `RH-C014` | RH holds for all zeros in a rigorously certified finite height range | bounded computational result | never global proof evidence |

## Ranked research tracks

The ranking is for the first desk cycle. It is not a claim about the eventual
route to a proof.

| priority | track | why it is admitted now | first decisive question | disposition |
|---:|---|---|---|---|
| 1 | Formal xi, critical-strip, and dependency map | The exact target and several analytic foundations already exist in pinned Mathlib | Can a standard entire xi object and its zero correspondence be represented exactly, including exceptional points and multiplicity, without duplicating or weakening the pinned target? | active |
| 2 | Li and Weil positivity | Positivity converts zero location into inequalities and may expose reusable finite and infinite sublemmas | Can the infinite convergence, logarithm-branch, and explicit-formula obligations be separated into reviewable formal contracts? | desk-screen |
| 3 | Nyman-Beurling and Báez-Duarte closure | The criterion translates RH into approximation in a Hilbert space, a setting with substantial general Lean infrastructure | Does pinned Mathlib support the required weighted `L²`, dilation, fractional-part, Mellin, and closure machinery without changing the statement? | desk-screen |
| 4 | Explicit formula, zero-free regions, mollifiers, and prime-error bounds | This is close to the arithmetic consequences of RH and can produce honest intermediate bounds or a ceiling for a restricted method | Is there a concrete new uniform inequality or a rigorous limit theorem for the chosen ansatz, rather than a repackaging of known bounds? | desk-screen |
| 5 | de Bruijn-Newman heat flow | It gives a sharp deformation framework, but `Λ ≥ 0` means proving RH in this route requires the opposite bound `Λ ≤ 0` | Is there a new monotone or coercive invariant capable of forcing the missing upper bound? | parked pending mechanism |
| 6 | Rigorous zero computation | Interval certificates can validate finite windows and test formal interfaces | Can a producer and independent validator close a specifically preregistered finite claim? | evidence-only |

Exactly one theorem-bearing route may become active after the first desk cycle.
Equivalent restatements are not progress unless they remove a named barrier or
produce a new bound that changes the route decision.

The Stage 0 lane is infrastructure. Subject to the `RH-002` red-team result, the
main direct mathematical bet is Li/Weil positivity. A finite-multiset or
finite-dimensional version may validate definitions, but it changes the route
decision only if it exposes a uniform argument controlling the infinite limit.

## Evidence and claim rules

1. Lean acceptance proves only the encoded statement. Independent review must
   confirm that the encoding matches the cited mathematics.
2. Numerical zero checks, finite positivity checks, and interval certificates are
   bounded computational evidence. No finite cutoff proves RH.
3. Random-matrix analogies, spectral analogies, physics models, and model-generated
   conjectures are heuristics until converted into an exact theorem with a recovery
   path to `_root_.RiemannHypothesis`.
4. A theorem of the form `A → RiemannHypothesis` is not progress unless `A` is
   independently justified and materially easier than RH. Renaming the difficulty
   as an assumption is prohibited.
5. A new equivalent criterion must preserve every regularity, convergence,
   multiplicity, ordering, and test-function hypothesis from its source.
6. Negative results close only the tested statement, representation, or bound.

## Mandatory red-team checks

Reject or return any argument that does one of the following:

- uses the Dirichlet series or Euler product outside its proved convergence region;
- rearranges a conditionally convergent zero sum without a stated ordering or
  convergence theorem;
- takes `log ζ`, divides by `ζ`, or moves a contour through a possible zero or pole
  without discharging the domain and residue obligations;
- ignores the pole at `1`, trivial zeros, zero multiplicity, or gamma factors;
- treats functional-equation symmetry as proof that every zero lies on the symmetry
  line;
- infers an infinite statement from a finite zero or coefficient computation;
- treats a random-matrix, operator, or geometric analogy as an identified operator
  with a proved spectrum;
- discards zero multiplicity because the current Mathlib zero object is a set;
- introduces an assumption equivalent to RH and then advertises the conditional
  implication as a proof;
- converts floating-point output into a sign or zero claim without interval bounds
  and an independently written validator.

## First 90-day exit condition

The activation phase succeeds if the repository produces all of the following:

1. a pinned Mathlib capability and blocker map;
2. exact primary-source extracts for the top three tracks;
3. adversarial dispositions for those tracks;
4. at most one selected theorem candidate with a dependency graph, claim boundary,
   independent review plan, and explicit death condition;
5. either one kernel-checked missing foundation or an honest `PARK` or `STOP`
   decision explaining why none is currently worth formalizing.

Solving RH is not a 90-day acceptance criterion. Reducing uncertainty about the
best next mathematical bottleneck is.
