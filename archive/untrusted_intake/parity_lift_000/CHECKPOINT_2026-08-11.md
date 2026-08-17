# PARITY-LIFT-000 checkpoint

Date: 2026-08-11
Branch: `research/parity-lift-000`
Draft PR: `#365`
Checkpoint parent head: `0ef47b7fbe32467e6aa94114863a1589e74d6a69`

Status: persistent GitHub checkpoint. This file exists so the research state does
not depend on chat context or temporary container storage.

## Safety and claim boundary

This line is theorem-first and non-executable. It does not target a real public
key, wallet, or production discrete-log instance. It creates no Research Engine
authorization, route promotion, or asymptotic-improvement claim.

## Central question after refinement

A weak canonical coordinate lift from public `(G,Q)` exists through ordinary
piecewise projective chart normalization, but an invertible coordinate change
alone cannot reveal the hidden scalar.

The actual target is an exact public decoder for one generator-relative bit at
less than the matched square-root baseline.

The current best localization is the EDS residue

```text
rho_G(Q) = chi(W_G(k)) = chi(psi_k(G)),   Q = [k]G.
```

For fixed public secp256k1 parameters the recorded bridge is

```text
(-1)^k = chi(phi_raw(Q)) * rho_G(Q).
```

The public sign factor can be evaluated from `Q`. The unresolved hidden part is
therefore `rho_G(Q)`. On secp256k1 the branch derives that this residual bit is
Kummer-invariant, so the surviving candidate can be written as

```text
Given x(Q), compute rho_G(Q)
without first recovering k and below square-root total cost.
```

No unknown-target value is computed in this branch.

## Formal results saved and kernel checked

`Ecdlp/Proved/ScalarParity.lean` contains:

1. `scalarParity_neg`
2. `scalarParity_not_factor_through_Kummer`
3. `no_global_alternating_translation_observable`
4. `parityOracle_recovers_dlog`

`Ecdlp/Proved/EdsResidueBalance.lean` proves the quadratic-exponent balance for
finite products and ratios of fixed-index transported EDS observables.

At checkpoint parent head, GitHub Actions reported success for both:

- `Verify Lean proofs`, run `31550596465`
- `Docs sync`, run `31550596466`

## Main mathematical conclusions saved

1. Direct canonical parity is anti-invariant under `Q -> -Q`, so it cannot
   factor through x-only, Kummer, `y^2`, even-theta, or any sign-erasing orbit
   norm.
2. Exact parity is not an order-two character of an odd cyclic group. It has one
   unavoidable wrap cut.
3. An exact parity oracle recovers the complete canonical scalar through bit
   peeling in at most `ceil(log2 n)` calls.
4. Exact direct parity uses all `n` Fourier frequencies. A fixed globally linear
   translation representation that outputs it requires dimension at least `n`.
5. A fixed theta space admitting globally linear translation by an order-`n`
   generator likewise requires line-bundle degree and section dimension at
   least `n`.
6. A rational function that directly outputs only `+1/-1` parity on every group
   point requires pole degree at least `ceil(n/2)` under the stated regularity
   assumptions.
7. These direct-parity barriers do not automatically transfer to the isolated
   EDS residue. Frozen toy Fourier data place the residue trace near square-root
   scale rather than showing the linear parity spike.
8. Fixed-index products and ratios of division-polynomial character values are
   quadratically balanced and showed no exact decoder in the bounded screens.
9. The surviving class is a Kummer-invariant nonlinear character decoder,
   unbalanced theta, sigma, or elliptic-net section, exact p-adic or analytic
   normalization, or a nonlocal relation that fixes the absolute residue.

These are scoped no-go and localization results, not a general lower bound for
all non-generic ECDLP algorithms.

## Bounded validation saved

The branch retains reproducible synthetic or fixed-public-parameter checks for:

- all odd cyclic orders through 127;
- five frozen prime-order toy curves `y^2=x^3+7`;
- direct and structured character screens;
- 46,260 exact toy multiplication-identity checks;
- fixed-public secp256k1 replay of the raw point-function bridge;
- Kummer-residue negation classification;
- bounded searches over small products and ratios of candidate characters.

The committed JSON files preserve every current result. No result depends only
on a temporary container.

## Open blockers

1. Independently replay the secp256k1 point-function bridge in Sage or a second
   CAS.
2. Resolve or precisely source-label the `phi_raw` versus normalized `phi`
   exponent discrepancy in the Lauter-Stange formula.
3. Bind the division-polynomial negation law and Kummer-residue specialization
   to the repository's exact curve definitions.
4. Source-pin and tighten the theta-group dimension argument.
5. Formulate `CHAR-RESIDUE-001` for the correctly isolated target
   `chi(f(x(Q))) = rho_G(Q)`, without incorrectly importing the direct-parity
   Fourier spike.
6. Seek either an explicit low-cost decoder with a full recovery and cost
   theorem or a scoped mixed-character/conductor obstruction for that exact
   class.

## Resume order

1. Read this checkpoint and PR #365.
2. Confirm the latest branch CI after this checkpoint commit.
3. Do the independent Sage replay before merging or promoting any source-level
   claim.
4. Continue only on `rho_G`, not on direct x-only parity and not on sign-erasing
   GLV orbit norms.
5. Keep the branch draft and isolated from canonical Research Engine state until
   all merge-boundary items in the PR are satisfied.

## Progress interpretation

Completion of the four formal arithmetic foundations: 100 percent.
Persistence of current notes, code, results, and proof files: 100 percent.
Validation of the fixed-public secp256k1 bridge: one implementation complete,
independent replay pending.
Existence of a sub-square-root EDS-residue or parity decoder: no positive
evidence yet.

There is no honest percentage measuring distance to a general ECDLP solution.
The concrete progress is a narrower surviving target and several rigorously
excluded mechanism classes.