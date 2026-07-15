# Security scope — what "≥128-bit generic security" does and does not mean

A precise reading of the machine-checked lower bound (`secp256k1_generic_security`,
`generic_dlog_sqrt_bound` in `Ecdlp/Proved/`). The claim is real, but its scope is narrow;
this file states exactly where it stops so nothing here reads as unconditional security.

## The theorem (proven, kernel-checked)

Any **classical, generic** algorithm — one that treats the group as a black box, using only
the group operation and *never inspecting the bit-representation* of a point — needs more than
`2^127` group operations to solve ECDLP on secp256k1. It is the information-theoretic
collision-counting bound of **Shoup (1997) / Nechaev (1994)**: the algorithm's whole view is
the collision pattern of the affine forms `a + b·X` it has formed in the unknown log `X`, two
distinct forms collide at ≤ 1 value, and a union bound over `q` queries gives success
probability `≤ q²/n`. It is **tight**: Pollard rho and baby-step/giant-step match it at
`O(√n)`, so generic DLP is `Θ(√n)`. Prime `n` (cofactor 1) matters — Pohlig–Hellman reduces
composite-order DLP to the largest prime-order subgroup.

## What it does NOT prove (the honest gaps)

1. **Not unconditional.** It says nothing about **non-generic** algorithms that exploit the
   concrete `(x, y)` encoding (`y² = x³ + 7` over `𝔽_p`). For the multiplicative group `𝔽_p^×`
   this gap is real and *proven*: **index calculus** provably beats `Ω(√p)` sub-exponentially
   by using smoothness/factorization the generic model ignores. So generic hardness **does not
   imply** actual hardness. For elliptic curves over a prime field no analogous algorithm is
   known — points do not factor, lifting to `ℚ` fails (Xedni calculus was refuted) — but its
   **non-existence is a conjecture**, not a theorem (~40 years of failed attempts).

2. **Classical only.** **Shor's algorithm** solves ECDLP in *polynomial time* on a quantum
   computer. The bound is a classical-query theorem and provably does **not** extend to
   quantum adversaries. secp256k1's 128-bit claim is classical-only.

3. **An unconditional lower bound is out of reach today.** ECDLP hardness implies `P ≠ NP`
   (discrete log is in NP ∩ coNP), and there are **no** known unconditional super-polynomial
   lower bounds for any natural problem. The generic bound is a *relativized* result (hardness
   relative to a random-encoding oracle), and relativized separations provably cannot settle
   real-world complexity.

## What the repo *additionally* proves (the classical landscape is saturated)

secp256k1 demonstrably avoids the known **non-generic classical** attacks — each machine-
checked: embedding degree > 100 (anti-MOV/Frey–Rück, `EmbeddingDegree.lean`), trace `t ≠ 1`
(anti-Smart/SSSA — not anomalous) and `t ≠ 0` with Hasse (ordinary, not supersingular,
`TraceOfFrobenius.lean`), prime field (no Weil descent). So every classical attack expressible
without a missing Mathlib foundation resists — the tractable attack landscape is saturated.

## The one place the numbers are *worse*: the quadratic twist

All of the above is about the curve `E`. The **quadratic twist `Ẽ / 𝔽_p`** is weaker, and the
repo now certifies it (`TwistSecurity.lean`). An `x`-only (Montgomery-ladder) scalar multiply
cannot tell an input on `E` from one on `Ẽ` — they share the `x`-line — so unvalidated input
runs in `Ẽ(𝔽_p)`, with the twist's security, not the curve's. Machine-checked:
`#Ẽ = 2p+2−n = 3²·13²·3319·22639·Q` with `Q` a **220-bit prime**. Two honest downgrades:

* the twist is **not** prime-order — cofactor `3²·13²·3319·22639 ≈ 2³⁷` gives real small
  subgroups a point can be confined to (the curve's point group, by contrast, is simple);
* the big subgroup is only `≈220` bits, so generic twist-DLP is `≈ √Q < 2¹¹⁰` — **below** the
  curve's `2¹²⁸`.

So the `128`-bit figure is contingent on **point validation**: `x`-only secp256k1 code that
skips it inherits `~110`-bit twist security and small-subgroup confinement. This is a
limitation certificate, and the reason ECDH/ladder implementations must check the point is on `E`.

## Honest ledger

| Claim | Status |
|---|---|
| Any **classical generic** algorithm needs > `2^127` group ops | **THEOREM** (kernel-verified core + corollary) |
| Matching `O(√n)` upper bound (rho, BSGS) ⇒ `Θ(√n)` | **THEOREM** |
| `n` prime, huge embedding degree, ordinary, prime field | **THEOREM** (parameter checks) |
| Twist order `= 3²·13²·3319·22639·Q`, `Q` a 220-bit prime; twist security `≈2¹¹⁰ < 2¹²⁸`, nontrivial cofactor | **THEOREM** (`secp256k1_twist_security_profile`; ⇒ `x`-only code must validate points) |
| No **non-generic** classical algorithm beats `√n` on the concrete curve | **ASSUMPTION** — open; best known attack is generic rho at ≈ `2^128.3` |
| Security against **quantum** adversaries | **FALSE** (Shor) |

## Scope of the kernel verification itself

What Lean checked is the **deterministic combinatorial core**: the model's assumptions enter as
hypotheses (the algorithm's knowledge = the collision pattern of injectively-formed affine
forms), not as conclusions derived from a formalized random-encoding adversary; Shoup's adaptive
probabilistic wrapper is standard on paper but **not** in the kernel. Primality of `n` enters as
`[Fact n.Prime]`; `2^255 < n` uses `native_decide` (extending trust to the Lean compiler). None
of this affects the mathematics — it bounds what "kernel-verified" covers.

**Bottom line.** `Ω(√n)` is a *real, proven* lower bound **for black-box (generic), classical
algorithms** — which happens to include every attack currently known against secp256k1 — and a
*well-tested-but-unproven* bound against all classical algorithms (provably false against quantum
ones). The Lean kernel adds certainty about the theorem *inside the model*, and none about the
model matching reality. That residual gap is where secp256k1's security stops being mathematics
and becomes a well-audited bet.
