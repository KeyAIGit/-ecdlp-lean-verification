# B1 formalization plan — `gcd(Φₙ, ψₙ²) = 1`, and the Mathlib TODO it hits

Full proof plan for node **B1** of Route B (`notes/SEPARABILITY_ROUTES.md`), decomposed into 10
sub-lemmas. **Key finding: B1's hard core (L4) is an *explicit open TODO in Mathlib itself*** —
so B1 is both a bigger effort than the roadmap's "few hundred lines" estimate **and** a concrete
**upstream-Mathlib contribution opportunity**.

## Executive summary (what to act on)
- **Size:** ~900–1500 lines across 2–3 files — *not* a single-file leaf. B1 is a project, not a node.
- **The crux:** "consecutive `ψₙ, ψₙ₊₁` share no root" (L7–L10), whose engine is **L4 + `Δ≠0`**.
- **L4 = `IsEllSequence (normEDS b c d)`** (the fundamental recurrence
  `Wₘ₊ₙWₘ₋ₙ = Wₘ₊₁Wₘ₋₁Wₙ² − Wₙ₊₁Wₙ₋₁Wₘ²`) is **an explicit `TODO` in
  `Mathlib/NumberTheory/EllipticDivisibilitySequence.lean` (v4.31.0)** — the pinned version. It is
  the single dominant cost (~400–700 lines, Ward-style double induction over `Frac(ℤ[b,c,d])`).
  **Proving it and PR-ing it upstream is a genuine, named Mathlib contribution** that would unblock
  B1 and help everyone.
- **Reachable now, independent of L4:** L1 (coprime ↔ no common root), L2/L3 (specialize to a scalar
  EDS + the reduction), **L5/L6 (Bézout-certificate coprimality `Δ≠0 ⇒ IsCoprime Ψ₂Sq Ψ₃` and
  `IsCoprime Ψ₃ preΨ₄`)**, L7 (the `β=0` case). L5/L6 are self-contained `linear_combination`
  certificates (cofactors computable on the server's CAS) — the best immediate leaves.

## The three ways forward (a real allocation decision)
1. **Chip the independent sub-lemmas now** (L5, L6, L2, L3, L1, L7) — real verified nodes, each
   small, that stand alone and pre-build B1's scaffolding. Free / in-session. Leaves L4 for later.
2. **Go for the L4 upstream contribution** — prove `IsEllSequence (normEDS …)`, PR it to Mathlib.
   Big (~semester-fraction), prestigious, unblocks B1 *and* benefits the community. Human-led + me.
3. **Feed the decomposed bounded sub-lemmas to the Opus autonomy** — L5/L6/L2/L3 are now bounded
   enough to be autonomous-harness targets (the `$/mo` budget applied to real depth-leaves).

**Recommendation:** start with **L5/L6** (CAS-assisted Bézout certificates — concrete wins that
introduce `Δ≠0` into the verified base), in parallel scope the **L4 upstream PR** as the flagship
deep contribution. Autonomy handles the remaining bounded scaffolding (L2/L3).

---

## Full sub-lemma plan (Fable-drafted, pure math)

*Pure algebra; none kernel-verified yet. Conventions: Mathlib's `Ψ₂Sq, preΨ, ΨSq, Φ` for
`W : WeierstrassCurve k` in short form. No group law / no `[n]`-map is used — everything is the
`normEDS` recurrences evaluated at a putative common root. Suffices to treat `n ≥ 1` by
`preΨ(−n) = −preΨ(n)`.*

- **L1 (EASY).** For `f g ∈ k[X]`, `IsCoprime f g ↔` no common root in `k̄`. Mathlib: `gcd` commutes
  with `map` to `k̄`; non-unit gcd over alg-closed has a root.
- **L2 (EASY–MEDIUM).** Fix `x₀∈k̄`, pick `β` with `β²=Ψ₂Sq(x₀)`, set `Wₖ := normEDS β (Ψ₃ x₀)
  (preΨ₄ x₀) k`. Then `eval x₀ (ΨSq n) = Wₙ²` and `eval x₀ (Φ n) = x₀Wₙ² − Wₙ₊₁Wₙ₋₁`. Uses
  `normEDS`/`preNormEDS` eval-compatibility + parity bookkeeping against Mathlib's `Φ` definition.
- **L3 (EASY).** If `eval x₀ (ΨSq n)=0=eval x₀ (Φ n)` (`n≥2`) then `Wₙ=0` and (`Wₙ₋₁=0` or
  `Wₙ₊₁=0`) — two *consecutive* terms vanish. Purely from the definition of `Φ`. (Dispatches `n=1`.)
- **L4 (HARD — Mathlib TODO).** `IsEllSequence (normEDS b c d)`; we use `r=1`:
  `Wₘ₊ₙWₘ₋ₙ = Wₘ₊₁Wₘ₋₁Wₙ² − Wₙ₊₁Wₙ₋₁Wₘ²`. Prove universally over `ℤ[b,c,d]`, transport by `eval`;
  Ward double induction over `Frac(ℤ[b,c,d])` using the definitional doubling recurrences
  (`preNormEDS'_odd/even`), clear denominators. **~400–700 lines; the dominant cost.**
- **L5 (MEDIUM).** `Δ≠0 → IsCoprime Ψ₂Sq Ψ₃` via an explicit Bézout certificate
  `u·Ψ₂Sq + v·Ψ₃ = (unit)·Δ^e` (cofactors from a resultant computation offline). One
  `linear_combination`. "No point is both 2- and 3-torsion."
- **L6 (MEDIUM).** `Δ≠0 → IsCoprime Ψ₃ preΨ₄`, same certificate method. "Not both 3- and 4-torsion."
- **L7 (MEDIUM).** `β=0 ⇒ Wₖ≠0` for odd `k` (so no two consecutive vanish). With `β=0`, even terms
  vanish and `preNormEDS'_odd` degenerates to products of odd terms; base `W₁=1`, `W₃=Ψ₃(x₀)≠0` by
  **L5**. **First use of `Δ≠0`.**
- **L8 (MEDIUM–HARD).** `β≠0`, `r := min{k≥2 : Wₖ=0}` ⇒ `Wᵣ₊₁≠0`. `r=3` needs **L6**; higher `r` by
  L4 instances `(r−1,r−2)`,`(r,r−3)` + minimality. Index gymnastics, `omega`-guarded.
- **L9 (MEDIUM).** `Wₖ=0 ⇒ r∣k`. Strong induction via L4 instances `(r,k−r)` and minimality.
- **L10 (EASY, assembly).** From L3: `Wₙ=0`, `Wₙ±₁=0`. `β=0`⇒ contradicts L7. `β≠0`⇒ L9 gives
  `r∣n` and `r∣n±1` ⇒ `r∣1`, contradicting `r≥2`. Hence no common root ⇒ `IsCoprime (Φ n) (ΨSq n)`.

**Mathlib inventory:** definitions + base values + doubling recurrences + degrees are present;
**by-hand:** L4 (TODO), L5–L9, coprimality itself, possibly the L2 eval-lemma. Start L2/L3 (pin
parity conventions), then L5/L6 (independent, certificate-based), attack L4 last.
