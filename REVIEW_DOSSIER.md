# REVIEW DOSSIER — ECDLP Lean verification (independent-review packet)

> **Historical snapshot.** This dossier reflects the ledger as it stood at review time
> (**~105 distinct / ~114 rows**); those figures are frozen here on purpose as the record the
> reviewers acted on. They are **not** current. The single canonical, live figure is **`STATUS.md`**
> (generated from `data/stats.json`); today's ledger is larger. Read the analysis below for the
> *reasoning*, not the counts. This file is intentionally excluded from the count-drift gate.

This is an honest, de-inflated synthesis of five adversarial reviews (Correctness & Soundness, Novelty & Significance, Claims & Count Integrity, GLV Endomorphism deep-audit, Strategy & Trajectory) prepared for an independent GPT reviewer to act on. **State of project, plainly:** the kernel-checked core is genuinely sound — there are **0 `sorry`, 0 `admit`, 0 axioms** in any built file (`Ecdlp/Proved/*` and the base layer; the only `sorry` strings live in `Ecdlp/Targets/*` stems and in prose/README, and `Ecdlp/Targets/*` is verifiably never imported from `Ecdlp.lean`, confirmed lines 1–39). CI-green therefore means every built theorem is fully proved with no axioms. The honest headline ledger size is **~105 distinct named results** (≈114 literal table rows before merging alternate-form restatements; the previously-circulated **128 is a retracted over-count** — see final section). The freshly-completed GLV endomorphism object (`glvPoint_add`, `Ecdlp/Proved/GlvHom.lean:41`, finished Jun 30) is real, non-trivial mathematics with full branch analysis and no `sorry` — but it proves only the *homomorphism half* (additivity), not the cryptographically load-bearing `glvPoint = [λ]` eigenvalue property, which remains an open stem. The substantive-vs-scaffolding ratio is roughly **10–15% substantive, ~85% routine** verified engineering; the autonomy/server/Featherless apparatus has produced essentially **zero** novel mathematics and is the project's largest credibility liability.

## What is actually verified

Grouped by pillar, faithfully and without inflation:

- **Primality of the actual secp256k1 field & group order (the strongest deliverable).** Full Pratt certificates for `p = 2^256 − 2^32 − 977` and for the group order `n`, discharging `[Fact p.Prime]` / `[Fact n.Prime]` genuinely (Mathlib `lucas_primality`, recursive descent to verified factors, `native_decide` only on small arithmetic inside the Lucas argument). The decimal in `Secp256k1PrimeP` matches the hex `p` and `2^256−2^32−977` exactly; the `n` instance is at `Ecdlp/Proved/Secp256k1PrimeN.lean:186`. Mathlib lacks these — this is the most reusable artifact.
- **secp256k1 as a Mathlib `EllipticCurve` instance** (`j = 0`, `a₁=a₂=a₃=a₄=0`, `Δ ≠ 0`), a modest but real instantiation (`Ecdlp/Proved/Secp256k1Curve.lean`).
- **Generic-group lower bound — combinatorial core only.** `generic_dlog_query_bound` / `generic_success_le` (`Ecdlp/Proved/GenericGroupBound.lean:118–201`) prove the information-theoretic heart of the Shoup/Nechaev bound (`p ≤ q·q` from affine-form collision counting). Not in Mathlib; the single best result in the repo. It is **not** the full Shoup theorem (no adversary/random-encoding/probability model — disclosed in-file, lines 33–38).
- **GLV endomorphism — homomorphism half only.** `glvPoint_add` (`Ecdlp/Proved/GlvHom.lean:41`) proves `glvPoint(P+Q) = glvPoint P + glvPoint Q` for all `P,Q` with exhaustive branch analysis (infinity branches, `P=−Q` vertical via `add_of_Y_eq`, general secant/tangent via `secp256k1_glv_slope`). The β-equivariance lemmas (`secp256k1_glv_slope/addX/addY`) are honest `β³=1` polynomial identities. The defining property `glvPoint = [λ]` is **not** proved.
- **secp256k1 ≥128-bit generic security (conditional, properly scoped).** `secp256k1_generic_security` (`Ecdlp/Proved/Secp256k1GenericSecurity.lean:27–31`) proves `2^127 < q` under `[Fact n.Prime]`. The prose hedges this to *generic* algorithms — this is honest and defensible.
- **Attack-boundary facts (mostly `native_decide` on 256-bit constants).** Embedding degree > 100 (`EmbeddingDegree.lean:34`), trace of Frobenius `t = p+1−n` with `t≠0,1` and `t²≤4p` (`TraceOfFrobenius.lean:33–37`), β/λ eigenvalues, BSGS `⌈√n⌉ ≤ 2^128+1`. These are textbook consistency facts about the curve, kernel-checked but compiler-trusting.
- **Mathlib re-exports / textbook wrappers.** `E[n]=ker[n]`, Lagrange, cofactor, division-polynomial invariants `b₂..b₈`, `Ψ` degrees, torsion lemmas. Valuable verified engineering, not new mathematics.
- **Discrete-log "protocol algebra" (scaffolding).** ~25–30 one-line identities over an abstract `[Module (ZMod n) G]` / `[Field F]` (Schnorr/EdDSA, DH, ElGamal, Pedersen, Okamoto, Chaum-Pedersen, MuSig2, Taproot, Feldman VSS, adaptor/blind Schnorr). Correct algebra; **never instantiated at secp256k1**, no hashing/adversary/probability/security definition.

