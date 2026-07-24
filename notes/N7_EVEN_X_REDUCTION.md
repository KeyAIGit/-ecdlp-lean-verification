# N7 `even_x_algebra` - closed reduction

Status: **kernel-checked and closed on 2026-07-24**.

The N7 uniform carrier needs the tangent-doubling step

```text
X_k = Phi_k(x) / PsiSq_k(x)
  ==> addX(X_k, X_k, slope_k) = Phi_(2k)(x) / PsiSq_(2k)(x).
```

For secp256k1, set `A := (Phi k).eval x` and `B := (PsiSq k).eval x`. The
polynomial part is now proved in:

- `Ecdlp/Proved/DivisionPolynomialPsiSqDoubling.lean`
- `Ecdlp/Proved/DivisionPolynomialPhiDoubling.lean`

The identities are

```text
(PsiSq (2k)).eval x = 4 * B * (A^3 + 7 * B^3)
(Phi   (2k)).eval x = A^4 - 56 * A * B^3.
```

## Finite derivation

Let

```text
U = prePsi(k-1)^2 * prePsi(k+2)
V = prePsi(k-2) * prePsi(k+1)^2
T = prePsi(k+1) * prePsi(k-1).
```

The even recurrence gives `prePsi(2k) = prePsi(k) * (U - V)`. The key
observation is the finite decomposition

```text
(U - V)^2 = (U + V)^2 - 4 * U * V.
```

`PrePsiPlusCompanion.lean` supplies `U + V`; `PrePsiSomos4.lean` supplies the
product needed for `U * V`. Substitution leaves two parity-specific ring
identities. The same two inputs also reduce the odd-index product appearing in
`Phi(2k)`. Consequently the earlier proposed strong induction and large
Groebner certificates are unnecessary for this wall.

## Point-level assembly

`Ecdlp/Proved/N7EvenXAlgebra.lean` proves
`Ecdlp.Curve.N7Uniform.even_x_algebra`.

From `B != 0` and `X_k = A / B`, it obtains `X_k * B = A`. The curve equation
and tangent-slope equation force `X_k^3 + 7 != 0`, hence
`A^3 + 7 * B^3 != 0`; therefore the doubled denominator is nonzero. After
substituting the two polynomial identities, the remaining cleared equality is
the standard secp256k1 tangent identity scaled by `B^4`, discharged by
`linear_combination`.

## Research consequence

This closes only the N7 even-step x-coordinate wall. The uniform torsion bridge,
the odd x-coordinate wall, and the even/odd y-coordinate walls remain separate
targets. Work on those targets must not cite this result as a completed uniform
multiplication theorem.
