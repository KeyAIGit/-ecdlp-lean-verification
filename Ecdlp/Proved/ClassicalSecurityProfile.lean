import Mathlib
import Ecdlp.Proved.CurveCardinalityExact
import Ecdlp.Proved.Secp256k1PrimeN
import Ecdlp.Proved.TraceOfFrobenius
import Ecdlp.Proved.EmbeddingDegree

/-!
# secp256k1's classical attack-resistance profile — one unconditional theorem

This is the **thesis statement** of the secp256k1 substrate: a single kernel-verified theorem
bundling every structural fact that closes off a *known, classically-expressible* attack on the
curve's discrete logarithm. Each conjunct is an independently proved theorem elsewhere in the
tree; this file assembles them into the one profile a security claim would cite.

**What the profile asserts (all unconditional, all proved):**
* `Nat.card E(𝔽_p) = n` — the exact group order, **cofactor 1** (`secp256k1_card_point_eq_n`,
  curve-specifically, no Hasse/Schoof).
* `Nat.Prime n` — the order is **prime** (`secp256k1_n_prime`, full Pratt certificate). Two
  consequences at once: **Pohlig–Hellman offers no reduction** (there is no proper factor of `n`
  to project onto), and the point group has **no proper nontrivial subgroup**, so
  small-subgroup / invalid-subgroup confinement attacks have no target.
* `t ≠ 0` where `t = p + 1 − n` — the curve is **ordinary, not supersingular**: the
  supersingular MOV/embedding-degree-≤6 transfer does not apply.
* `t ≠ 1` — the curve is **not anomalous** (`#E ≠ p`): the Smart / Semaev–Satoh–Araki `p`-adic
  attack is inapplicable.
* `t² ≤ 4p` — the **Hasse** bound, so `#E = n` sits in the valid range (sanity/consistency).
* `∀ j < 100, p^{j+1} ≢ 1 (mod n)` — the **embedding degree exceeds 100**, so the MOV/Frey–Rück
  pairing transfer lands in an intractably large field `𝔽_{p^k}`.

**Honest scope — what this is NOT (read `notes/SECURITY_SCOPE.md`).**
This is the *classical, structural* attack-resistance envelope: it certifies that none of the
known classical shortcuts (Pohlig–Hellman, small-subgroup, supersingular-MOV, anomalous-SSSA,
small-embedding-degree MOV/FR) applies to secp256k1. It is **not** a proof that the ECDLP is
hard: the only *positive* hardness result in this repo is the **generic-group `Ω(√n)` lower
bound** (`secp256k1_generic_security`), which bounds only black-box generic algorithms and says
nothing about a hypothetical non-generic prime-field attack (whose non-existence is the open
ECDLP hardness conjecture). And it is **classical only** — Shor's algorithm solves the ECDLP in
quantum polynomial time; nothing here bears on that.

So: this theorem is the machine-checked statement *"every classical attack we can express is
blocked,"* not *"secp256k1 is unbreakable."* That honest boundary is the point.
-/

namespace Ecdlp.Curve

/-- **secp256k1's classical attack-resistance profile.** A single unconditional theorem
collecting the structural facts that individually rule out each known classically-expressible
ECDLP shortcut: cofactor 1 and prime order (⇒ no Pohlig–Hellman, no small subgroup), not
supersingular (`t ≠ 0`), not anomalous (`t ≠ 1`), Hasse-consistent (`t² ≤ 4p`), and embedding
degree `> 100` (⇒ no feasible MOV/Frey–Rück transfer). See the module docstring for the honest
scope: this is the *classical structural* envelope, not a hardness proof (the only proved
hardness is the generic `Ω(√n)` bound) and not quantum-secure (Shor breaks it). -/
theorem secp256k1_classical_security_profile :
    Nat.card secp256k1.toAffine.Point = Secp256k1.n ∧
    Nat.Prime Secp256k1.n ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 0 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ≠ 1 ∧
    ((Secp256k1.p : ℤ) + 1 - Secp256k1.n) ^ 2 ≤ 4 * (Secp256k1.p : ℤ) ∧
    (∀ j, j < 100 → Secp256k1.p ^ (j + 1) % Secp256k1.n ≠ 1) :=
  ⟨secp256k1_card_point_eq_n,
   Ecdlp.Primality.secp256k1_n_prime,
   secp256k1_trace_ordinary_nonanomalous.1,
   secp256k1_trace_ordinary_nonanomalous.2.1,
   secp256k1_trace_ordinary_nonanomalous.2.2,
   secp256k1_embedding_degree_gt_100⟩

end Ecdlp.Curve
