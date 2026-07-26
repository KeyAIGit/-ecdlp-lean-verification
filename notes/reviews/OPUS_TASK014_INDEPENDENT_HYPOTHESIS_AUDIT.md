# OPUS-001 — Independent hypothesis triage for TASK-014

**Assignment:** GitHub issue #254.
**Review baseline:** PR #251 head `99231d1fb689ca4968e20ef411577b1cf4da61c1`
(branch `agent/research-engine-mutation-hardening`), read-only. Frozen `main` at review time:
`fed55d84675fd96e5f40204b9f5f49baa8c01172`. Also read: PR #248 (base `79295c09…`), PR #250.
**Date:** 2026-07-26.
**Repository changes made by this review:** this file only. No merge of #248, #250, or #251. No
edit to any historical outcome file. No route promotion, no experiment authorization.

---

## 0. Provenance disclosure (read this before weighing anything below)

This audit was produced by one model in one session: an orchestrator plus twelve subagents, all
the same model, all with access to the same brief. Where this document says "producer" and
"independent validator", that means **the two lines were written without seeing each other's
output** — a genuine methodological separation that catches arithmetic and modelling errors, and
it did catch several. It is **not** source-independent review, and must not be recorded as such.
Agreement between two of these lines is weak evidence; the strong evidence here is (a) verbatim
primary-source quotation and (b) arithmetic re-executed from `p` and `n` alone.

Three claims below were **overturned by adversarial re-checking of this audit's own output**, and
each overturn is recorded in place rather than silently corrected. Two of the overturned claims
were the orchestrator's own.

No novelty is claimed for anything in this document. Absence of a result from the literature or
from this repository is not treated as evidence of novelty anywhere below.

---

## 1. Executive conclusion

**None of the three directions deserves scarce mathematical, reviewer, or compute budget, and no
successor candidate is proposed.** The three dispositions are reached for three genuinely
different reasons, and the reasons matter more than the verdicts:

1. **Petit smooth-subgroup, instance (i)** — `STOP`. Closed **unconditionally** on secp256k1 by
   arithmetic, with no solver model, no Gröbner heuristic, and no representation choice. Every
   divisor of `p-1` large enough to satisfy the paper's own factor-base condition is divisible by
   the prime `13441`; the resulting factor base is short of the paper's requirement by 7.4 to
   20.2 bits at **every** arity in 10..20. A representation-free counting bound then puts the
   attack at least **+59.4 to +95.6 bits above the matched baseline**. The honest caveat: this
   closes a region an attacker following the published construction would never enter, because
   the construction's own sizing condition already fails there.
2. **Connected-`S3` GLV phase rigidity** — `STOP`, as a *correctness note*, not as research. The
   theorem is settled (and the repository already states it correctly, including the subtle
   hypothesis). But it is **decision-irrelevant**: for every fixed target with `x(R) != 0` the
   surviving phase group is **trivial**, so the GLV phase buys exactly zero symmetry reduction in
   the only case index calculus uses. A group whose order does not grow with the arity `m`
   licenses no complexity conclusion, and none is drawn.
3. **Zero-minor guess-and-determine (Mahalanobis 2026)** — `STOP` for the explicit exhaustive
   signature-table implementation under the paper's own stated probability model, which costs at
   least **2^248.88** operations against a baseline of 2^126.53. The strongest available argument
   is not ours: **the lineage's own parameter choice sets the candidate count ≈ p** ([LV2018]
   Sec 3.0.2 fixes `C(3n'+l, l) ≈ p`), and [LV2018]'s own stated per-pass success
   `0.6 (log p)^2 / p` gives ~2^241 passes at 256 bits versus 2^128 for rho. Four openings are
   preserved and explicitly **not** closed.

**Where one additional reviewer-hour has the greatest expected information value:** not on any of
the three mechanisms. It is on defect **F1** below — a wrong arity-sizing convention that is
*machine-enforced* in `scripts/typed_evidence_lib.py` and currently mis-sizes the only live cell
in the smooth-subgroup family by two arities. Fixing it is roughly an hour and it changes what
the engine will select next. Second-highest: the Kudo CANS 2018 acquisition, now with a named
untried route (the WCC 2017 precursor).

---

## 2. Source-anchored comparison matrix

Read status is reported for the **exact artifact read**, never upgraded from metadata, abstract,
or a secondary description. "Full text read" below always names which version.

