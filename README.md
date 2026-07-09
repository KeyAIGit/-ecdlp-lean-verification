# ECDLP Lean formalization (v0)

![Verified theorems](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json)

Machine-checked layer for the ECDLP knowledge graph (corpus folder 15_Knowledge_Graph,
formalization table 07_Formalization/KG_CLAIM_FORMALIZATION_v1.csv).

## Live stats (machine-readable)
The verified-theorem counts are published as JSON, regenerated automatically from
`VERIFIED.md` on every merge to `main` (`.github/workflows/docs-sync.yml` +
`scripts/gen_stats.py`). Fetch them from a site or dashboard via the raw URLs:
- **Full stats:** `https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/data/stats.json`
- **Shields badge endpoint:** `https://raw.githubusercontent.com/KeyAIGit/-ecdlp-lean-verification/main/badges/theorems.json`

`data/stats.json` exposes `ledger_rows`, `distinct_results`, `proved_modules`,
`sorry_count` (0), and `custom_axioms` (0). No scraping of markdown needed.

## Layout
- `REPOSITORY_ARCHITECTURE.md` - repository-level map: canonical sources,
  generated artifacts, public surfaces, Research OS controls, and cleanup
  candidates. Machine-readable companion: `repo/ARTIFACTS.yaml`.
- `Ecdlp/Secp256k1Verified.lean` - PROVED on Lean core alone (no Mathlib). 8 theorems
  verified with `native_decide`:
    - `p_special_form`        : p = 2^256 - 2^32 - 977            [sec2-secp256k1-field-005]
    - `glv_lambda_eigenvalue` : lam^2 + lam + 1 ≡ 0 (mod n)        [glv-subgroup-eigenvalue-006]
    - `lambda_is_cube_root`   : lam^3 ≡ 1 (mod n)
    - `beta_field_eigenvalue` : beta^2 + beta + 1 ≡ 0 (mod p)
    - `beta_is_cube_root`     : beta^3 ≡ 1 (mod p)
    - plus `lambda_ne_one`, `lam_lt_n`, `beta_lt_p`
- `Ecdlp/Lagrange.lean` - Mathlib proof that element order divides finite group order.
- `Ecdlp/Statements.lean` - Mathlib-dependent formalization targets. The current ZMod target is closed with no `sorry`.
- `Ecdlp/Proved/` - promoted, machine-checked theorems (built and gated). **See the
  directory itself for the full, current module list** (torsion `E[n]`, division
  polynomials Ψ₂–Ψ₄, the GLV endomorphism object — proved an *additive* endomorphism
  (`glvHom`); the cryptographically load-bearing `[λ]` eigenvalue identity
  `glvPoint = [λ]` is **not** proved (open, see `TRUST_REPORT.md`/`ABSTRACT_SCOPE.md`) —
  curve invariants, anomalous-scope, collision/solve-step, …); the items below are
  illustrative, not exhaustive. Includes a **verified discrete-log protocol algebra**
  (abstract completeness/soundness *identities* over `[Module (ZMod n) G]` / `[Field F]` —
  not proven security of deployed protocols; see `ABSTRACT_SCOPE.md`):
    - `GenericGroupBound.lean` - Shoup/Nechaev generic-group `Ω(√p)` lower bound for
      the discrete log (first such in Mathlib); model-soundness lemmas.
    - `BabyStepGiantStep.lean`, `PollardRho.lean` - matching `O(√n)` upper bounds, so
      generic DLP is `Θ(√n)`.
    - `Secp256k1GenericSecurity.lean` - secp256k1 ≥128-bit **classical, generic** security
      (`2^127 < q`; black-box model only — says nothing about non-generic attacks, and is
      classical: Shor breaks ECDLP quantumly. See `notes/SECURITY_SCOPE.md`).
    - `SchnorrSoundness.lean` - Schnorr 2-transcript extractor (a linear-algebra identity in
      the scalar field — no adversary/probability); the "Pedersen binding ⇒ DLP" implication
      is *narrated*, not formalized (the trapdoor is an uninterpreted field element — see
      `ABSTRACT_SCOPE.md`).
    - `DlogCompleteness.lean` - Schnorr/EdDSA verification; Diffie–Hellman agreement.
    - `DlogPrimitives.lean` - ElGamal decryption; Pedersen homomorphism.
    - `DlogAdvanced.lean` - Okamoto 2-witness extraction; Chaum–Pedersen DLEQ.