## Adversarial findings

Merged, deduplicated, ranked most-severe first. No softening.

### 1. [HIGH] The "discrete-log cryptography library" is abstract algebra mislabeled as cryptography
Every protocol theorem is a one-liner over an arbitrary module/field, never instantiated at the secp256k1 point group, with no adversary, hash, probability, or security definition. `schnorr_verify` is `subst; rw[add_smul,mul_smul]`; `taproot_tweak_verify` is `module`; `dh_agree` is `mul_comm`. "Special soundness" cryptographically means an extractor reducing to DL-hardness; what is proved is that `(s1−s2)/(c1−c2)` solves a linear equation — true in *any* field, including ones where DL is trivial.
**Evidence:** `Ecdlp/Proved/DlogCompleteness.lean`; `Ecdlp/Proved/SchnorrSoundness.lean:27–33` (`schnorr_extract`); VERIFIED.md:133 ("soundness/completeness of deployed protocols").
**Verdict: REAL over-claim (honest-but-irredeemably-mislabeled).** The proofs are sound; the *labels* are crypto over-claims. Not publishable as crypto formalization. Relabel each row as "algebraic identity underlying X."

### 2. [HIGH] GLV "object completed" overstates: only the homomorphism half exists; `glvPoint = [λ]` is an open `sorry`
VERIFIED.md and `GlvHom.lean:28–30` call `glvPoint` "a bona fide endomorphism of the secp256k1 point group" and "completes the GLV object," and `GlvEndomorphism.lean:10–12` says it "acts as scalar multiplication by `λ` on the base-point subgroup." Additivity is genuinely proved. But (a) it is **not** packaged as a Mathlib `AddMonoidHom` (grep for `AddMonoidHom`/`→+` in `Ecdlp/Proved/Glv*.lean` returns nothing), and (b) the `glvPoint = [λ]` property — the whole cryptographic point of GLV — is proved **nowhere**: the only λ-action statement is `glv_root_mod_n_condition` (`Ecdlp/Targets/glv_root_mod_n_condition_008.lean:14`), which ends in `sorry`, and that stem is the *abstract* eigenvector-propagation lemma, not the curve-specific `glvPoint G = λ•G` eigenvalue fact (which is absent entirely — grep for `glvPoint` alongside `λ •`/`smul` across `Ecdlp/Proved` returns nothing).
**Evidence:** `Ecdlp/Proved/GlvHom.lean:41` (additivity, real); `GlvHom.lean:28–30`, `GlvEndomorphism.lean:10–12` (over-claiming prose); `Ecdlp/Targets/glv_root_mod_n_condition_008.lean:14` (`sorry`).
**Verdict: REAL — most important novelty gap.** No false theorem is built (the ledger row correctly scopes to "is additive"), but the source-file/notes narrative conflates "is an additive endomorphism" (proved) with "is `[λ]` on `⟨G⟩`" (entirely open). Genuinely-new-but-partial, narratively oversold as finished.