| Source | Read status | Claim status | What it actually claims | Bar it does *not* clear |
|---|---|---|---|---|
| **Yokoyama–Yasuda–Takahashi–Kogure 2020**, JMC 14, 460–485, DOI `10.1515/jmc-2019-0029` | **full text read** (Wayback snapshot of the De Gruyter PDF, sha256 `8d7256195d40b1af…`, 26 pp.) | conditional estimate | **Prop. 9, §4.1.2, p.475:** at least `(m·d^(m-1))^(1-eps)` field operations for a Gröbner basis of `I_m(a,b)`, for almost every `a,b`, by **any algorithm using S-polynomials** | A **cost** bound, not a solving-degree bound. Scoped to the **naive** setting where `V` is a *random* subset. Conditional on Assumption 7 and the explicitly non-rigorous Remark 8. **Does not bound** Petit–Kosters–Messeng, Amadori, or Kudo |
| **Petit–Kosters–Messeng 2016** (PKC), framework + instances (i), (ii) | **full text read** | heuristic | A framework whose cost hinges on an **unquantified** `T(E,m,L)`. §3.2 p.9: expected solutions ≈ `(deg L)^m / (m!·p)`; balance point p.10 `(deg L)^m ~ m!·p` | "**The complexity of our algorithms remains an open problem**" (Contributions, p.4). "only practical for small parameters at the moment". "the set of experiments is too limited to draw any conclusion at this stage". **Every** experiment fixes `m = 2`, `p <= 4206593` (22 bits) |
| **Amadori–Pintore–Sala 2018** | **full text read** | conditional estimate | For fixed `m`, as `p` grows, outperforms Petit et al. — **relative** only | The `r^(1/2)` bar is **explicitly not claimed**. Table 1 crossovers are against Petit, never against rho. Rests on the **unproven** assumption (13) `T ~ T'`. Thresholds are explicitly below cryptographic sizes |
| **Kudo–Yokota–Takahashi–Yasuda 2018** (CANS) | **abstract only — acquisition unresolved** | unclear | Nothing may be attributed beyond the abstract | No exponent, constant, crossover, arity range, or comparison bar is attributable. See §7 |
| **Faugère–Huot–Joux–Renault–Vitse 2014** | partial text read | experiment | A computational record for the 8th **symmetrized** summation polynomial `P_{phi,8}`, attached to a **rational 2-torsion point** | **Audit correction:** this is *not* "the largest classical Semaev polynomial ever computed" — Table 1 records that classical `S_7` and `S_8` were **not** computed. The premise fails outright for secp256k1: `n` is prime, so there is no rational 2- or 3-torsion |
| **Gaudry 2009** | partial text read | heuristic | `Õ(q^(2-2/n))` for fixed extension degree `n >= 2` | secp256k1 is a prime field; `n = 1` voids the construction |
| **[LV2018]** Mahalanobis–Mallick(–Abdullah), INDOCRYPT 2018 (read as arXiv:1703.07544v3) | **full text read** (preprint; proceedings text not obtained) | theorem (reduction) | Thm 3.2: the **reduction** is polynomial with success → `1 - 1/e ≈ 0.6321` | Complete algorithm: per-pass success `0.6 (log p)^2 / p`, i.e. **~2^-241 at 256 bits ⇒ ~2^241 passes vs 2^128 for rho — by the authors' own arithmetic**. §3.0.2 sets `C(3n'+l, l) ≈ p` **by parameter choice**. No experiment of any kind reported |
| **[NM2021]** Abdullah–Mahalanobis–Mallick, GCC 12(2) | **full text read** | conditional estimate | Zero-minor search via Gaussian-elimination/Schur complement | The authors **stopped because growth was exponential**. All data characteristic 2. **No prime-field experiment anywhere** |
| **[ZM2025]** Abdullah–Mahalanobis (read as arXiv:2310.04132v1; **published Exp. Math. version not obtained**) | **full text read** (preprint) | experiment | Zero minor ⇒ DLP (Thm 3.1); almost-principal-minor experiments | Load-bearing **initial-minor conjecture** is unproved. Every table is `F_(2^25)`..`F_(2^50)`. Extrapolation **explicitly disclaimed**. The APM-vs-GESC comparison is admitted unfair in APM's favour |
| **[GD2026]** Mahalanobis, arXiv:2607.09814v1, 10 Jul 2026 | **full text read** (pp. 1–13, 15; p.14 not retrieved) | heuristic | Guess-and-determine for a zero minor via central hyperplane arrangements; "has the potential to be a polynomial time algorithm" | §5.1: "**we are not sure of the complexity of the algorithm at this moment**". "For big fields the probability is not known." The `d(p)` law "**remains unexplored**". General position is **assumed and never checked**. **Zero ECDLP experiments of any size** in this paper |

**`D^m/(m!·p)` is now anchored.** It is PKC 2016 §3.2 p.9 with the balance point on p.10. It was
correctly held as "review input, not canonical fact" in the baseline, and that caveat may now be
discharged — see confirmation C1 and defect F1, which the same paragraph forces.

*Unresolved:* whether Semaev 2004 independently states an `m!`-denominator yield expression. No
statement about Semaev 2004's contents is made anywhere in this document.

---

## 3. Disposition per direction

### 3.1 Petit smooth-subgroup / composed-map route — `STOP` (instance (i)); `PARK` (instance (ii))

**Instance (i) closes unconditionally.** All 16 divisors of `p-1` that avoid the 237-bit prime
cofactor are

```
1, 2, 3, 6, 7, 14, 21, 42, 13441, 26882, 40323, 80646, 94087, 188174, 282261, 564522
```

with a **hard gap: no divisor lies strictly between 43 and 13440**. Every divisor at or above
`p^(1/20) = 2^12.80` is divisible by `13441`, which is prime. Meanwhile PKC's own condition 1
(`|{x : L(x)=0}| ~ p^(1/m)`) needs `deg L` from `2^25.60` (m=10) down to `2^12.80` (m=20), and
the best `B`-smooth divisor available for any `B <= 13440` is `42 = 2^5.39` — short by **7.41 to
20.21 bits at every arity in 10..20**.

A **representation-free counting bound** then closes it without any solver model: the number of
points of `E(F_p)` expressible as a sum of at most `m` factor-base points is at most
`C(#F+m, m)`, so a single-target attack needs at least `p / C(#F+m, m)` trials. Charging **one
group operation per trial**:

| | m = 10 | m = 20 | margin over baseline 2^126.5333 |
|---|---|---|---|
| `#F = 42` | 2^222.1190 | 2^202.9684 | **+95.59 to +76.44 bits** |
| `#F = 84` (maximally generous) | — | — | **+86.43 to +59.35 bits** |

Because this is a counting fact about the factor base and not about how the system is solved, it
closes **all four representations and the hybrid simultaneously**. Verified independently: the
bound in fact beats the baseline for every `m <= 118` at `#F = 42` (and `m <= 54` at `#F = 84`);
full coverage of `E(F_p)` would need `m = 1108`. **The arity window 10..20 is therefore a hedge
tighter than what is proved** — the closure is valid on `m ∈ [2,118]`.

**Honest limitation on this closure (adversarial finding R02).** The closed region is exactly the
region where PKC's own condition 1 already fails at every audited arity. No attacker following
the published construction would enter it. The closure is *correct* and *decision-irrelevant*.

**Instance (ii) is not closed and the `p-1` arithmetic is irrelevant to it.** The auxiliary
curve's order ranges over the whole Hasse interval; §3.4/§3.5 exists precisely to bypass the
`p-1` obstruction. The cheapest representation found has 288–340 variables with every equation of
total degree `<= 4` and a degree-4 Macaulay matrix of only `2^56.6–2^58.2` bytes. It survives
entirely on the unbounded `T(E,m,L)`, whose exact matching budget is `T*(m) = 2^98.7542` (m=10) to
`2^110.6792` (m=20) — permitting a dense Macaulay solve only to degree 6 (7 at m=20) at
`omega = 2.37`.

**The decisive structural finding, and it runs against a factor-base intuition:** `D* = (m!p)^(1/m)`
is `2^27.78` at m=10 and `2^18.77` at m=16 — **100 to 109 bits below** the rho cost — and the
linear algebra `D*^2` is `2^55.6`/`2^37.5`. So **neither the factor base nor the linear algebra is
the obstruction for `m >= 5`**; with `T = 1` the cost-model floor drops below the baseline at
`m = 5`. The cost model alone therefore **cannot** close this screen at any arity `>= 5`.
Everything rests on `T`.

Substituting the only anchored bound on `T` (Yokoyama Prop. 9) makes the `D`-dependence **cancel
identically**, giving a floor of `m·m!·p >= 4p = 2^258.0000`, i.e. +130.17 bits over rho, with a
flip threshold `eps >= 0.6051` against Yokoyama's stipulated `0 < eps << 1`. **This transfer is an
inference, not an anchored result:** Yokoyama assumes `V` random; Petit's `V` is a multiplicative
subgroup or an isogeny-kernel coset. If Assumption 7 fails for structured `V`, this substitution
evaporates and nothing quantitative closes the screen.

An `S_m`-symmetry argument independently closes instance (ii) for `m >= 19` (`omega = 2`) or
`m >= 17` (`omega = 2.37`), shrinking the open window to **`m ∈ [10,16]`**, inside which the open
question becomes "is the solving degree `<= 4–5`?" rather than "`<= 6–7`?".

**Scoped desk label:** `bounded_negative` for instance (i) on secp256k1, all `B <= 13440`, all
four representations plus the hybrid, arities `m ∈ [2,118]`, plain single-target classical.
`inconclusive` for instance (ii) at `m ∈ [10,16]`. A positive label would not authorize an
experiment, and none is authorized.

### 3.2 Connected-`S3` GLV phase rigidity — `STOP` (close as a correctness note)

**The mathematics is settled, and there was no genuine disagreement** (adversarial finding R07:
the "prover" and "refuter" outputs are the same theorem; the refuter's counterexample *is* the
prover's own lemma). Verified independently by the orchestrator:

For `y^2 = x^3 + b`, `char != 2,3`, `b != 0`, `S3` is weighted-homogeneous of weighted degree 4
(`wt x = 1`, `wt b = 3`); all nine monomials have `x`-degree `≡ 1 (mod 3)`. The coordinatewise
`C3` phase group of **one** hyperedge is exactly the diagonal `{(0,0,0),(1,1,1),(2,2,2)}` —
**forced twice over, independently**, by the degree-4 part alone and by the degree-1 part
(`-4b·x_i`) alone. It therefore does **not** rest on `b != 0`.

`S3` is absolutely irreducible, via the exactly verified identity

```
disc_{x2} S3  =  16 (x1^3 + b)(x3^3 + b)
```

which upgrades scalar covariance to **zero-variety preservation** for a single hyperedge — the
`(a) ⇔ (b)` bridge, and the hypothesis the orchestrator's first pass had flagged as an open gap.

**The internal-variable loophole is closed structurally, not arithmetically:** a coordinatewise
action assigns one exponent per **variable**, not per **occurrence**, so a degree-2 internal
variable receives a single exponent that both of its edges independently pin. Absorbing a phase
mismatch would require rescaling per occurrence, which is a different, system-changing map. This
is exactly the loophole a tree-local rephrasing would need, and it is shut.

**Correction to the orchestrator's own derivation.** My first pass argued the fixed-target clause
from "`R != O` and `n` prime". That is **valid for secp256k1 but false as a general statement**,
and the repository was already right where I was wrong. The correct hypothesis is **`x(R) != 0`**,
not `R != O`. Smallest counterexample, verified by exhaustive enumeration: over `F_7`,
`y^2 = x^3 + 1`, `beta = 2` (equivalently 4), `R = (0,1)` — a **nonzero** point of order exactly 3
(`#E(F_7) = 12`). The fibre of `S3(x1,x2,0) = 0` has 10 elements and of all 9 phases exactly
`{(0,0),(1,1),(2,2)}` survive. Scanning every `x_R != 0` over that curve: **zero** breaks.
`x(R) = 0` is the unique fixed point of `x -> beta·x`, and it picks out the two 3-torsion points
`(0, ±sqrt b)`.

**New, and it settles a question the baseline left explicitly open:** on secp256k1 **both
exceptional loci are empty**. Recomputed here — `7` is a **non-residue** mod `p` (Legendre
`(7|p) = -1`), so there is no rational point with `x = 0`; and `-7` is a **non-cube** mod `p`, so
there is no rational 2-torsion. Consistent with `n` prime and `n` odd.

**Why this earns no budget (adversarial finding R08).** The system index calculus actually uses is
the **fixed-target** PDP system, and for every `r != 0` its phase group is **trivial** — so the
GLV phase yields exactly **zero** set-stabilizer reduction in the only case that matters. The
surviving group has order 3 or 1 **independent of the arity `m`**, and per the standing rule that
fact alone implies nothing about cost. No complexity, solving-degree, or ECDLP consequence is
drawn.

**Not established, and must not be cited as if it were:** the `F_q`-rational version without an
added non-degeneracy hypothesis (small-`q` breaks occur when a coordinate is identically 0 on the
rational solution set, since 0 is the phase's fixed point); cyclic and over-determined
hypergraphs; the edge-dominance step for the **balanced `S3` tree**, which is proved only for the
caterpillar chain — and the balanced tree is precisely the representation the instance-(ii) cost
lines use (adversarial finding R13). Nothing here is about arbitrary birational maps, all
geometric automorphisms, solving degree, or "all GLV-Semaev algorithms". **No Lean formalization
was begun or proposed.**

### 3.3 Zero-minor guess-and-determine — `STOP` (explicit implementation only)

**The disputed counts are resolved, by fitting the author's own Table 1.** All 210 published cells
(`log2 p = 40..60`, `d = 5..14`) are reproduced to 5 decimals by Eq. (4) with exponent
`N = C(l'+d, d)`. Every rival exponent shape fails even when granted a free per-row `l'`:

| exponent | best achievable max error |
|---|---|
| **`C(l'+d, d)`** | **0.000000** (exact, at `l'_eff = 3·floor(log2 p / 2) + 1`) |
| `C(l', d)` | 0.033400 |
| `C(l'+d, d-1)` | 0.035240 |
| `C(l+d, d)` | 0.054750 |

**The paper is internally inconsistent, and the inconsistency is optimistic.** Eq. (4) uses
`C(l'+d, d)` while **Algorithm 1 line 11 enumerates `C(l', d)`** — 14.92 bits fewer at
`l' = 385, d = 63`. Table 1 is *not* reproducible from the paper's own printed pseudocode: the
prose reading `l' = floor(3 log2 p / 2)` matches 41 of 85 informative cells, and Algorithm 3 as
printed matches **0 of 85**; the fit needs round-**down** plus an unexplained `+1`.

Exact identity, verified as rationals: `C(l'+d, d-1) / C(l'+d, d) = d / (l'+1)` — at `(384, 63)`
this is `9/55 = 2^-2.6114`. **The signature table is smaller than the outer trial budget**, so the
negative cannot be blamed on the table.

**secp256k1 scale** (`n' = 256, l = 768, l' = 384`): smallest `d` with `C(384+d, d) >= n` is
`d* = 63` (`C(447,63) = 2^258.0456`; `C(446,62) = 2^255.2187 < 2^256` confirms minimality).
`log2(1/q) = 256.0000` exactly for `q = (n-767)/(n(n-383))`.

| accounting | cost | vs rho 2^127.8257 | vs rho·|Aut| 2^126.5333 |
|---|---|---|---|
| charitable floor `p·ln2·d/(l'+1)`, at the model optimum `d = 4` | **2^248.8825** | +121.06 | **+122.35** |
| one operation per candidate *event* | 2^255.4712 | +127.65 | +128.94 |
| Algorithm 1's real per-candidate work | 2^270.7916 | +142.97 | +144.26 |
| the paper's own matrix-free simulation (Algorithm 3) | 2^264.0562 | — | — |
| free-parameter minimum over all `(l', d)`, charging `l'^3` to write `M` and `l'^4` for the kernel | 2^226.0 | — | +99.47 |

The matrix-free simulation carries the same floor, so **the negative cannot be attributed to
linear algebra**.

**Two overturned claims, recorded rather than quietly dropped.**

- *The orchestrator's "d-invariance" result.* I derived that under a generous reading where one
  trial tests the whole table, `work = trials × table = ln2·p = 2^255.4712` **exactly,
  independent of `d`** — the table size cancels algebraically. That derivation is arithmetically
  right but rests on the reading refuted immediately below, and under the correct linear
  accounting the floor is `p·ln2·d/(l'+1)`, which is **monotone in `d`** (2^248.88 at `d = 4`;
  the formula alone minimizes at `d = 1`, and `d >= 2` is needed for the `(d-1)×d` kernels to
  exist at all). **The d-invariance claim is withdrawn.**
- *The independent validator's birthday alarm.* It argued that since **any** two identical
  penultimate intersections give a zero minor, a table of `S` entries tests `C(S,2)` pairs, giving
  a floor of `sqrt(2p) = 2^128.5000` — `Theta(sqrt p)`, **the same exponent as rho**, losing by
  only `2^0.674`. It flagged this loudly, as instructed. **It is wrong, and the refutation is
  structural.** Two signatures coincide, `T(b1) = T(b2) = <v>`, only if every row in `b1 ∪ b2` is
  orthogonal to `v`, i.e. `rank(b1 ∪ b2) <= d-1` — a determinantal condition of codimension
  `k-d+1` for `|b1 ∪ b2| = k`. At `q ~ 2^256` each row beyond the `d`-th costs a further 256 bits,
  so only the `k = d` term survives and the event count collapses back to Eq. (4)'s `C(l'+d, d)`.
  **Verified by exhaustive enumeration** over `F_7`, `F_11`, `F_13` at `d = 3, 4`: the rank
  condition held for **every** colliding pair in every run (36/36, 15/15, 12/12, 193/193, 129/129,
  156/156), with the `|union| = d` term dominating and higher terms vanishing as `q` grows exactly
  as the codimension count predicts.

**The strongest argument here is the lineage's own.** [LV2018] §3.0.2 sets `C(3n'+l, l) ≈ p` **by
parameter choice**, so the candidate-minor count is `~p ~ 2^256` by construction; and [LV2018]'s
own stated per-pass success `0.6 (log p)^2 / p` gives `~2^241` passes at 256 bits against `2^128`
for rho. The authors' own arithmetic already places the complete attack worse than generic
methods.

**Scope — what this negative closes and what it must not be read as closing.** It closes **only**
the explicit exhaustive signature-table implementation under the probability model
arXiv:2607.09814v1 itself states. It does **not** close, and each of the following remains
genuinely open:

| preserved opening | smallest thing that would resolve it | rough cost |
|---|---|---|
| the **zero-minor reduction** itself ([ZM2025] Thm 3.1 / [LV2018] Thm 3.2) — a *theorem*, unaffected | nothing; it is correct and should be recorded as correct | — |
| an **implicit or sublinear duplicate search** that never materializes the table | a stated algorithm with a cost argument; the rank obstruction above is the thing it must beat | ~1 reviewer-day to assess once stated |
| a **matrix-specific per-trial probability materially above `~1/p`** — the model assumes uniform independent sums, and `K` is highly structured; this is proved nowhere in the lineage | measured collision statistics on the *actual* kernel matrices at 40–60 bits, prime field, against the `1/p` null | needs released code + seeds |
| an **independently validated structural correlation** changing the exponent — the authors' own **initial-minor conjecture** | it would have to lift the per-candidate probability by a factor `F >= 2^127.6455` merely to **tie** plain rho | open research problem |

**Prerequisites before even a toy matrix experiment is worth a reviewer-hour** (checked against
what is available today): released code — **not available**; raw data and exact seeds — **not
available**; curve parameters for a *prime-field* run — **none reported anywhere in the lineage**;
resource measurements — binary-field only, `F_(2^25)`..`F_(2^50)`; a complete correctness argument
for the duplicate-to-zero-minor step — **incomplete**, the paper itself concedes a first duplicate
may have index-set union of cardinality `> l'` and Algorithm 2 then returns "No result". **No
secp256k1 discrete-log run is authorized under any circumstance.**

---

## 4. Unresolved assumptions, and what would resolve each

| # | Assumption | Status | What would resolve it |
|---|---|---|---|
| U1 | `T(E,m,L)` for PKC instance (ii) at `m ∈ [10,16]` | **unbounded in the source**; the authors call it an open problem | A solving-degree bound for the structured system. Nothing in this audit supplies one, and none may be assumed |
| U2 | Yokoyama Prop. 9 transfers to **structured** `V` | **inference, not anchored** — Yokoyama's `V` is random | Check whether Assumption 7 (`NS(Syz)`-semi-normality) survives when `V` is a multiplicative subgroup or isogeny-kernel coset |
| U3 | Kudo's hybrid is exponent-neutral (fix `k` vars ⇒ `d^k` subsystems of the same type) | **inference, not anchored — the repository's own claim is currently unsupported** | Read CANS 2018, or the WCC 2017 precursor |
| U4 | Amadori assumption (13) `T ~ T'` | **unproven**; the authors call proving it open | Out of scope here |
| U5 | Edge-dominance for the **balanced `S3` tree** (Workstream C) | proved only for the caterpillar chain | Finite-model search on balanced trees over a wider curve set than the six sixth-power-class representatives tested |
| U6 | `F_q`-rational Workstream C statement without a non-degeneracy hypothesis | **false at small `q`**; unknown whether the non-degenerate breaks at `p ∈ {7,13}` survive at larger `p` | Extend the exhaustive scan; irrelevant to secp256k1, where both loci are empty |
| U7 | Per-trial independence in [GD2026]'s model | assumed, never checked; general position likewise "assumed and never checked" | Collision statistics on real kernel matrices (see §3.3 table) |
| U8 | Whether Semaev 2004 states an `m!`-denominator yield expression | **not obtained** | Read eprint 2004/031. Does not block anything: the expression is anchored in PKC §3.2 |

---

## 5. Full-cost comparison against the matched baseline

**Baseline** (single target, classical, plain; no precomputation amortized across targets, no
oracle, no quantum): Pollard rho on secp256k1, `sqrt(pi·n/4) = 2^127.825748`; with the order-6
automorphism, `2^126.533267`. Both recomputed by two independent routes agreeing to 8+ decimals.

| Mechanism | Full charged cost | Margin over 2^126.5333 | What the margin rests on |
|---|---|---|---|
| PKC instance (i), `#F = 42`, `m ∈ [2,118]` | 2^202.97 – 2^222.12 | **+76.4 to +95.6** | Pure counting; no solver model |
| PKC instance (i), `#F = 84` (generous) | — | +59.4 to +86.4 | Pure counting |
| PKC instance (ii), `m >= 17` (`omega = 2.37`) | — | closed | `S_m`-orbit lower bound on `T` |
| PKC instance (ii), `m ∈ [10,16]` | **undetermined** | — | Rests entirely on the unbounded `T` (U1) |
| Zero-minor, charitable floor at `d = 4` | 2^248.8825 | **+122.35** | Eq. (4) as pinned by Table 1, plus the rank obstruction |
| Zero-minor, free-parameter minimum | 2^226.0 | +99.47 | As above, with realistic `l'^3`/`l'^4` charges |
| Zero-minor, by the lineage's own arithmetic ([LV2018]) | ~2^241 passes | +114 | The authors' own stated per-pass success |
| Connected-`S3` GLV phase | **no cost change** | 0 | Group order 3 or 1, constant in `m`; trivial for `x(R) != 0` |

**One asymmetry in this convention, stated because it matters (adversarial finding R11).** The
baseline credits rho the full `sqrt(6) = 2^1.2925` automorphism speedup, but no line above credits
the *candidate* side the factor-3 advantage it is equally entitled to on a `j = 0` curve (one
decomposition of `R` yields relations for `lambda R` and `lambda^2 R` at no cost). **Any margin
reported below ~2 bits is therefore not a margin under this convention.** Every margin above is
far larger than that — which is precisely what the refutation of the birthday reading rescued,
since that reading would have produced a 0.67-bit "margin".

---

## 6. Severity-ranked defects in the current repository interpretation

Ten defects and five confirmations. Anchors are against PR #251 head. No fix is applied by this
review, and **no edit to any historical outcome file is proposed** — issues there are recorded as
findings only.

| # | Sev | Anchor | Defect | Smallest correction |
|---|---|---|---|---|
| **F1** | **P1** | `repo/ECDLP_TYPED_EVIDENCE_V0.json:517–518`; machine-enforced at `scripts/typed_evidence_lib.py:715–728` | The arity-14 smooth-subgroup cell uses **only** PKC §3.1 condition 1 (`ceil(p^(1/14)) = 319558`) and **drops the same paper's §3.2 relation-yield balance** `(deg L)^m ~ m!·p`. Recomputed: `ceil((14!·p)^(1/14)) = 1931997 > 564522`; the yield at `m = 14` is `2^-24.8499` per system; the **smallest arity where 564522 suffices is `m = 16`**, needing `S_17` (per-variable degree `2^15`), not `S_15` (`2^13`) | Add the §3.2 balance point as a **second** predicate rather than replacing condition 1: keep 319558 labelled as the condition-1 figure and add `ceil((m!·p)^(1/m))`. Follow the scope discipline of `EDD-2026-07-25-003` — do **not** convert this into a route-wide negative |
| **F2** | **P1** | `data/source_registry.json:23` vs `repo/ECDLP_TYPED_EVIDENCE_V0.json:195` | **TASK-014's Amadori allegation is confirmed verbatim**: registry says `full_text_inspected`, typed evidence says `metadata_only`. The **stronger** value is the one carrying no artifact hash and no claim extract (`data/source_claim_extracts/` holds only `fhjrv2014.json` and `petit_kosters_messeng2016.json`). It persists because the consistency gate at `typed_evidence_lib.py:344–352` is **one-directional** | Either downgrade `gen_source_registry.py:259` to `full_text_unread`, or — since this audit **did** obtain and read the full text — upgrade the typed-evidence side and add the missing extract. Make the gate bidirectional |
| **F3** | P2 | `repo/RESEARCH_CLAIMS_V0.json:118`, evidence_events 232–240 | `REO-2026-07-24-004` is cited as evidence for the GLV independent-cube bounded negative, but it is a **Ward-EDS** outcome: `route_id "R-EDS-DIVISION-POLYNOMIAL"`, `hypothesis_id "HYP_WARD_EDS_001"`, claim boundary "Ward EDS rank of apparition and zero-set measurements only" | Remove `REO-2026-07-24-004` from the evidence list (leaving REO-001..003) |
| **F4** | P2 | `repo/ECDLP_TYPED_EVIDENCE_V0.json` `TP-SECP-PMINUS1-SMOOTH-DIVISOR` / `SC-SECP-PMINUS1-FACTORIZATION`; `Ecdlp/Proved/Secp256k1PrimeP.lean:174,177` | Status `kernel_derived` with a locator whose theorem statement is `Nat.Prime …` — the **factorization appears only as a `native_decide` proof step inside another proof**, not as a theorem | Retarget or retoken. **Note:** PR #250 supplies exactly the missing standalone theorem (`secp256k1_p_sub_one_factorization`), so landing #250 resolves this properly rather than by relabelling |
| **F5** | P2 | `notes/GLV_SEMAEV_ITERATION_001.md:217` | Bare token `proved` for the full coordinatewise classification, which is **certificate-backed only** — contradicting line 83 of the same file and `VERIFIED.md:259` | Change the cell to `proved (certificate-replayed; not kernel-checked)` |
| **F6** | P2 | `BARRIERS.md:139–141` | "the decomposition collapses to one equation … as hard as the original" is contradicted by the repository's own route record (`ECDLP_DECISION_SUBSTRATE.json:771`) and by PKC Algorithm 1 Step 4b | Qualify the subject: it holds for a factor base given only by a coordinate condition; published prime-field variants adjoin `m` univariate equations |
| **F7** | P3 | `SC-GLV-ENDOMORPHISM`, and two others | `kernel_verified` locators that do not carry the asserted statement — e.g. "order three"/"automorphism" is asserted at `secp256k1_glvHom_ne_id`, whose statement is only `glvHom ≠ id` | Repoint at `glvPoint_cube_eq_id`, or split into nontriviality and order-three claims |
| **F8** | P3 | `BARRIERS.md:422–424` | "still the only Lean Semaev … anywhere" — a **universal priority claim inferred from a bounded dated scan**, while `notes/GLV_SEMAEV_ITERATION_001.md:347` states the correct rule | Restate as "not surfaced by the dated scan …; absence from that scan is not evidence of absence" |
| **F9** | P3 | `experiments/HYPOTHESES.yaml:253` | Cites **P1** (an `m = 2` Tonelli–Shanks solve) as the source of a pure-arithmetic `p-1` fact, and scopes it as "`p-1`-smoothness routes look weak" — wider than proved | Restate with the arithmetic provenance and the exact arity bound |
| **F10** | P3 | `tasks/ECDLP_RESEARCH.md:272–274, 337–339`; `data/source_registry.json` (25 ids) | **Yokoyama 2020 is entirely absent from the source registry**, so TASK-014's exit criterion about it has no object | Add `yokoyama_yasuda_takahashi_kogure2020`. This audit obtained the full text with a pinned sha256, so it can be ingested as read |

**Confirmations — the repository is right where a defect was expected.** Reported because an audit
that only lists faults is not calibrated.

- **C1** — `D^m/(m!·p)` is **not** treated as canonical anywhere. A repository-wide grep returns
  exactly one hit: the caveat itself, at `tasks/ECDLP_RESEARCH.md:305–306`. Correct discipline.
- **C2** — the `p-1` smoothness screen closes only what it proves. `EDD-2026-07-25-003` records
  `scope: mechanism_instance_only`, `route_effect: none`, `authorization: none`, and an explicit
  reopening condition. This is the model F1's correction should follow.
- **C3** — *the strongest point in the baseline.* The fixed-target GLV hypothesis is **already
  stated as `x(R) != 0`**, not `R != O`, in every layer, with `r = 0` named as the exceptional
  locus. **This audit's orchestrator got it wrong and the repository got it right.** Available
  strengthening, not a fix: the locus is now known **empty** for secp256k1.
- **C4** — Kudo is pinned `full_text_unread` with a **dedicated gate clause**
  (`check_scientific_semantics.py:164–165`), and there is **no** Kudo source claim, cost quantity,
  or barrier anywhere. Exactly right, and it is what keeps U3 honest.
- **C5** — no threat-model mismatch. Five disjoint models declared; every mechanism cell carries
  `classical-single-target-plain`; the Luo et al. 2026 quantum figures appear only under the
  fault-tolerant model.

**One correction this audit owes to earlier work in this repository's orbit, not to the
repository:** the claim that `S_8` is "the largest Semaev polynomial ever computed" is wrong as
stated. FHJRV 2014's record object is the 8th **symmetrized** polynomial `P_{phi,8}`, and their
Table 1 records that classical `S_7` and `S_8` were **not** computed. The construction also needs
a rational small-order torsion point, which secp256k1 does not have.

---

## 7. Unresolved acquisition records

**Kudo, Yokota, Takahashi, Yasuda, CANS 2018 — NOT OBTAINED. Read status: `abstract_only`.**

Routes tried and their exact failures: Springer (403 on every path), eprint/arXiv/HAL (no
version exists), the author's page (403, no Wayback snapshot), Semantic Scholar mirrors, CiteSeerX,
dblp-linked copies, Kyushu University institutional repository, NII/CiNii, researchmap.jp, KAKEN,
and a search for a thesis or later same-group paper restating the result with proof.

**Consequence — this must remain blocked.** The repository's assertion that the hybrid method
fixes `k` variables and yields `d^k` subsystems of the *same structural type*, and therefore
cannot move the exponent, is an **inference with no primary-source anchor**. It is not certified
by this audit in either direction. No novelty claim is permitted in this mechanism family while
the body is unread. The gate at `check_scientific_semantics.py:164–165` correctly enforces the
read status and should stay.

**One untried route worth a reviewer-hour:** the WCC 2017 precursor by the same group — Yokota,
Kudo, Yasuda, *Practical limit of index calculus algorithms for ECDLP over prime fields*.

Also not obtained, with claims scoped accordingly: the **published** Experimental Mathematics
version of [ZM2025] (only arXiv:2310.04132v1 was read — no assertion is made that the published
theorem statements or hypotheses match); the **INDOCRYPT proceedings** text of [LV2018] (only
arXiv:1703.07544v3 — note the brief lists three authors while the arXiv v3 title page carries
two, and this audit does not resolve which is correct); **page 14 of 15** of arXiv:2607.09814v1;
and **Semaev 2004** eprint 2004/031.

---

## 8. Successor candidate

**None is proposed.** Zero candidates is an acceptable outcome under the brief, and it is the
honest one here.

The one direction with an open window — PKC instance (ii) at `m ∈ [10,16]` — fails the candidate
contract at the first gate: it has no **non-generic information source** that is both exact and
target-relevant, because its entire cost hinges on `T(E,m,L)`, which the source declines to bound
(U1) and which this audit could bound only by a transfer that is itself unanchored (U2). A
candidate whose falsifiable prediction reduces to "the solving degree is at most 4–5, we think"
is not a specified mechanism; it is a restatement of the open problem. Proposing it would convert
retained uncertainty into a fundable object, which is the failure mode this whole review exists to
prevent.

---

## 9. Final project decision

| Direction | Decision | One-line reason |
|---|---|---|
| **1. Petit smooth-subgroup / composed-map, instance (i)** | **`STOP`** | Closed unconditionally on secp256k1 by divisor arithmetic plus a representation-free counting bound, `m ∈ [2,118]`, `+59.4` to `+95.6` bits |
| **1′. Petit instance (ii), auxiliary curve / isogeny** | **`PARK`** | Open only at `m ∈ [10,16]`, and only on an unbounded `T` the source declines to bound. Not a candidate; revisit if and only if a solving-degree bound for structured `V` appears |
| **2. Connected-`S3` GLV phase rigidity** | **`STOP`** | Settled mathematics, already correctly stated in the baseline, and decision-irrelevant: the group is trivial for every `x(R) != 0`, and its order is constant in `m`. Close as a correctness note. No Lean work |
| **3. Zero-minor guess-and-determine** | **`STOP`** | The explicit exhaustive implementation costs `>= 2^248.88` under the paper's own model; the lineage's own parameterization sets the candidate count `≈ p`. Four openings preserved and unclosed |

**Highest expected information value per reviewer-hour, in order:** (1) defect **F1**, because it
is machine-enforced and currently mis-sizes the only live cell by two arities; (2) defect **F2**,
now cheaply fixable in the *upgrade* direction since this audit obtained the Amadori full text;
(3) the Kudo acquisition via the WCC 2017 precursor, which is the only thing keeping U3 an
inference; (4) ingesting Yokoyama (F10) so the TASK-014 exit criterion has an object.

**No experiment is authorized. No route is promoted. No novelty is claimed. `secp256k1` remains a
forbidden target.**
