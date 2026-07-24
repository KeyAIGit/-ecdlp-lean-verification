# Depth roadmap: the `ψₙ ↔ E[n]` bridge as a lemma dependency graph

This is the **decomposition** of one deep, currently-unformalized result — the classical
correspondence between division polynomials `ψₙ` and `n`-torsion points — into a graph of
lemmas tagged **LEAF / MID / CORE**, so we can attack the *reachable leaves* now (by hand and
via the autonomous harness) while flagging the one genuinely hard core item honestly.

## Why this document exists
"Depth is blocked by missing Mathlib theory" is true but not a dead end. The missing theory
is not monolithic: it decomposes, and most of the pieces are polynomial algebra or finite
group theory that **are** reachable. This map turns "depth" into a concrete, prioritized
target list. It was produced by decomposition (Claude Fable 5, pure math) cross-checked
against a live survey of Mathlib's `AlgebraicGeometry/EllipticCurve/` tree.

## Live Mathlib survey (what actually exists, checked on the server)
- **Present:** `DivisionPolynomial/Basic.lean` + `Degree.lean` (the `ψₙ`/`Ψₙ` and their
  `x`-degrees — nodes N1–N4 territory); the group law with associativity (`Affine`,
  `Jacobian/Projective` addition formulas); `VariableChange`, `Reduction`, `NormalForms`;
  an `LFunction.lean` for elliptic curves (worth a look for Frobenius-trace formalism).
- **Absent:** the **Weil pairing** (nothing under `AlgebraicGeometry/`), the
  **multiplication-by-`n` isogeny degree / separability** theory, `#E[n] = n²`,
  `E[n] ≅ (ℤ/n)²`, and computable point-counting `#E(𝔽_p)`.

## The one irreducibly hard item
Per the map, the **unique** CORE-by-theory item on the entire critical path is
**separability of `[n]`** (`[n]*ω = n·ω` on the invariant differential `ω = dx/2y`). The
degree `n² ` itself falls out of the polynomial layer (N4 + N5 + N7); it does **not** need
Weil pairings. Everything else is polynomial algebra, finite group theory, or large-but-
decidable identities.

## Reachable frontier — attempt these now
| Node | Statement (informal) | Tag | Status |
|---|---|---|---|
| **N12** | odd `n`: `E[n] ∩ E[2] = {O}` and the `±`-pairing of `x`-coords | LEAF | ✅ **proved** — `secp256k1_odd_two_torsion_disjoint` (`Ecdlp/Proved/TorsionCoprime.lean`) |
| N4 | `φₙ := x·ψₙ² − ψₙ₊₁ψₙ₋₁` is monic of degree `n²` | LEAF | reachable (needs Mathlib `φ`/`Ψ` API) |
| N5 | `gcd(φₙ, ψₙ²) = 1` in `k̄[x]` (ends in a resultant-vs-`Δ` computation) | MID | reachable; **highest-value unblocked** (feeds N10 degree + N11). 🔄 **reduced to the scalar EDS**: the eval bridge (`Ecdlp/Proved/DivisionPolynomialEvalBridge.lean`, `exists_normEDS_consecutive_eq_zero_of_not_isCoprime`) shows `¬IsCoprime(Φₙ,ΨSqₙ)` over `k` ⟹ two consecutive `normEDS` zeros over `k̄`; remaining N5 work is now a no-consecutive-zeros statement about the scalar sequence. 🔓 **propagation engine landed**: `normEDS_isEllSequence` (`NormEDSIsElliptic.lean`, the L4 port) + `normEDS_somos4` + the L5/L6/L6b degenerate-case certificates make the scalar statement attackable now — stated as the open stem `Ecdlp/Targets/normeds_no_consecutive_zero.lean` (registry `targets/normeds_no_consecutive_zero.json`; TASK-005 memo in `notes/POINT_COUNTING_KEYSTONE.md`) |
| **L2/L3** (eval bridge) | `(ΨSq n).eval x₀ = w n²`, `(Φ n).eval x₀ = x₀·w n² − w(n+1)w(n−1)` for `w = normEDS β Ψ₃(x₀) preΨ₄(x₀)`, `β²=Ψ₂Sq(x₀)` | LEAF | ✅ **proved** — `eval_ΨSq_eq_normEDS_sq`/`eval_Φ_eq_normEDS`/`eval_preΨ_eq_preNormEDS` (`Ecdlp/Proved/DivisionPolynomialEvalBridge.lean`), curve-generic; cert `scripts/certs/eval_bridge_check.py` |
| N7@small `n` | `x∘[n] = φₙ/ψₙ²` for fixed `n = 2,3,4,5` | closed `ring` identities | reachable — ideal harness/prover-loop targets |
| N10(iii) | finite-abelian group of order `n²`, exponent `∣ n`, with `≤ d²` `d`-torsion is `(ℤ/n)²` | MID | ✅ **proved uniformly for prime `n`** — `nonempty_addEquiv_zmod_prod_of_card_eq_sq` (`Ecdlp/Proved/TorsionStructure.lean`); the concrete first composite profile `n=4` is also closed by `nonempty_addEquiv_zmod_four_prod_of_card_and_two_torsion` (`Ecdlp/Proved/FourTorsionClassification.lean`); general composite `n` remains open |
| N8, N9 | conditional on N7 (state with N7 as hypothesis, discharge later) | MID | reachable as reductions |

