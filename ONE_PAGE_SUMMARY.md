# ECDLP Lean verification — one-page external summary

> Counts here are a snapshot; the single canonical figure is **`STATUS.md`** (generated from `data/stats.json`). If they differ, STATUS.md wins.

A hand-built, AI-assisted, kernel-verified Lean 4 + Mathlib library about the
secp256k1 elliptic curve and the boundary of the classical attacks on its discrete-log
problem. **242 ledger rows / ~204 distinct kernel-verified results** (38 rows are
alternate-form or supporting restatements of the same fact). **0 `sorry`, 0 `admit`,
0 open obligations.**

**Trust base (precise).** No result depends on any *custom* axiom or on `sorryAx`. The
only axioms anything depends on are Lean/Mathlib's standard `{propext, Classical.choice,
Quot.sound}` — used by essentially every Mathlib proof. Results proved by `native_decide`
(~33 concrete 256-bit arithmetic facts) **additionally trust the Lean compiler** via the
`Lean.ofReduceBool` axiom — a real extension of the trusted computing base, not a
formality. This is machine-enforced: the axiom-audit CI gate (`Ecdlp/AxiomAudit.lean` +
`scripts/check_axioms.py`) fails the build if anything depends on an axiom outside this
whitelist.

---

## For a Lean / formal-methods expert

**Genuinely substantive results (~5–8):**
- **Pratt primality certificate for `p = 2^256 − 2^32 − 977`** (the secp256k1 field
  prime) — full recursive certificate discharging `Fact p.Prime`. Mathlib lacks this.
- **Pratt primality certificate for `n`** (the group order) — same, discharging
  `Fact n.Prime`. These two are the most reusable artifacts in the repo.
- **Generic-group DLP lower bound — combinatorial core** (`generic_dlog_query_bound`,
  `p ≤ q·q`): the information-theoretic heart of the Shoup/Nechaev `Ω(√p)` bound, via
  affine-form collision counting over `ZMod p`. Not in Mathlib. It is **not** the full
  Shoup theorem — there is no adversary / random-encoding / probability model (disclosed
  in-file).
- **secp256k1 as a Mathlib `EllipticCurve` instance** (`j = 0`, `Δ ≠ 0`), grounding the
  group law on the actual curve.
- **`glvPoint_add`**: the GLV map `(x,y) ↦ (βx, y)` is proved an **additive
  endomorphism** of the secp256k1 point group, with full affine-slope branch analysis
  (infinity, vertical `P = −Q`, secant, tangent), bundled as `glvHom : Point →+ Point`.
  The cryptographically load-bearing `glvPoint = [λ]` eigenvalue property is now **proved
  on all of ⟨G⟩** (`secp256k1_glvPoint_eq_lam_on_zmultiples`), via the weak keystone
  `addOrderOf G = n`; extending it to the **full** group `E(𝔽_p)` still needs `#E = n`.

**Routine Mathlib re-export / wrappers:** `E[n] = ker[n]`, Lagrange (`order_dvd_card`),
cofactor, division-polynomial invariants `b₂..b₈` and `Ψ₂/Ψ₃/preΨ₄` degrees, torsion
filtration lemmas. Verified engineering, not new mathematics. The ~25–30 discrete-log
"protocol" theorems (Schnorr, DH, ElGamal, Pedersen, Okamoto, Chaum–Pedersen, MuSig2,
Taproot, Feldman VSS) are one-line algebraic identities over an abstract
`[Module (ZMod n) G]` / `[Field F]`, encoding no security model — abstract algebra, not
cryptography. (They are now **also instantiated on the concrete curve subgroup ⟨G⟩**, and
`ZMod n ≃+ ⟨G⟩` is proved a group isomorphism — but that is the *bijection* underlying
ECDLP, still not a hardness/security theorem.)

**Honest substantive-vs-scaffolding ratio: ~10–15% substantive, ~85% routine.**

## For a strong generalist researcher

**What this IS:** a kernel-verified library pinning the concrete secp256k1 facts
(primality of `p` and `n`, the curve as an elliptic curve, `j = 0` / CM structure
behind GLV) and the *boundary* of the classical ECDLP attacks — generic-group `Θ(√n)`
hardness, no small embedding degree (MOV/FR resistance), non-anomalous / ordinary trace
of Frobenius (Smart/SSSA resistance), Pohlig–Hellman — **plus a precise no-go map** of
the Mathlib foundations still missing to formalize ECDLP cryptanalysis (Weil pairing,
p-adic / formal-group logs, Semaev polynomials, lattice reduction, point counting).

**What this is NOT:** not an attempt to break secp256k1; not a security-model
cryptography formalization (no adversary, hash, or probability model); the discrete-log
"protocol library" is abstract algebra, not a proof that deployed protocols are secure.
Several attack-boundary facts are *conditional* (e.g. `#E(𝔽_p) = n` is taken as
definitional, since Schoof point-counting is absent from Mathlib).

---

**Single next high-value move:** the GLV eigenvalue `glvPoint = [λ]` on `⟨G⟩`, the
`Module (ℤ/n)` structure, the protocol instantiation, and the `ZMod n ≃+ ⟨G⟩` discrete-log
isomorphism are now all proved on the crypto subgroup. The next honest rung is the **strong
keystone `#E(𝔽_p) = n`** (needs Hasse, absent from Mathlib), which would extend every one of
those from `⟨G⟩` to the whole point group `E(𝔽_p)`.

**Honest limitation:** the Weil pairing — highest-leverage missing foundation (it gates
MOV/Frey–Rück) — is out of scope. It is a multi-month, research-grade Mathlib
contribution that needs divisors / function fields / Miller's algorithm before `eₙ` can
even be *stated*. The contribution there is the gap map, not the pairing.
