# Upstream bundle — the curve-free results this repo can contribute to Mathlib

*Outbound companion to `notes/UPSTREAM_SCAN.md`.* The scan asks **"is X already upstream?"**;
this memo asks the reverse: **which kernel-verified results built here are stated generally
enough (no secp256k1, no ECDLP) to be Mathlib PR candidates**, what each still needs before it
is submission-ready, and where it would land. Per `ROADMAP.md` §2 this is value channel #2
("Mathlib upstreaming — the strongest form of external verification and the most durable
artifact"). **Submission itself is a human decision** (`ROADMAP.md` §6: anything public-facing);
this memo only prepares the package — it does not open any PR.

Honesty note carried throughout: one flagship item (`normEDS_isEllSequence`) is a **port of an
existing stalled contribution by other authors**, not original to this repo — upstreaming it
means *helping land their work*, credited to them. The other four items are original here.

---

## Tier A — submission-ready with light generalization (pure `CommRing` / `AddCommGroup`)

These are already stated over an abstract ring/group with no curve and no `secp256k1`. The work
before a PR is naming/docstring conventions, splitting the port-scaffold from the new content,
and (where noted) relaxing a hypothesis to Mathlib's preferred generality.

| # | Result (current name) | File | Statement (curve-free) | Target Mathlib file | Pre-PR work |
|---|---|---|---|---|---|
| A1 | `normEDS_isEllSequence` | `NormEDSIsElliptic.lean` | `normEDS b c d` satisfies `IsEllSequence` over any `CommRing` — **closes the open TODO** in Mathlib's own `EllipticDivisibilitySequence.lean` | `Mathlib/NumberTheory/EllipticDivisibilitySequence.lean` | **Port, not original** (Junyan Xu / David Angdinata, PR #13155 net-relation lineage) — rebase their block onto current master and submit **under their authorship**; strip our `EDSPort` namespace wrapper |
| A2 | `isEllSequence_of_rec_one` | `EllSequenceRecOne.lean` | the 3-index elliptic-sequence identity is a pure consequence of its `r = 1` case, over any `CommRing`, with **no** `W 1 = 1` / non-vanishing hypothesis | same file as A1 | original; already minimal (one `linear_combination`); just needs a Mathlib-style docstring + name (`IsEllSequence.of_rec_one`?) |
| A3 | `normEDS_somos4` | `NormEDSSomos4.lean` | the `n = 2` Somos-4 slice `normEDS(m+2)·normEDS(m−2) = b²·normEDS(m+1)·normEDS(m−1) − c·normEDS(m)²`, any `CommRing`, all `m : ℤ` | same file as A1 | original; companion identity to A1; the two private `linear_combination` step-lemmas are clean |
| A4 | `nonempty_addEquiv_zmod_prod_of_card_eq_sq` | `TorsionStructure.lean` | a finite `AddCommGroup` of order `n²` killed by a prime `n` is `≃+ ZMod n × ZMod n` | `Mathlib/GroupTheory/…` (finite-abelian classification neighbourhood) | original; already over a bare `AddCommGroup`; consider a `Fintype`/`Nat.card` phrasing choice and whether to state the multiplicative dual too |

## Tier B — original, novel, needs a short generalization pass

| # | Result (current names) | File | Statement | Why it is new | Pre-PR work |
|---|---|---|---|---|---|
| B1 | `normEDS_shift_mul_shift_of_eq_zero`, `normEDS_sub_eq_zero_of_eq_zero`, `normEDS_not_consecutive_zeros`(`'`) | `NormEDSConsecutiveZeros.lean` | **Ward apparition rigidity**: over an integral domain, `normEDS b c d` never vanishes at two consecutive integers, given the sharp `¬(b=0∧c=0)`, `¬(c=0∧d=0)`; plus the translation identity at a zero and the case-split-free `ρ`-descent | no equivalent anywhere upstream (the scan found only the *definitions*, not this rigidity); it is the scalar heart of the `gcd(Φₙ,ΨSqₙ)=1` argument but stated with **no curve in sight** | original; already over `[CommRing R] [IsDomain R]`; a Mathlib PR would pair it with A1 as "properties of `normEDS`" and may want the rank-of-apparition corollary (`zeros = ρℤ` in the `W(ρ+1)≠0` case) stated explicitly |

## Tier C — curve-generic but elliptic-curve-specific (larger, later)

Not pure ring/group theory, but stated over an arbitrary `WeierstrassCurve` / field with no
`secp256k1` — candidates once the EC-specific Mathlib neighbourhood is the right home.

- **The evaluation bridge** (`DivisionPolynomialEvalBridge.lean`, `EvalBridge`/`LocalStructure`/
  `Descent` sections): `(ΨSq n).eval x₀ = normEDS(…)²` and `(Φ n).eval x₀ = x₀·normEDS(…)² −
  normEDS(n+1)·normEDS(n−1)`, connecting Mathlib's `Φ`/`ΨSq` at a point to the scalar `normEDS`.
  Curve-generic (Mathlib + the A-tier lemmas only). Would strengthen Mathlib's
  division-polynomial ↔ EDS story. Pre-PR: separate the curve-generic sections from the
  secp256k1 instantiation (already sectioned that way).

---

## The one general theorem this bundle would *enable* upstream (not yet built)

The torsion-structure family `E[n](k̄) ≅ (ℤ/n)²` is proved here **only for the concrete primes
`n ∈ {2,3,5,7}` on secp256k1** (`{Two,Three,Five,Seven}TorsionStructure.lean`), because the
**general** case needs the one CORE-hard item — **separability of `[n]`** (`notes/SEPARABILITY_ROUTES.md`).
A4 is the group-theoretic *last step* of that theorem, already general; the assembly *pattern*
(closure bridge + exact root count + `±y` pairing + A4) is what a general Mathlib
`E[n] ≅ (ℤ/n)²` would reuse. So the honest upstream story is: **A1–A4 + B1 are shippable now;
the headline `E[n]≅(ℤ/n)²` is not — it is gated on the separability core, which remains the
open program.**

## Suggested PR sequencing (for a human to action)

1. **A1 + A2 + A3** as one PR completing the `normEDS`-is-elliptic TODO, credited to the #13155
   authors (A1) with A2/A3 as accompanying lemmas — highest value ÷ effort, closes a real TODO.
2. **B1** as a follow-up "`normEDS` apparition" PR (depends on A1 landing).
3. **A4** independently, into the finite-abelian-group area.
4. **Tier C** later, once A-tier is in and the EC-division-polynomial maintainers are looped in.

Nothing here is submitted; this is the package. The kernel has verified every listed result in
this repo (see `VERIFIED.md`); Mathlib's review is the external re-verification `ROADMAP.md` §2
is after.
