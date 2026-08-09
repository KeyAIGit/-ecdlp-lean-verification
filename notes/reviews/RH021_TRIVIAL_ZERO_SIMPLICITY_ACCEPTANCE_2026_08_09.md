# RH-021 trivial-zero-simplicity contract acceptance record

Date: 2026-08-09

Status: **FINAL — ACCEPT WITH APPLIED PROOF-PLAN AND API FIXES; zero
blocking findings.**

## Reviewed baseline and exact objects

- repository `main` at
  `ba46b13ed6003c216176b72bd565dd4947f75826`;
- pinned Lean version 4.31.0 and Mathlib revision
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`;
- technical-review candidate after the mathematical/API proof-plan repairs
  and before the final packaging/import audit: 491 lines, SHA-256
  `04480e25046c566b51323ae830c8d371154fc845c173ce46d4108064ad9b8abb`,
  Git blob `a7188c2d956ca26eb1b7394616cd8eb92672c9cf`;
- final accepted
  `domains/riemann-hypothesis/TRIVIAL_ZERO_SIMPLICITY_CONTRACT.md`: 496
  lines, SHA-256
  `06b414de60a0e11c1bf4d15c867f10ce0f6d655f9d747dd74d495dcbc0232812`,
  Git blob `99bbcca8bafbdf63c7dd74f6817acb6bce66bf78`.

The candidate and final objects differ only in the title/status paragraph and
five direct-import lines added when the final packaging lens found that the
explicit-import promise still relied transitively on supplier modules for the
functional equation, local-order laws, affine derivative helpers,
cpow-nonvanishing and Gamma-nonvanishing. The final object records the
independent decision made here and directly imports all five modules. No
statement, proof plan, locator, obligation or claim boundary changed after the
technical lenses returned ACCEPT.

The exact four-declaration surface was reproduced by taking the first `lean`
fence below each of the T1, T2, T3 and T4 headings in contract section 2,
removing the fence lines, joining the four UTF-8 records in order with one
blank line, and omitting the final line feed. Its SHA-256 is
`5dbc69c6443a383d562da35d37955b9001563e63c89227c9cf5e3ced90ff858f`.
The extraction contains exactly four `theorem` openers, zero definitions and
zero additional public declarations.

No Lean file was created and no Lean toolchain was run for this acceptance.
This record is source/API review of a frozen statement surface, not a kernel
verdict.

## Authority and effect

`RH-021` authorizes only contract design and independent acceptance. This
record therefore:

- accepts exactly four proposed root-level theorem signatures;
- authorizes a later, separate drafts-lane transcription and static review;
- does not authorize a built module or promotion in the same task;
- adds no import, ledger row, registry entry, axiom-audit row or barrier
  evidence;
- selects no RH route and supplies no evidence for or against
  `_root_.RiemannHypothesis`.

The result under design is a small zeta theorem: every negative-even trivial
zero has local analytic order one. `S1-GLOBAL-ZEROS` and `S1-GROWTH` remain
OPEN and all RH routes remain PARKED. Acceptance changes no barrier row.

## Independent review panel

Three separate lenses were applied to the complete final contract.

1. **Mathematical-truth lens.** Re-derived the four implications, the
   positive-odd/negative-even point arithmetic, the simple cosine zero, the
   five-factor order sum and the affine transport. It independently rejected
   a pointwise functional equation as insufficient and required a genuine
   neighbourhood equality.
2. **Pinned-API fidelity lens.** Re-opened the load-bearing declarations at
   the exact Mathlib pin and the built repository wrapper, checked namespace,
   binder and conclusion shapes, scanned every proposed name in pinned
   Mathlib and the repository, and verified that all directly consumed APIs
   appear in the proposed import list.
3. **Governance and claim-boundary lens.** Audited the one-task queue rule,
   anti-inflation surface, two-stage gate, `analyticOrderAt` junk branches,
   finding A7 history, route/barrier neutrality and exact minimal file scope.

All three lenses return **ACCEPT**. Blocking findings after applied fixes:
**zero**.

## Decision: **ACCEPT WITH APPLIED PROOF-PLAN AND API FIXES**

All four statements are mathematically sound as written and form a sufficient,
anti-inflation surface. No declaration name, binder, hypothesis, point or
conclusion changed during review. The fixes below changed only the explanatory
derivation, import plan and review lifecycle status.

| Lens | Final verdict | Blocking findings | Surface changes |
|---|---|---:|---:|
| Mathematical truth | **ACCEPT** | 0 | 0 |
| Pinned API fidelity | **ACCEPT** | 0 | 0 |
| Governance / claim boundary | **ACCEPT** | 0 | 0 |

## Applied findings and dispositions

### F1 — Composite cosine derivative, applied

The feasibility note mentioned `Complex.deriv_cos'`, which differentiates
`cos` itself and does not by itself prove the derivative of
`s ↦ cos (π * s / 2)`. The contract now requires
`HasDerivAt.ccos` after constructing the inner derivative with
`hasDerivAt_const_mul` and `HasDerivAt.div_const`. The essential chain factor
`π / 2` is explicit and must be proved nonzero.

