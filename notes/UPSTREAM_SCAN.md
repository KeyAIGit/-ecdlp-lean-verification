# Upstream-existence scan — is it already formalized in Mathlib?

> **Dated research memory.** The exact 2026-07-22 source-tree audit is recorded
> in `repo/ECDLP_DECISION_SUBSTRATE.json`, including the pinned and observed
> Mathlib commits and the lexical-method caveat. Upstream PR status can change;
> this note does not authorize a port.

*Engine artifact.* An automated multi-agent scan (`upstream-existence-scanner` workflow) of
mathlib4 master + open PRs + Lean Zulip, for each open ECDLP target / barrier: does a Lean 4
formalization already exist (free import / stalled PR / genuinely nowhere)? This is the
repeatable generalization of the manual discovery that found the net-relation proof (PR #13155,
ported in `Ecdlp/Proved/NormEDSIsElliptic.lean`). Method: 8 read-only web-research agents +
synthesis. Every URL is agent-surfaced; the residual caveat is un-indexed private forks.

# Upstream-Existence Scan — ECDLP / secp256k1 Lean 4 Formalization

Synthesized from 8 per-topic findings. No links are invented; every URL below appears in the source findings. No topic was marked *unclear* — all verdicts are `none`/`partial` at stated-high confidence, so nothing carries a low-confidence flag (the only universal caveat is the un-surfaceable private-branch risk noted in several findings).

---

## 1. FREE PORTS / ADOPTABLE NOW
Things that exist in Mathlib master (hence already in pinned v4.31.0, adoptable by plain `import`) or in a portable open-PR form (transcribe/rebase, like the EDS net-relation port). Ranked by value ÷ effort.