### 3. [HIGH] The reviewer summary "128 theorems" is a known-incorrect, already-retracted figure
128 is reachable only by counting the ~22 internal recursive Pratt sub-lemmas individually — a convention VERIFIED.md itself now disavows (lines 130–131). Sending "128" externally re-asserts the exact inflation the project already retracted and contradicts every current in-repo number.
**Evidence:** VERIFIED.md:130–131 (disavows 128); git `0289864` ("ledger 127 → 128").
**Verdict: REAL and live.** Do **not** send 128. Honest figure: "~105 distinct results (≈114 ledger rows), 0 sorry, 0 axioms."

### 4. [HIGH] Four-way internal count inconsistency for the same body of work
The same ledger is reported as ~99 (`README.md:50`, `AGENTS.md:23`, `BARRIERS.md:16`), simultaneously ~105 **and** ~99 in the *same VERIFIED.md paragraph* (lines 126 vs 131), 108 in `data/knowledge_graph.md:5` (stale, last built at `0289864`, missing the 6 newest GLV theorems), and ~114 literal table rows. A reviewer cross-checking concludes the bookkeeping is unreliable.
**Evidence:** VERIFIED.md:126 ("~105") vs VERIFIED.md:131 ("~99 … honest headline"); `README.md:50`, `AGENTS.md:23`, `BARRIERS.md:16` ("~99"); `data/knowledge_graph.md:5` ("108 theorems"); `glvPoint_add` absent from `knowledge_graph.json`.
**Verdict: REAL internal contradiction** in the file designated "canonical source of truth" (VERIFIED.md:127). Lines 126 and 131 cannot coexist; one must be corrected and propagated.

### 5. [HIGH] The autonomy/prover apparatus has produced zero novel mathematics
By git evidence, 100% of the genuinely novel math came from the interactive dev agent (the GLV ladder is a burst of hand-driven commits, Jun 28–30). The single "server-proved" result (`anomalous_iff_trace_one`) was closed by plain `omega`, which CI runs in seconds anyway. The Featherless paid tier has **never** returned a proof (permanent HTTP 403); the rented server OOMs at 4GB. Worse, after the prior review flagged this, commit `5097485` **added** more server apparatus (a 24/7 daemon) rather than cutting it.
**Evidence:** commit `d3072cc` ("server-proved" via Tier-0 `omega`); `scripts/prover_loop.py:185`; `notes/ARCHITECTURE.md:29`, `AGENT_ORCHESTRATION.md:86–87` (403/OOM); commit `5097485` (added `prover_daemon.sh`).
**Verdict: REAL and material.** Harms credibility/signal, not soundness. The "autonomous research org" narrative (Layer-1/2/3, mermaid diagrams, SERVER_RUNBOOK, AGI north-star) is the loudest AI-padding tell precisely because the autonomy demonstrably produced ~one `omega` result. Cut the stack; keep only the CI kernel gate.

### 6. [MEDIUM] Generic-group bound is the combinatorial *core*, not "the" Shoup/Nechaev bound
`hsolve` (collisions determine the log) and `hgen` ("A constant off badSet F") are assumed idealizations, not derived from any adversary/oracle/random-encoding model; there is no probability space and the forms `F` are fixed (non-adaptive). The unhedged "first Mathlib-checked Ω(√p) lower bound" in `README.md:23` and `BARRIERS.md:47` implies the full theorem.
**Evidence:** `Ecdlp/Proved/GenericGroupBound.lean:118–131`, `152–178`; in-file scope note `33–38`.
**Verdict: SOUND, best result in the repo, honestly scoped in-file — but the README/BARRIERS "first such" needs the qualifier "the combinatorial/information-theoretic core of."** Crucially the hypotheses do **not** smuggle the conclusion (conclusion is a cardinality bound; hypotheses are about collision structure). Borderline-publishable as a short note if reframed.

### 7. [MEDIUM] `#E(𝔽_p) = n` is taken as definitional; "ordinary/non-anomalous" is conditional
`secp256k1_trace_ordinary_nonanomalous` defines `t = p+1−n` and checks `t≠0, t≠1, t²≤4p`, but takes `#E = n` as input. There is no formalized point-counting (Schoof absent from Mathlib). The Hasse check is a consistency sanity-check, not a proof that `#E = n` with cofactor 1.
**Evidence:** `Ecdlp/Proved/TraceOfFrobenius.lean:30,33–37`; VERIFIED.md:75.
**Verdict: SOUND as a conditional theorem; over-stated in the VERIFIED.md headline.** The "disclosed boundary node" framing is the honest standard, but the headline "ordinary, non-anomalous" reads as an established curve property. Flag the conditionality explicitly in VERIFIED.md.

