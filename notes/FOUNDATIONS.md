# Deep foundations roadmap — toward the Weil pairing and the transfer reductions

This is the **honest map** of the deepest barrier in `BARRIERS.md` (B3: curve &
polynomial depth). It records what Mathlib already provides, the precise rung that
is missing, and a concrete ladder of stepping-stones — so the foundation work can
be picked up incrementally (by a human, by the prover loop, or by a future
automated reasoner) without re-discovering the gap each time.

**Reality check.** A full, kernel-verified Weil pairing is a multi-month,
research-grade Mathlib contribution. Nothing here claims it is close. The value is
the map and the verified first rungs, not a finish line.

## Why this matters for ECDLP

Two of the four classical "transfer" attacks reduce ECDLP to an easier discrete log
*through the pairing*:
- **MOV / Frey–Rück** — embeds `⟨P⟩` into `𝔽_{p^k}^×` via the Weil/Tate pairing.
- **Anomalous (Smart/SSSA)** — uses the `p`-adic elliptic logarithm, not the
  pairing, but lives in the same torsion/formal-group neighbourhood.

We have already machine-checked that secp256k1 **resists** both (`EmbeddingDegree`,
`TraceOfFrobenius`) — the security-relevant boundary facts. What is *not*
formalizable yet is the **attack mechanism itself**, because the Weil pairing is not
in Mathlib. Formalizing the pairing would let a future system reason about the
transfer constructively, not just about its inapplicability here.

## What Mathlib has (verified present)

| Component | Mathlib location | Status |
|---|---|---|
| Weierstrass curves, `a`/`b`/`c`-invariants, `Δ`, `j` | `AlgebraicGeometry.EllipticCurve.Weierstrass` | ✓ used here |
| Affine/Projective/Jacobian point group law | `…EllipticCurve.Affine` / `Projective` / `Jacobian` | ✓ used here |
| **Division polynomials** `ψₙ, φₙ, ωₙ, preΨ, ΨSq, Φ` | `…EllipticCurve.DivisionPolynomial.{Basic,Degree}` | ✓ **bridged** (below) |
| `j`-invariant models, isomorphism-of-`j` | `…EllipticCurve.{ModelsWithJ,IsomOfJ}` | ✓ available |
| Reduction, variable change, normal forms | `…EllipticCurve.{Reduction,VariableChange,NormalForms}` | ✓ available |

## What is missing (the gap)

| Missing rung | Consequence | Difficulty |
|---|---|---|
| `n`-torsion subgroup `E[n]` as a group object | no `E[n] ≅ (ℤ/n)²` | high |
| **Weil pairing** `eₙ : E[n] × E[n] → μₙ` + bilinearity/non-degeneracy | no MOV/FR transfer, no pairing-based crypto | very high |
| Tate pairing | alternative transfer | very high |
| Isogenies as a developed theory | no degree/dual/kernel reasoning | high |
| Semaev summation polynomials `Sₙ` | no elliptic index calculus | high |

## The ladder (concrete stepping-stones, in order)

1. **`b`-invariants of secp256k1** — `b₂=b₄=b₈=0`, `b₆=28`.  ✓ **done**
   (`Ecdlp/Proved/DivisionPolynomial.lean`).
2. **2-division polynomial** `Ψ₂Sq = 4X³+28`.  ✓ **done** (same file). Roots = the
   order-2 `x`-coordinates (the roots of `X³+7`).
3. **3-division polynomial** `Ψ₃ = 3X⁴ + 84X` for secp256k1, and its degree.
   *(next; a concrete `simp`/`ring` identity on top of the `b`-invariants.)*
4. **`ψₙ` vanishing ⟺ `n`-torsion** — connect `ψₙ(x_P)=0` to `[n]P = O`. The easy
   forward direction for 2-torsion is ✓ **done** (`Ecdlp/Proved/TwoTorsion.lean`:
   an order-2 `x`-coordinate is a root of `Ψ₂Sq`). The general statement — all `n`,
   both directions, tied to actual point order — needs the division-polynomial/
   point-group bridge; Mathlib has the pieces but not the equivalence as a packaged
   lemma. *(research-level, but bounded.)*
5. **`E[n]` as `(ℤ/n)²`** — the structure theorem. Hard; needs the algebraic
   closure / separability story.
6. **Weil pairing** — define `eₙ` (e.g. via Miller's algorithm / Weil reciprocity),
   prove bilinear, alternating, non-degenerate, Galois-equivariant. The summit.

Rungs 1–3 are tractable now (concrete polynomial identities). Rung 4 is the first
genuinely hard step and the right target for a focused effort. Rungs 5–6 are the
multi-month core.

## Status of the open rungs

Rungs 1–3 and the easy direction of rung 4 are **proved** (`DivisionPolynomial.lean`,
`TwoTorsion.lean`). The general rung-4 equivalence and rungs 5–6 (the `E[n]`
structure theorem and the Weil pairing itself) remain open — they need Mathlib
foundations that do not yet exist, per the project rule that the kernel, not the
generator, certifies proofs. They are the right targets for a focused, human-
directed (or server-prover) effort, not an overnight autonomous one.
