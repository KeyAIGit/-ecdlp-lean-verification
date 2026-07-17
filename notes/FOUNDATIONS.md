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
| **Abel–Jacobi map / class group** `toClass : E(F) ↪ Pic(F[W])` | `…EllipticCurve.Affine.Point` (`import …RingTheory.ClassGroup.Basic`) | ✓ **present** — the group law *is* built on it |
| **Coordinate ring `F[W]`, function field `FunctionField`** | `…EllipticCurve.Affine.Point` | ✓ available |
| **Roots of unity `μₙ`** (Weil-pairing target) | `…RingTheory.RootsOfUnity.*` | ✓ available |
| `j`-invariant models, isomorphism-of-`j` | `…EllipticCurve.{ModelsWithJ,IsomOfJ}` | ✓ available |
| Reduction, variable change, normal forms | `…EllipticCurve.{Reduction,VariableChange,NormalForms}` | ✓ available |

## What is missing (the gap)

| Missing rung | Consequence | Difficulty |
|---|---|---|
| ~~`n`-torsion subgroup `E[n]` as a group object~~ ✓ **done** (Mathlib `AddSubgroup.torsionBy`, notation `A[n]`; our bridge in `Ecdlp/Proved/Torsion.lean`) | `E[n]` available; `E[n] ≅ (ℤ/n)²` still open | ~~high~~ closed |
| **Weil pairing** `eₙ : E[n] × E[n] → μₙ` + bilinearity/non-degeneracy — *substrate (Abel–Jacobi `toClass`, `FunctionField`, `μₙ`) is present; rung W1 (torsion ⟺ principal) done, see sub-ladder below* | no MOV/FR transfer, no pairing-based crypto | high (was very high) |
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
   an order-2 `x`-coordinate is a root of `Ψ₂Sq`). Full **both-direction** bridges are
   ✓ **done for `n = 3, 5, 7`** (`{Three,Five,Seven}TorsionBridge.lean`) by an elementary
   route that explicitly computes `[n]P` — but that route is `n`-specific and does not
   generalize. The **engine** that would generalize it is the multiplication formula
   `x([n]P) = Φₙ(x)/ΨSqₙ(x)` (Mathlib's canonical `Φ`/`ΨSq`); its **base case `n = 2`** is now
   ✓ **done** (`Ecdlp/Proved/MultiplicationFormula.lean`, `secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq`:
   `x(2•P) = Φ₂/Ψ₂Sq = (x⁴−56x)/(4y²)`). The **general `n`** formula — by induction on the
   division-polynomial recurrence — is the genuinely missing rung: it needs the
   division-polynomial/point-group link that Mathlib v4.31 does **not** package (present only
   in a stalled upstream PR; see `notes/UPSTREAM_SCAN.md`). This is the *same* class of missing
   machinery (function field / coordinate ring of the curve) as the Weil pairing itself — so
   the general bridge is **not** a cheap stepping-stone below the pairing, it is a comparable
   port. *(research-level; the base case is landed, general `n` is the multi-month gap.)*
5. **`E[n]` as `(ℤ/n)²`** — the structure theorem. Hard; needs the algebraic
   closure / separability story.
6. **Weil pairing** — define `eₙ` (e.g. via Miller's algorithm / Weil reciprocity),
   prove bilinear, alternating, non-degenerate, Galois-equivariant. The summit.

Rungs 1–3 are tractable now (concrete polynomial identities). Rung 4 is the first
genuinely hard step and the right target for a focused effort. Rungs 5–6 are the
multi-month core.

### Weil-pairing sub-ladder — reappraised (the substrate is already upstream)
A closer look at Mathlib **revises the difficulty downward** from "from zero": Mathlib's
elliptic-curve group law is itself **built on the ideal class group** of the coordinate ring,
exposing the **Abel–Jacobi map** `toClass : E(F) ↪ Pic(F[W])` as an *injective group
homomorphism* (`…Affine.Point`, `toClass_injective` / `toClass_eq_zero`), together with the
coordinate ring `F[W]`, the function field `FunctionField`, and the roots-of-unity target `μₙ`.
So the Weil pairing does **not** need the divisor↔point substrate built from scratch — it exists.
The concrete sub-ladder, from what is now done to the summit:
- **W1 — torsion ⟺ principal divisor** ✓ **done** (`Ecdlp/Proved/WeilDivisorClass.lean`,
  `secp256k1_torsion_iff_principal`): `n • P = 0 ⟺ n • toClass P = 0`, i.e. `n·([P] − [O])` is
  principal — the existence precondition for the Miller function `f_P`.
- **W2 — extract the Miller function** `f_P` ✓ **done** (`secp256k1_miller_function_exists`):
  from W1's principality, `ClassGroup.mk_eq_one_iff` yields a generator `f_P ∈ F(secp256k1)` of the
  principal ideal `(XYIdeal' h)ⁿ` — the Miller function with `div f_P = n·([P] − [O])`.
- **W3 — evaluate `f_P` at a divisor** `f_P(D_Q)` and prove independence of the chosen
  representative. The **representative-independence half** is ✓ **done**
  (`secp256k1_miller_function_unique`: two Miller functions differ by a unit of `F[E]`, via
  `Submodule.span_singleton_eq_span_singleton` — **proof designed by the Fable model,
  kernel-verified**, the first piloted "strong-model + Lean-kernel" rung). The **evaluation half**
  (`f_P(D_Q)`) is being built as new infrastructure (Mathlib v4.31 has no rational-function
  evaluation API and does not know `F[E]` is Dedekind): the **regular-function evaluation
  homomorphism** `evalAt : F[E] →+* F` (value of a regular function at a rational point, via
  `quotientXYIdealEquiv`) is ✓ **done** (`Ecdlp/Proved/PointEvaluation.lean`: `evalAt_surjective`,
  `evalAt_ker` = the maximal ideal at `P`). **Done further** (2026-07-16): the localization form
  `evalRatAt : Localization.AtPrime ⟨X−x,Y−y⟩ →+* F` and now the **fraction-level layer**
  (`Ecdlp/Proved/FunctionFieldEval.lean`): `evalFracAt` with representation-independence,
  Miller-loop multiplicativity, unit-nonvanishing, the `evalRatAt` bridge, and
  `secp256k1_miller_eval_scaling` (the W2 representative ambiguity is a globally
  nonvanishing unit at every rational point). **Next:** the `a/b`-presentation extraction
  for abstract `FunctionField` elements, then evaluation at divisors `f_P(D_Q)`.
- **W4 — Weil reciprocity** `f(div g) = g(div f)` — the crux identity. *Likely a genuine Mathlib
  gap.*
- **W5 — define `eₙ(P,Q)` and prove bilinear / alternating / non-degenerate / Galois-equivariant.*
  The summit.

W1, W2, and W3's representative-independence half are landed (W3 via a Fable-designed,
kernel-verified proof). The open frontier is the **function-evaluation API** (W3's evaluation half,
`f_P(D_Q)`) and **Weil reciprocity** (W4) — both genuine Mathlib gaps. This replaces the earlier
"multi-month from zero" estimate: the **hardest substrate (Abel–Jacobi) is already Mathlib's**, and
the remaining work is the function-evaluation + reciprocity layer.

### `E[n]` as a group object — closed via Mathlib (`Ecdlp/Proved/Torsion.lean`)

The "rung 1" framing ("define `E[n]` from scratch") turned out to be partly already
solved: Mathlib's `AddSubgroup.torsionBy A n` (notation `A[n]`) **is** `E[n] = ker[n]`,
with a `Module (ZMod n)` structure (`torsionBy.zmodModule`). The genuinely-new work was
the connective tissue tying it to ECDLP, now proved and in the ledger:

| Theorem | Content |
|---|---|
| `mem_torsionBy_iff_addOrderOf_dvd` | `P ∈ E[n] ⟺ ord(P) ∣ n` |
| `torsionBy_eq_ker_nsmul` | `E[n] = ker[n]` (kernel of `nsmulAddMonoidHom n`, the `[n]` map) |
| `zmultiples_le_torsionBy` | `⟨G⟩ ⊆ E[n]` for the base point (`ord G ∣ n`) |
| `torsionBy_dvd_le` | filtration `E[m] ≤ E[n]` for `m ∣ n` |
| `torsionBy_eq_top` / `zmod_module_nsmul_eq_zero` | DL-model bridge: `G[n] = ⊤` (cofactor-1 shape) |

What remains open (and needs Mathlib foundations that do not yet exist): the **structure
theorem** `E[n] ≅ (ℤ/n)²` (rung 5) and the **Weil pairing** (rung 6).

## Status of the open rungs

Rungs 1–3 and the easy direction of rung 4 are **proved** (`DivisionPolynomial.lean`,
`TwoTorsion.lean`). The general rung-4 equivalence and rungs 5–6 (the `E[n]`
structure theorem and the Weil pairing itself) remain open — they need Mathlib
foundations that do not yet exist, per the project rule that the kernel, not the
generator, certifies proofs. They are the right targets for a focused, human-
directed (or server-prover) effort, not an overnight autonomous one.