- `Ecdlp/Targets/` - open conjecture stems (one `sorry` each); **not** built and **not**
  gated, so the "green build = all proved" invariant holds. See each folder's README.
- `data/` - read-only knowledge-graph corpus consumed by the Layer 3 generator.
- `VERIFIED.md` - ledger mapping claim IDs to verified Lean theorem names and files.
- `BARRIERS.md` - formalization-status registry: what of the corpus is provable
  now vs blocked, and which Mathlib foundations are missing (the no-go map).

## Build
Core verified file (no Mathlib):
    lean Ecdlp/Secp256k1Verified.lean
Full project incl. Mathlib targets:
    lake exe cache get && lake build
Toolchain pinned in `lean-toolchain` (Lean v4.31.0); Mathlib rev pinned in `lakefile.toml`.

## Autonomous engine
The scaffolded loop — **discover → attempt → draft PR** — is
`.github/workflows/autonomous-engine.yml`. In practice the proofs that land come from the
zero-cost **tactic ladder** plus **human-in-loop** promotion; external model-provers
(Pythagoras-4B → Goedel-V2-32B) have been *attempted with 0 accepted*. See
**`notes/ENGINE.md`** for how it works,
its safety model (draft-only, kernel-judged, budget-capped), the one-time secret setup that
turns it on, and an honest account of what it does autonomously vs what still needs
orchestration.

## Pipeline role
This is stage 2 (formalization agent output) of the autonomous research mechanism.
Each `formalizable` claim in KG_CLAIM_FORMALIZATION_v1.csv becomes a theorem here;
`native_decide` handles concrete arithmetic facts, Mathlib handles structural ones.

Current ledger: **0 `sorry`, 0 open obligations, no custom axioms** (machine-enforced by
the axiom-audit gate; `native_decide` facts additionally trust the compiler — see
`TRUST_REPORT.md`). For the live row & distinct-result count see **`STATUS.md`** /
`data/stats.json` — not duplicated here to avoid drift.
Beyond the corpus, the project hosts:
- a verified discrete-log **protocol algebra** (generic hardness + protocol
  completeness/soundness *identities* over an abstract module/field — not a security model
  for deployed protocols, see `ABSTRACT_SCOPE.md`), including the rho/BSGS **solve step**
  (collision ⇒ discrete-log recovery);
- the **saturated classical attack landscape**: Pohlig–Hellman, anti-MOV/FR
  (embedding degree > 100), anti-Smart/SSSA + supersingular (trace of Frobenius);
- secp256k1 grounded as a Mathlib `EllipticCurve` with **machine-checked primality**
  of `p` and `n` (full Pratt certificates), and a **division-polynomial / torsion**
  foundation (`Ψ₂Sq`, `Ψ₃`, 2-torsion bridge, `#E[2] ≤ 4`) — see
  `notes/FOUNDATIONS.md` for the roadmap toward the Weil pairing;
- a machine-readable **knowledge graph** (`data/knowledge_graph.json` + rendered
  `.md`) indexing every theorem, its dependencies, and the formalization barriers.

## Authorship & AI disclosure
The human maintainer is the author and bears intellectual responsibility for every
claim of novelty and significance; correctness of each listed theorem is guaranteed
by the Lean kernel. AI tooling (assistant models for formalization, code, and
proof search) was used as an aid — it is disclosed here and is not an author. CI-bot
commits are git metadata, not authorship. License and the final author list are set
by the maintainer.
