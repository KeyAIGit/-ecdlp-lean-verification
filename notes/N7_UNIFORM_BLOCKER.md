# N7 uniform blocker record

Status: **blocked, with one named wall closed**

Last bounded pass: **2026-07-24**

This record distinguishes the verified fixed-index and even-step substrate from
the still-open uniform theorem. It does not claim that N7 is proved.

## Closed in this pass

`Ecdlp.Curve.N7Uniform.even_x_algebra` is now a built theorem in
`Ecdlp/Proved/N7EvenXAlgebra.lean`. Its two division-polynomial doubling inputs
are built in:

- `Ecdlp/Proved/DivisionPolynomialPsiSqDoubling.lean`
- `Ecdlp/Proved/DivisionPolynomialPhiDoubling.lean`

The standalone kernel run is recorded at
<https://github.com/KeyAIGit/-ecdlp-lean-verification/actions/runs/30119285017>.
The proof uses no `sorry`, no custom axiom, and no generated elimination
certificate.

## Residual obligations

`Ecdlp/Targets/n7_uniform_carrier_induction.lean` now contains six bare `sorry`
obligations:

| obligation | class | blocker |
|---|---|---|
| `nsmul_eq_zero_iff_psi_evalEval_zero` | conceptual bridge | no uniform Point-to-division-polynomial multiplication theorem |
| `odd_x_algebra` | coupled scalar identity | consecutive-multiple y-coupling plus cross-index division-polynomial algebra |
| `even_y_algebra` | coupled scalar identity | omega-free tangent y-coordinate relation |
| `odd_y_algebra` | coupled scalar identity | omega-free secant y-coordinate relation |
| `odd_step_group`: `k * P = O` branch | downstream torsion branch | uniform Point-to-division-polynomial bridge |
| `odd_step_group`: `(k+1) * P = O` branch | downstream torsion branch | uniform Point-to-division-polynomial bridge |

`Ecdlp/Targets/n7_uniform_secp256k1_x.lean` contains one wrapper `sorry`; it
consumes the carrier theorem and is not a seventh independent mathematical wall.

## Why the earlier plan changed

The earlier reduction treated `PsiSq(2k)` and `Phi(2k)` as requiring a strong
`normEDSRec'` induction or large Groebner cofactors. The landed
plus-companion identity exposes the missing finite information:

```text
(U - V)^2 = (U + V)^2 - 4UV.
```

The plus-companion theorem supplies `U+V`, while Somos-4 supplies `UV`. This
turns both doubling identities into finite parity-specific ring proofs. See
`notes/N7_EVEN_X_REDUCTION.md`.

## Upstream state

Mathlib PR #13782, "ZSMul formula in terms of division polynomials", is the
relevant upstream route for the conceptual bridge. Until a usable theorem is
available in the pinned toolchain, the in-repo carrier induction remains the
independent route.

## Decision

No statement was weakened and no open theorem was promoted. The target remains
`blocked` because the uniform result is incomplete, but the blocker count and
proof DAG now reflect real progress.

The next bounded pass should attack exactly one of `odd_x_algebra`,
`even_y_algebra`, or `odd_y_algebra`. Work on the uniform bridge can proceed
independently and should be integrated only after kernel verification.