### F2 — Analyticity cannot come from one complex derivative, applied

An initial T3 plan attempted to obtain analyticity of the cpow, Gamma and zeta
cofactors from isolated `DifferentiableAt` facts. That implication is invalid
over the complex numbers without neighbourhood/global differentiability.
The accepted plan now requires:

- a global `Differentiable` cpow family followed by
  `Differentiable.analyticAt`;
- `DifferentiableOn` Gamma on the open right half-plane followed by
  `DifferentiableOn.analyticAt` at the positive odd point; and
- the pinned neighbourhood theorem `analyticOn_riemannZeta` for zeta.

This is a load-bearing mathematical correction to the proof plan, with no
change to any theorem statement.

### F3 — T2 does not export its proof-local analyticity witness, applied

T2 exports only an `analyticOrderAt = 1` equality. Its internal `AnalyticAt`
witness is not available to T3. The accepted T3 plan explicitly rebuilds
analyticity of `s ↦ cos (π * s / 2)` from `Complex.analyticAt_cos` and the
inner affine map, while consuming only T2's order equality.

### F4 — Explicit-import promise completed, applied

The final proposed import list directly names the modules supplying the built
reflection wrapper, functional equation, zeta nonvanishing, complex Cauchy
theorem, local-order laws, affine derivative helpers, trigonometric
zero/identity/derivative APIs, cpow differentiation/nonvanishing and Gamma
differentiation/nonvanishing. The following previously transitive dependencies
are now explicit:

- `Mathlib.Analysis.Complex.CauchyIntegral`;
- `Mathlib.NumberTheory.LSeries.RiemannZeta`;
- `Mathlib.Analysis.Analytic.Order`;
- `Mathlib.Analysis.Calculus.Deriv.Mul`;
- `Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic`;
- `Mathlib.Analysis.SpecialFunctions.Trigonometric.Complex`;
- `Mathlib.Analysis.SpecialFunctions.Pow.Complex`;
- `Mathlib.Analysis.SpecialFunctions.Gamma.Beta`.

### F5 — Review lifecycle status, applied

During review the document was labelled proposed and did not claim that a
future acceptance record already existed. Only after the mathematical and API
lenses returned ACCEPT was the final title/status changed to accepted and
this record added atomically.

## Statement disposition

| ID | Declaration | Disposition |
|---|---|---|
| T1 | `riemannZeta_comp_one_sub_eventuallyEq_functionalEquation` | **ACCEPT.** The open neighbourhood `1 < re s` excludes every functional-equation exceptional point, so the pinned pointwise identity lifts to the required `EventuallyEq`. |
| T2 | `analyticOrderAt_cos_pi_mul_div_two_at_two_mul_nat_add_three` | **ACCEPT.** The cosine vanishes at `2n+3`, the full composite derivative is `-sin(…) * (π/2)`, and cosine-zero implies sine is `±1`; analyticity plus nonzero derivative gives order one. |
| T3 | `analyticOrderAt_riemannZeta_comp_one_sub_at_two_mul_nat_add_three` | **ACCEPT.** The constant, cpow, Gamma and zeta cofactors are analytic and nonzero; the cosine has order one; local congruence and repeated product laws give `0+0+0+1+0=1`. |
| T4 | `analyticOrderAt_riemannZeta_neg_two_mul_nat_add_one` | **ACCEPT.** The built affine-reflection wrapper transports T3 from `2n+3` to `-2(n+1)` after beta-safe point normalisation. |