### 8. [MEDIUM] Weil-pairing "summit" mis-scheduled as "months"
Ranked #1 by leverage (49 claims) and tagged "months," but it is definition-blocked behind divisors/function-fields/Miller's algorithm absent from Mathlib v4.31 and open in the human Mathlib community for years.
**Evidence:** `notes/FOUNDATION_ROADMAP.md:47–52`; `FOUNDATIONS.md:63–68`; `BARRIERS.md:67–73`.
**Verdict: partly honest (notes disclaim closeness), partly over-stated.** "Months" and leverage-ranking an unstartable target are category errors. Restate as "out of scope; contribution is the gap map"; rank by leverage-per-tractable-effort.

### 9. [LOW] `native_decide` enlarges the TCB beyond the kernel CLAUDE.md claims is "the only judge"
~33 load-bearing 256-bit facts (`p_special_form`, β/λ eigenvalues, `embedding_degree_gt_100`, trace, `2^255<n`, BSGS sqrt) are `native_decide`-only, trusting the Lean compiler. CLAUDE.md's "the Lean kernel is the only judge" is technically false for these rows, and VERIFIED.md does not disclose this caveat.
**Evidence:** `Secp256k1GenericSecurity.lean:21,49`; `EmbeddingDegree.lean:34`; `TraceOfFrobenius.lean:37`; `Secp256k1Verified.lean:8`.
**Verdict: ACCEPTABLE trade-off, honestly fixable.** Mitigation is correct where it matters most — primality structures `native_decide` to discharge only small checks inside a kernel-checked Lucas argument. Add a one-line TCB disclosure to VERIFIED.md.

### 10. [LOW] No-sorry gate has a latent hole (process-risk, not present defect)
The CI gate greps `*.lean` under `Ecdlp/` excluding `Targets/`. `sorry` is a Lean *warning*, not an error, so if a built file ever did `import Ecdlp.Targets.frontier_*`, `lake build` would stay green **and** the grep would skip `Targets/` — the `sorry` would reach the built graph undetected. Today `Ecdlp.lean` imports zero `Targets` modules (verified, lines 1–39), so no defect exists now.
**Evidence:** `.github/workflows/ci.yml` (`--exclude-dir=Targets`); `Ecdlp.lean:1–39`; every `Ecdlp/Targets/*` carries a `sorry`.
**Verdict: SOUND today; cheap fix.** Have the gate additionally assert no built file contains `import Ecdlp.Targets`.

### 11. [LOW] Several "soundness/extraction" theorems are trivial ring identities in heavy crypto prose
`adaptor_extract` (`t = s − s'` from `s = s'+t`) and `blind_unblind` (`s = s'+α` from `s' = s−α`) are `rw [h]; ring`, dressed in atomic-swap/Lightning/e-cash prose. The genuinely substantive `schnorr_extract` is real; these riders are not.
**Evidence:** `Ecdlp/Proved/SchnorrSoundness.lean:63–64, 70–71`; VERIFIED.md:58–59.
**Verdict: SOUND but ROUTINE.** Prose inflates trivial field arithmetic into named protocol-soundness results. The file is honest that it is all scalar-field; relabel.

### 12. [LOW] `anomalous_iff_trace_one` is a tautological `omega` restatement, named as a security result
With universally-quantified `p N a_p` and hypothesis `N = p+1−a_p`, it proves `N=p ↔ a_p=1` by `omega`. It mentions secp256k1 nowhere and restates its own hypothesis, yet is presented as the "Smart/SSSA attack boundary."
**Evidence:** `Ecdlp/Proved/AnomalousScope.lean:23–26`; VERIFIED.md:116.
**Verdict: SOUND but vacuous-leaning/inflationary.** A correct, honestly-stated helper, but it adds a named ledger row reading as a security result.

### 13. [LOW] Formalizable-now backlog is routed to the dead daemon; some open targets are Mathlib renames
`FOUNDATION_ROADMAP.md:64–65` routes the near-term backlog to a daemon that can't run it; `Ecdlp/Targets/` includes `frontier_orderOf_one`, `frontier_card_pos`, `frontier_pow_card_eq_one` — Mathlib one-liners indistinguishable from Mathlib itself.
**Evidence:** `FOUNDATION_ROADMAP.md:64–65`; `Ecdlp/Targets/frontier_*.lean`.
**Verdict: REAL, lower-stakes.** Drop generic group-theory renames; keep only targets that tie to secp256k1 specifically.