**Blocked (with the single unblocking theorem):**
- **N7 uniform** ← the addition-formula rational identity packaged for substitution in `k(E)` (effort, not theory).
- **N10** ← **separability of `[n]`** (the one hard item).
- **N11** ← N10 (take the *counting* route, not the geometric one — it needs no scheme theory).
- **N13** (main theorem) ← N10 + N11; assembly only.

**Critical path:** `N5 → N7 → N10(i)+[separability] → N10 → N11 → N13`.

These reachable leaves are exactly what the autonomous `agent-day` harness should target (see
`targets/queue.json`): each is either a closed identity or a self-contained algebra/group
lemma. The harness proves leaves; the CORE separability item is a longer, human/community-scale
effort — flagged here, not hidden.

---

## Full dependency map (Fable-drafted, pure math)

*The following graph and node analysis is pure algebraic geometry / number theory; only the
node marked ✅ above is currently kernel-verified. The rest is the plan.*

**Setting.** `E : y² = x³ + Ax + B` over a field `k`, `char k ≠ 2,3`, `Δ = −16(4A³+27B²) ≠ 0`.
`f(x) = x³+Ax+B`, `R = k[x,y]/(y²−f)`, `k̄` an algebraic closure. Target statement assumes
`char k ∤ n`.

**Target (T).** For odd `n` with `char k ∤ n`: `ψₙ ∈ k[x]`, `deg_x ψₙ = (n²−1)/2`, `ψₙ`
separable over `k̄`, and its roots are exactly the `x`-coordinates of the `P ∈ E(k̄)∖{O}` with
`[n]P = O`.

**Graph.**
```
N1 ─ N2 ─ N3 ─ N4                      (polynomial layer)
           │     │
           └──── N5 (coprimality)
N6 (curve ring is a domain)
N6 + group law ⇒ N7 (mult. formula, CORE-by-effort)
N7 ⇒ N8 ⇒ N9  ("⇒" direction)
N3 + N4 + N5 + N7 ⇒ N10 (#E[n]=n², CORE: separability)
N9 + N3 + N10 ⇒ N11 (bridge, "⇐", via counting)
N9 + N11 + N10 + N12 ⇒ N13 = T
```

- **N1 (LEAF)** recursion `ψ₀..ψ₄` + `ψ_{2m+1}=ψ_{m+2}ψ_m³−ψ_{m−1}ψ_{m+1}³`, `ψ_{2m}=(2y)^{-1}ψ_m(ψ_{m+2}ψ_{m−1}²−ψ_{m−2}ψ_{m+1}²)`, well defined in `R` (even case divisible by `2y`).
- **N2 (LEAF)** parity: `n` odd ⇒ `ψₙ ∈ k[x]`; `n` even ⇒ `ψₙ ∈ 2y·k[x]`; so `ψₙ² ∈ k[x]` always.
- **N3 (MID)** `deg_x ψₙ = (n²−1)/2` (odd), leading coeff `n`; **must** carry `char k ∤ n` (else the degree drops — the target is false without it).
- **N4 (LEAF)** `φₙ := xψₙ² − ψₙ₊₁ψₙ₋₁ ∈ k[x]` monic of degree `n²`.
- **N5 (MID)** `gcd(φₙ, ψₙ²)=1` in `k̄[x]`; uses `Δ ≠ 0` (a common root propagates down to `gcd(φ₂, ψ₂²)` whose resultant is a power of `Δ`).
- **N6 (LEAF/MID)** `y²−f` irreducible ⇒ `R` a domain, `k(E)` its fraction field; evaluation at `P` is a ring map; inversion `(x,y)↦(x,−y)`.
- **N7 (CORE-by-effort)** `x∘[n] = φₙ/ψₙ²` in `k(E)`; induction via `[n+1]P=[n]P+P` and the addition formula — a huge `ring` identity mod `y²=f`. **Stratifies:** each fixed `n` is a self-contained computable identity.
- **N8 (MID given N7)** for affine `P` with `ψₙ(P) ≠ 0`: `[n]P ≠ O` and `x([n]P)=φₙ(P)/ψₙ(P)²`.
- **N9 (MID given N7–N8)** forward: `[n]P=O ⇒ ψₙ(P)=0` (contrapositive of N8; `ψ₂=2y` handles `E[2]`).
- **N10 (CORE)** `char k ∤ n` ⇒ `[n]` separable of degree `n²`, so `#E[n]=n²`, `E[n]≅(ℤ/n)²`. Three inputs: (i) degree from `φₙ/ψₙ²` in lowest terms = N4+N5+N7; (ii) **separability** `[n]*ω=nω` (the hard item); (iii) kernel-structure group lemma (MID).
- **N11 (CORE geom / MID via counting)** `ψₙ(x₀)=0 ⇒ (x₀,±√f(x₀))` are `n`-torsion. **Counting route (preferred):** N9 makes every one of the `(n²−1)/2` torsion `x`-coords a root of `ψₙ`; degree `(n²−1)/2` (N3) exhausts the roots, giving `⇐` and separability for free — no scheme theory.
- **N12 (LEAF)** ✅ odd `n`: `E[n]∩E[2]={O}`; nonzero `P∈E[n]` has `y≠0`, `x(P)=x(−P)`, distinct `±`-pairs distinct `x` ⇒ `(n²−1)/2` `x`-values.
- **N13 (MID)** assemble: two inclusions (N9, N11) + cardinality (N3, N10, N12).

---
*Provenance: dependency analysis drafted by Claude Fable 5 (pure math), cross-checked against
a live Mathlib survey; the reachable-frontier priorities and the single ✅ verified node are
the actionable output. Only `secp256k1_odd_two_torsion_disjoint` is kernel-verified so far.*
