# HASSE_RECON.md — Mathlib v4.31 reconnaissance toward `#E(𝔽_p) = n`

Live scouting of the pinned toolchain (Lean v4.31.0 + its Mathlib) for the **strong keystone**
`#E(𝔽_p) = n` (cofactor 1). Findings verified by grepping the actual Mathlib source on the warm
server (not from memory), 2026-07. Supersedes the Mathlib-inventory parts of
`POINT_COUNTING_KEYSTONE.md` §3.1, which predates the current toolchain.

## What Mathlib v4.31 has (verified)

- Full Weierstrass-curve group law (Affine / Projective / Jacobian), division polynomials,
  `toClass`/`Pic` substrate, `j`-invariants — as before.
- **NEW: `AlgebraicGeometry/EllipticCurve/LFunction.lean`.** It defines the local L-function of
  a Weierstrass curve over a nonarchimedean local field:
  `localPolynomial = 1 − a·T + q·T²` (good reduction), with
  `a = q + 1 − Nat.card ((W'.reduction R).toAffine.Point)` and `q = Nat.card (residue field)`.
  So Mathlib now **names the point-count `Nat.card E.toAffine.Point` and the trace `a = q+1−#E`
  as first-class expressions** — the quantities the keystone is about are expressible.
  *Caveat (from Mathlib's own docstring):* these use `Nat.card`, which has **junk value 0** when
  the type is infinite — i.e. Mathlib does **not** prove the point group finite; the L-function
  is defined formally regardless.

## What is still absent (verified — grep empty)

- **`Finite` / `Fintype` instance for `WeierstrassCurve.Affine.Point`** — nowhere in Mathlib,
  not even over a finite field. So `Nat.card E.toAffine.Point` is currently junk (0) for any
  concrete curve until finiteness is supplied.
- **The Hasse bound** `|#E(𝔽_q) − (q+1)| ≤ 2√q` — absent (the only `Hasse.lean` in Mathlib is a
  graph-theory Hasse *diagram*, unrelated).
- **Trace of Frobenius as a developed invariant** (char. poly `φ² − tφ + q = 0` on the Tate
  module), Schoof, CM point counting, Weil conjectures for curves — all absent.

## Consequence: the certificate route, recomputed

`#E = n` reduces (as in `POINT_COUNTING_KEYSTONE.md` §3.3) to three pieces:

| piece | v4.31 status | cost |
|---|---|---|
| **1. `n ∣ #E`** — order-`n` point `G` + `Finite E(𝔽_p)` + Lagrange | Lagrange ✅, `Nat.card ⟨G⟩ = n` ✅ (proved), **`Finite` instance ✗ but elementary** | **bounded — landable now** |
| **2. Hasse** `#E ≤ p + 1 + 2√p` | ✗ absent | multi-month, research-grade |
| **3. interval uniqueness** `2n > p+1+2√p ⇒ #E = n` | one `native_decide` on ℤ | trivial |

**The reachable, non-Hasse increment is piece 1: `n ∣ #E(𝔽_p)`.** It needs one elementary new
instance — `Finite (secp256k1.toAffine.Point)` via the injection
`Point ↪ Option (𝔽_p × 𝔽_p)` (`0 ↦ none`, `some x y _ ↦ some (x,y)`; the field is finite) —
after which additive Lagrange (`Nat.card ↥⟨G⟩ ∣ Nat.card E`) plus the proved
`secp256k1_grp_card : Nat.card ⟨G⟩ = n` give `n ∣ #E`. This also makes `Nat.card E.toAffine.Point`
**meaningful** (not junk), so the newly-available L-function coefficient becomes real for the curve.

That is a genuine partial strong-keystone result: it pins `#E ∈ {n, 2n, 3n, …}` and reduces the
whole keystone to **exactly one missing theorem, the Hasse bound**, which rules out every
multiple `> n` via `2n > p+1+2√p`.

## Honest cost of the remaining gap (Hasse)

Hasse is a comparable-depth theorem to the Weil pairing (`FOUNDATIONS.md` B3), not a stepping
stone below it. Every standard proof needs machinery Mathlib lacks: the Frobenius endomorphism
on the Tate module with its characteristic polynomial and a positivity/Cauchy–Schwarz bound
(`|t| ≤ 2√q`); or Riemann–Roch + the functional equation; or Manin's elementary route, which
still needs `End(E)` as a lattice with a positive-definite norm form. **Multi-month,
research-grade.** The L-function file's arrival is encouraging (the surrounding theory is being
built upstream) but does **not** shortcut Hasse.

## Recommendation

1. **Piece 1 — LANDED ✅.** `Finite (secp256k1.toAffine.Point)` + `n ∣ #E(𝔽_p)` are now
   proved in `Ecdlp/Proved/CurveCardinality.lean` (both **pure-kernel**, no `native_decide`),
   imported from `Ecdlp.lean`, and in the ledger (`VERIFIED.md`). Server-verified building on
   the pinned toolchain. This is the first verified rung *toward* the strong keystone (the notes
   previously had *nothing* on `#E` itself, only the ⟨G⟩ weak keystone). It also lights up the
   L-function coefficient for secp256k1 (and transfers to P-256 with its order-point certificate).
2. **Park the Hasse bound** as blocked, same tier as the Weil pairing — reduced now to a single
   reusable theorem, but that theorem is a multi-month port. Do not start it as a session task.
3. **Watch upstream.** With `LFunction.lean` landed, the elliptic-curve-over-finite-fields theory
   is actively growing in Mathlib; a future toolchain bump may bring finiteness / Frobenius /
   Hasse and collapse this gap. Re-run this recon after each Mathlib bump.