### 14. [LOW] Code-quality smell: β²+β+1=0 re-derived by copy-paste in four GLV files
Identical `hβeig` blocks in `GlvEndomorphism.lean:33–39,63–69`, `GlvHom.lean:45–50`, `GlvSlope.lean:37–43`, plus `beta_cubed_eq_one` in `GlvAddFormula.lean:28–37`.
**Verdict: not a correctness risk** (every copy is kernel-checked) — a maintainability smell that slightly inflates apparent proof volume. One shared lemma fixes it.

## Honest self-assessment

**Substantive-vs-scaffolding ratio: ~10–15% substantive, ~85% routine.** The GLV work does not move this ratio. Of ~105 named results, the defensibly-substantive set is **~5–8**: Pratt `p`, Pratt `n`, the secp256k1 `EllipticCurve` instance, the generic-bound combinatorial core, and `glvPoint_add`.

- **Genuinely novel / reusable:** the two Pratt certificates for the actual secp256k1 `p` and `n` (Mathlib lacks them — the single most useful deliverable); the generic-group combinatorial core (not in Mathlib); `glvPoint_add` (delicate full-branch affine slope arithmetic over Mathlib's `WeierstrassCurve.Point` — the most substantive *new* proof, even though it is only the homomorphism half).
- **Routine:** ~33 `native_decide` concrete facts, direct Mathlib re-exports (torsion, Lagrange, cofactor, division-polynomial invariants), and the ~25–30 abstract protocol identities. Valuable verified engineering and textbook facts, not new mathematics.
- **Where overclaiming risk lives (the four labels a hostile reviewer will single out):** (1) "verified discrete-log cryptography library" / "soundness of deployed protocols" — it is abstract algebra never instantiated at secp256k1; (2) "completes the GLV object" — only additivity, not `[λ]`; (3) "first Ω(√p) lower bound" — only the combinatorial core, no adversary model; (4) the "autonomous research org / verified base for a future AGI" narrative — never operationalized, and the autonomy produced ~one `omega` result, so the prose-to-novel-math ratio is upside-down.

**No single result is a standalone publication.** A workshop/tool paper is plausible only if every over-claiming label is stripped to what the kernel checked: a hand-built (AI-assisted), kernel-verified secp256k1 cryptography + attack-boundary library, plus a precise no-go map of the missing Mathlib foundations for ECDLP cryptanalysis.

## Trajectory & next 5 moves

Prioritized, highest-EV first.

1. **Delete the autonomy stack that produces nothing.** Remove `prover_daemon.sh`, `SERVER_CONNECT.md`, `SERVER_RUNBOOK.md`, `server-*.yml`, the Featherless tier. Keep **only** `ci.yml` (the kernel gate) + the human-merge PR flow. This removes the single biggest AI-padding attack surface and costs no verified theorems.
2. **Sweep to ONE canonical count and close the bookkeeping hole.** Adopt "≈114 ledger rows / ~105 distinct results" with an explicit merge rule, propagate to README/AGENTS/BARRIERS/VERIFIED honesty-note, rebuild `knowledge_graph.json` from current VERIFIED.md, delete 99/108/128 everywhere, and add a CI check that fails on count drift. Fix VERIFIED.md:126-vs-131 first.
3. **Finish the GLV object honestly.** Bundle `glvPoint` as an `AddMonoidHom` via `AddMonoidHom.mk'` (`glvPoint_zero` + `glvPoint_add` already exist — ~10 lines, low risk), then attack the *real* missing ingredient `glvPoint G = λ•G` (curve-specific eigenvalue) and close `glv_root_mod_n_condition_008` properly — **not** as a `sorry`. Relabel the ledger row to "φ is additive (homomorphism half; φ=[λ] not yet established)" until both are done.
4. **Hand-prove the rung-4 general division-polynomial ↔ point-order equivalence** `ψₙ(x_P)=0 ⟺ [n]P=O` for general `n` (`FOUNDATIONS.md:56–60`): the first genuinely-hard-but-*bounded* novel target reachable without a missing Mathlib definition — higher value than ten leaf rows.
5. **Write up the generic-group Θ(√n) core + the attack-boundary map** (`embedding_degree>100`, `trace≠0,1`, Pratt p/n) as a short formal-methods note / Mathlib-PR candidate, and **demote the Weil pairing** from "scheduled #1 / months" to an explicit "out-of-scope gap map."

## Concrete questions for the GPT reviewer

1. **Canonical count.** Endorse "≈114 ledger rows / ~105 distinct results" with a stated merge rule as the single headline (eliminating 99/108/128), and should the ~9 "supporting:"/alternate-form rows be visually tagged so the distinct count is reproducible by anyone? Is a CI count-drift check worth adding given this drift has recurred twice?
2. **Generic-group bound.** Is it defensible to call `generic_dlog_query_bound` "the Shoup/Nechaev Ω(√p) bound," or — without an adversary/random-encoding/probability model — must it be reframed as "the information-theoretic core of"? Where exactly is the line between "the combinatorial core of" and "is" the bound? Would a referee accept the core as a first Mathlib formalization at all?
3. **GLV completion.** To prove `glvPoint = [λ]` on `⟨G⟩`, the missing concrete fact is `glvPoint G = λ•G` for the secp256k1 generator (an eigenvalue identity on the *curve group*, not just `β²+β+1=0` in 𝔽_p). Is this provable by `native_decide` on coordinates, or does it require division-polynomial/torsion machinery — and is *that* the true bottleneck rather than the cyclic-propagation stem `glv_root_mod_n_condition_008`? Is there a risk that closing that abstract stem gives a false sense of completing the `[λ]` claim?
4. **Bundling order.** Given `glvPoint_zero` and `glvPoint_add` both exist, is `AddMonoidHom.mk'` the right minimal next move, or should `glvPoint` be *defined* as an `AddMonoidHom` so `map_add` comes for free? Which ordering better serves any downstream pairing/decomposition use?
5. **Substantive count.** Of the five candidate-substantive results (Pratt p, Pratt n, `EllipticCurve` instance, generic-bound core, `glvPoint_add`), which is the strongest standalone contribution to upstream Mathlib? Is the Pratt machinery for secp256k1 p/n actually novel relative to existing Mathlib primality tooling (`norm_num`/Pratt), or subsumed? Does the soundness lens confirm or revise the ~10–15% substantive estimate?
6. **Protocol library.** Is there *any* framing under which the abstract-module protocol identities count as a contribution (e.g., a reusable "discrete-log protocol algebra" interface), or is it irredeemably scaffolding because it is never instantiated at secp256k1 and encodes no security definition?
7. **Conditional boundary nodes.** Does taking `#E(𝔽_p)=n` as definitional (no Schoof in Mathlib) make `secp256k1_trace_ordinary_nonanomalous` and the cofactor/order facts conditional in a way that *must* be flagged in VERIFIED.md, or is the disclosed "verified boundary node" framing the honest standard?
8. **Gate hardening.** Should the no-sorry gate additionally assert that no built file imports `Ecdlp.Targets` (closing the warning-not-error hole, given `sorry` stays green and the grep skips `Targets/`)?
9. **Strategy.** Do you agree with the next-5-moves ranking, and would you swap move 3 (finish GLV) and move 4 (rung-4 division polynomial)? Is there a defensible reason to keep *any* orchestration machinery beyond the CI gate? Of the four AI-padding tells (renamed group-theory leaf rows; the autonomy narrative; "Weil pairing months away"; the unoperationalized AGI north-star), which is most lethal to fix first?

## Note on the "128" figure

**Do not send "128 theorems" to any reviewer.** 128 is a retracted over-count: it arises only by counting the ~22 internal recursive Pratt-certificate sub-lemmas as individual theorems — a convention VERIFIED.md itself now explicitly disavows (lines 130–131). The honest, defensible figure to propagate everywhere (README:50, AGENTS:23, BARRIERS:16, the VERIFIED.md:131 honesty-note, and a freshly rebuilt `knowledge_graph.json`) is: **≈114 named ledger rows / ~105 distinct kernel-verified results (after merging alternate-form/supporting restatements), 0 `sorry`, 0 axioms.** Also correct the live self-contradiction in VERIFIED.md, where line 126 says "~105" and line 131 says "~99" for the same table, and the stale "108" in `data/knowledge_graph.md:5`.