| Rank | Object | Where | Effort | Value for ECDLP |
|---|---|---|---|---|
| 1 | **Division-polynomial `preΨ` / `ΨSq` / `Φ` infrastructure** (from the normalised EDS) | master: `Mathlib/AlgebraicGeometry/EllipticCurve/DivisionPolynomial/Basic.lean` + `Degree.lean` — https://leanprover-community.github.io/mathlib4_docs/Mathlib/AlgebraicGeometry/EllipticCurve/DivisionPolynomial/Basic.html (merged PRs #6703, #13399, #10878, #14063) | **Zero** — plain import | Valuable x-coordinate infrastructure. The audited `Basic.lean` still has a TODO for a bivariate `ωₙ`, and Mathlib does not supply the general point-`nsmul` bridge. |
| 2 | **Rank-1 elliptic divisibility sequences** — `IsEllSequence`, `IsEllDivSequence`, `normEDS` over ℤ | master: `Mathlib/NumberTheory/EllipticDivisibilitySequence.lean` — https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/EllipticDivisibilitySequence.html (PRs #10814, #13786) | **Zero** — plain import | Foundation for divisibility/torsion recurrences; underlies the division polynomials above. |
| 3 | **Weierstrass group law** — `WeierstrassCurve.Affine.Point` (also Projective/Jacobian) `AddCommGroup`, plus base-change (`WeierstrassCurve.map`) and variable-change | master: https://leanprover-community.github.io/mathlib4_docs/Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Point.html ; 2-torsion unit formulas in `Jacobian/Formula.lean`, `Projective/Formula.lean` | **Zero** — plain import | The group structure every ECDLP statement quantifies over; also lets you *instantiate* P-256 as a short-Weierstrass curve by transcription. |
| 4 | **Rank-1 net-relation layer** — `atom` / `atomRel` / `rel` / `IsEllipticNet := ∀ p q r s : ℤ, rel = 0`, with `map_*` naturality (the "recently-found net-relation port") | open PR #25989 (branch `Multramate:EllipticNet`) https://github.com/leanprover-community/mathlib4/pull/25989 ; groundwork PRs #13155 https://github.com/leanprover-community/mathlib4/pull/13155 , #13057 ; zsmul-via-ψₙ PR #13782 https://github.com/leanprover-community/mathlib4/pull/13782 | **Low** — PR-transcription onto v4.31 | Same class of port already adopted; a 4-index reformulation of Stange's net axiom. NB: rank-1 only — does *not* deliver general multi-index nets (see §3). |
| 5 | **Geometry-of-numbers primitives** — `ZLattice` / `Zspan` / covolume; Minkowski convex-body theorem + Minkowski bound | master: https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Module/ZLattice/Covolume.html ; https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/NumberField/Discriminant/Basic.html | **Zero** — plain import | Only foundation available for any lattice-attack side (bounds on short vectors); does *not* include LLL/SVP/CVP (see §3). |
| 6 | **`MvPolynomial` + resultants** (multivariate polynomial API) | master (referenced throughout Semaev/net findings) | **Zero** — plain import | Substrate for a from-scratch Semaev summation-polynomial construction. |

---

## 2. STALLED-UPSTREAM (exists but in an open/stalled PR)
Worth watching or actively helping land; adoption today means transcription, not `import`.

| Object | PR | Status / note |
|---|---|---|
| Elliptic-net (rank-1, ℤ-indexed net axiom) | #25989 — https://github.com/leanprover-community/mathlib4/pull/25989 | Open, principal EC contributor (Multramate). Continues **closed/superseded** #25030. |
| Net-relation groundwork (Junyan Xu / alreadydone) | #13155 — https://github.com/leanprover-community/mathlib4/pull/13155 ; #13057 | Open/stalled; the net-relation reformulation of EDS. |
| ℤ-smul via division polynomials (multiplication-by-n through ψₙ) | #13782 — https://github.com/leanprover-community/mathlib4/pull/13782 | Open. **Strategically important**: this is the missing link toward the torsion bridge in §3. |
| Elliptic-curve heights | #25986 — https://github.com/leanprover-community/mathlib4/pull/25986 (continues closed #15786 https://github.com/leanprover-community/mathlib4/pull/15786) | Open; unrelated to pairing/torsion but the active EC frontier. |

---

## 3. CONFIRMED BARRIERS (genuinely not formalized anywhere)
The real gaps — the publishable no-go map. Each is the *precise missing object*, absent from master, all surfaced PRs, and wider-GitHub Lean search.

| Missing object | Precise gap | Evidence of absence |
|---|---|---|
| **Weil pairing** | `e_n : E[n] × E[n] → μ_n` with bilinearity/alternation/non-degeneracy, **and** the structure theorem `E[n] ≅ (ℤ/n)²` | Repo code search `"Weil pairing"` = 0 hits; `Weil` surfaces only Mordell–Weil + surname. No divisors/function-field or Weil-reciprocity substrate present. |
| **Division-polynomial torsion bridge** | The equivalence **ψₙ(P) = 0 ⟺ P ∈ E[n]** (i.e. n·P = 0) | `partial` verdict: ψₙ defs exist (§1 #1) but no lemma linking ψₙ to the `Point` group law / mul-by-n. Needs #13782-style mul-by-n. |
| **Semaev summation polynomials** | `S_n` (recursive resultant construction) + property `S_n(x₁…xₙ)=0 ⟺ ∃ yᵢ, Σ(xᵢ,yᵢ)=O` | `"Semaev"` = 0 hits repo-scoped **and** all-of-GitHub Lean. Distinct object from division polynomials. |
| **General multi-index elliptic nets** | `IsEllipticNet` as a map from a **rank ≥ 2** free abelian group (ℤⁿ) with net recurrence + **subnet (sub-lattice) functoriality** | `IsEllipticNet`/`EllipticNet` = 0 hits in master; PR #25989 inspected directly and is rank-1 ℤ-indexed only. |
| **EC isogenies / endomorphisms / Frobenius** | An isogeny type / point-group `AddMonoidHom`; the **q-power Frobenius** endomorphism on E(𝔽_q); the general theorem *O-fixing rational map ⟹ group hom* | Master module index (`Mathlib.lean`) has no Isogeny/Endomorphism/Frobenius module; `AddSubMap.lean` is a heights x-coord map, not isogenies. |
| **Other standard curves** | NIST **P-256/secp256r1** group order/cofactor; **Curve25519** (Montgomery) and **ed25519** (twisted Edwards) — including the curve *models* themselves | Curve names = 0 hits. Mathlib has **no Montgomery or twisted-Edwards model** and **no point-counting/Schoof/Hasse-to-exact-order**, so orders are only assertable. |
| **Generic group model / cost model** | GGM oracle + query-count framework for crypto **lower bounds** | `"generic group model oracle"` = 0 hits; Mathlib has essentially no cryptography. Only external `VCVio` (Verified-zkEVM/VCV-io, not v4.31-pinned, no GGM) loosely prefigures it. |
| **Lattice reduction / HNP** | LLL/BKZ reduction, reduced-basis notion, SVP/CVP as decision/approx problems, **Hidden Number Problem** | `"LLL lattice reduction"` = 0 hits (code + PR). All prior formalizations are **Isabelle/HOL** (LLL: JAR 2020; SVP/CVP NP-hardness: arXiv 2306.08375; HNP: ITP 2025 https://drops.dagstuhl.de/storage/00lipics/lipics-vol352-itp2025/LIPIcs.ITP.2025.23/LIPIcs.ITP.2025.23.pdf), not Lean. |

---

## Bottom line

The **generic algebraic scaffolding** of the ECDLP is in good shape upstream:
the Weierstrass group law, base/variable change, division-polynomial
`preΨ`/`ΨSq`/`Φ` infrastructure, rank-1 elliptic divisibility sequences,
geometry-of-numbers primitives, and multivariate-polynomial/resultant
infrastructure are available in pinned Mathlib v4.31. The audited tree still
lacks the project-ready ECDLP superstructure: no Weil pairing or
`E[n] ≅ (ℤ/n)²`, no Semaev family, no genuine multi-index nets, no
isogeny/Frobenius layer, no point counting for named curves, no LLL/SVP/CVP or
HNP, and no general generic-group cost model.

The point/division-polynomial bridge remains a legitimate formal frontier, but
it is no longer declared the unconditional "highest-ROI next port." It is
`build_if_selected`/`retain_frontier` work: resume it when a surviving route in
`repo/ECDLP_DECISION_SUBSTRATE.json` needs the general theorem.