## Load-bearing pinned checks

The panel directly checked the following declarations and roles at Mathlib
commit `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`:

- `riemannZeta_one_sub`, including both exceptional-point hypotheses —
  `Mathlib/NumberTheory/LSeries/RiemannZeta.lean:176-178`;
- `analyticOn_riemannZeta` — the same file at `:144-145`;
- `riemannZeta_ne_zero_of_one_le_re` —
  `Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410-414`;
- `Complex.cos_eq_zero_iff` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Complex.lean:33`;
- `Complex.cos_eq_zero_iff_sin_eq` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:1015-1016`;
- `HasDerivAt.ccos` —
  `Mathlib/Analysis/SpecialFunctions/Trigonometric/Deriv.lean:150-152`;
- `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero`,
  `analyticOrderAt_congr`, `analyticOrderAt_mul`, and the analytic/nonzero
  order-zero law — `Mathlib/Analysis/Analytic/Order.lean:328`, `:175`,
  `:497`, and `:133`;
- `Differentiable.analyticAt` and `DifferentiableOn.analyticAt` —
  `Mathlib/Analysis/Complex/CauchyIntegral.lean:625-650`;
- cpow differentiation/nonvanishing —
  `Mathlib/Analysis/SpecialFunctions/Pow/Deriv.lean:111-113` and
  `Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:49-51`;
- Gamma differentiation/nonvanishing —
  `Mathlib/Analysis/SpecialFunctions/Gamma/Deriv.lean:65-83` and
  `Mathlib/Analysis/SpecialFunctions/Gamma/Beta.lean:453-456`;
- built `analyticOrderAt_comp_const_sub` —
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean:128-169`.

The four proposed declaration names have zero declaration matches in baseline
`main` at `ba46b13` and zero matches in pinned Mathlib. Final-package
non-declaration occurrences are confined to this record and the queue closure.
No pinned theorem already states the accepted all-`n` result.

## Exceptional-point and junk-value verdict

At `s₀ = 2n+3`, every point of the chosen neighbourhood avoids `1` and all
nonpositive integers; zeta and Gamma are analytic there. At the base point,
the constant, cpow, Gamma and zeta factors are nonzero. The cosine is analytic,
zero and has nonzero derivative. Thus none of the five order calculations
uses the nonanalytic junk value `0` or the locally-zero value `⊤`.

At `z₀ = -2(n+1)`, zeta is analytic because `z₀ ≠ 1`. The built affine map
has derivative `-1 ≠ 0`, so its order transport is legitimate. T4 states
order exactly one and therefore excludes both junk branches; the known value
zero alone is never treated as simplicity evidence.

## Finding A7 and claim boundary

Finding A7 in the historical multiplicity package correctly removed an
unpinned `n=0` simplicity assertion from that package. This stage-one
acceptance does **not** supersede A7: no kernel theorem exists yet. The new
contract is a separate package designed to address the gap. Only a later
kernel-green promotion may record that the repository-wide absence has been
filled, while leaving the dated M4/A7 history unchanged.

The accepted surface concerns only the local analytic order of zeta at its
negative-even trivial zeros. It says nothing about nontrivial-zero or xi
simplicity, zero enumeration or counting, growth, Hadamard factorization,
cutoffs, route selection, or RH. It closes no barrier, advances no barrier,
and partially closes no barrier.

## Gate result and next authority

`RH-021` stage-one acceptance is complete. The only authorized successor is a
separate drafts-lane transcription/static-review task for these exact four
signatures. That task may not add a built module, root import, ledger row,
registry entry or kernel claim. Any changed name, binder, hypothesis, point or
conclusion returns the surface to contract review.

A later promotion, if separately activated, must run isolated elaboration,
the full build, no-incomplete-proof and lane-isolation checks, inverse ledger
coverage and both axiom audits on its exact head. Green documentation CI in
this acceptance PR is not a Lean verdict for a theorem that does not yet
exist.
