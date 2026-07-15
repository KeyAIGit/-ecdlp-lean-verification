# Ward's theorem (★₁) for `normEDS` — design + sympy-verified certificates

Repository classification: experimental trace / archive candidate. Keep this
directory for provenance until a dedicated archive PR reviews it. It is not a
canonical source of truth for current theorem counts, public claims, or active
tasks.

Provenance: symbolic-algebra design pass (sympy). **Nothing here is kernel-verified**;
these are the design certificates to be transcribed into Lean and checked on the server,
the same pipeline that produced `Ecdlp/Proved/NormEDSSomos4.lean` (the `n=2` slice, which
IS kernel-verified). Scripts re-run standalone with `python3 <file>.py`.

## Goal
Close the open Mathlib TODO "`normEDS` satisfies `IsEllDivSequence`". With
`isEllSequence_of_rec_one` (merged) the elliptic half reduces to the `r=1` master
recurrence (★₁):

    W(m+n)·W(m−n) = W(m+1)·W(m−1)·W(n)² − W(n+1)·W(n−1)·W(m)²   for all m,n ∈ ℤ.

## Key structural findings (all numerically / Groebner verified in the scripts)

1. **The proof is forced to the `preNormEDS` ("V") level.** Set `V k := preNormEDS (b⁴) c d k`,
   `B := b⁴`, `e(k) = k mod 2`. Then `W k = V k · b^(e k)`. Every parity case of (★₁) at
   W-level equals `b^(2·e(m+n))` × a V-level identity, so W-goals follow from V-goals by
   *multiplication*, never division. Working purely at W-level is impossible: for (★₁) at
   `n=3, m` odd, every W-level certificate proves only `b²·goal = 0` (even-index W's enter
   only via `b·W(2k) = …`). The V-level doubling recurrences are `b`-clean.

2. **A second companion (★₃) is required** (beyond Somos-4). W-level:
   `b·W(m+n+1)·W(m−n) = W(n+1)W(n)·W(m+2)W(m−1) − W(n+2)W(n−1)·W(m+1)W(m)`;
   V-level (B-free, parity-uniform):
   `V(m+n+1)V(m−n) = V(n+1)V(n)V(m+2)V(m−1) − V(n+2)V(n−1)V(m+1)V(m)`.
   Proven necessary by Groebner: products `V(a)V(b)` with `a+b` **odd** (which halving
   inevitably produces) are rewritable only by (★₃). Specializations recover EVEN, ODD,
   Somos-4, and clean 3-term slices.

3. **Mutual strong induction** on `μ(m,n) = |m|+|n|` over the two families {(★₁),(★₃)},
   WLOG `m > n ≥ 0`. Base slices `n = 2, 3` of both families are certificate-complete:
   **14 sympy-verified integer `linear_combination` certificates** (all parity cases,
   m = 2t / 2t+1 × t even/odd), see `c10_out.txt`, `c12_out.txt`, plus the derived `K`
   lemma (shown to be inside the two-family ideal — not a new axiom).

4. **Outer step `n ≥ 4` — the honest gap.** The pairing phase (eliminating all `P·Q`
   cross-products via (★₁)/(★₃) instances of smaller measure) is verified, but the leftover
   pure-window tail does **not** close from the two families alone (Groebner-proven negative:
   not in `I_A + I_T`; 220 re-pairing variants and the exchange syzygies all stall). The
   classical closure (Junyan Xu's Lean approach; why Mathlib states `IsEllSequence` 4-index)
   is to run the **same halving descent on the four-index net relation**
   `R(p,q,r,s): W(p+q)W(p−q)W(r+s)W(r−s) − W(p+r)W(p−r)W(q+s)W(q−s) + W(p+s)W(p−s)W(q+r)W(q−r) = 0`,
   of which (★₁) = R(m,n,1,0). All base certificates above are the small-parameter cases of R
   and carry over unchanged. **This R-descent is the remaining (multi-session) compute.**

## File guide
- `eds_common.py`, `vmachine.py`, `outer_common.py`, `f0_numeric.py` — the V/W model + peel machine.
- `c3_bases*.py`, `c10_bases_final.py`, `c12_slodd3.py` → `c10_out.txt`, `c12_out.txt` — the 14 base-slice certificates.
- `c8_K.py`, `c1b_companion.py`, `c1e_U.py` — the K and (★₃)/U companions.
- `c4_*`, `c5_*`, `c14_*`, `c15_*`, `c16_final.py`, `c17_exchange.py` — outer-step pairing + the negative Groebner results.
- `tracked_gb*.py`, `solver.py` — the tracked-Groebner / linear-solver harness.

## Four-index relation R — descent result (second design pass, HONEST NEGATIVE)

`R(p,q,r,s) := W(p+q)W(p−q)W(r+s)W(r−s) − W(p+r)W(p−r)W(q+s)W(q−s) + W(p+s)W(p−s)W(q+r)W(q−r)`.
Files: `rwin.py`, `r0_def.py`, `r1_vlevel.py`, `r3_descent.py`, `r5_full.py`, `r6_nf.py`…`r11_nf.py`.

Verified: `R ≡ 0` numerically; **(★₁) = R(m,n,1,0)** exactly; the V-level `b⁴`-decoration table
(only one of the three R-terms ever carries a factor, always `B=b⁴`, determined by the parities of
`p,q,r,s`); the explicit coupling identity `R(s,t,1,0)_V : A0²·T1·Tm1 − A1·Am1·T0² + P0·Q0 = 0`
and the in-window R-families `R(s+i,t+j,u,v) ≡ 0`, `R(s+t,s−t,u,v) ≡ 0` (all sympy `expand==0`);
the correct multigrading is the EDS weight as a **quadratic form in the free centers s,t**
(`V(αs+βt+g) ↦ (s²,st,t²,s,t,K)`, `K=g²−1−3e(g)`), under which the even–even outer defect E is
homogeneous of weight `(8,0,8,0,0,−8)`.

**Correction to pass 1:** (★₃) is *not* literally a single `R(p,q,r,s)` (its left term `b·W(m+n+1)W(m−n)`
has too few factors). It is a derived two-term companion; the clean R-shaped statement of the same
content is `R(s,t,1,0)`.

**Honest negative finding (the real boundary).** The even–even outer step does **NOT** close as a single
low-cofactor-degree (≤6) `linear_combination` of the full in-window R-instance set + window (EVEN/ODD/
Somos) rules. Three *exact* linear-algebra membership tests — normal form modulo the four disjoint
single-window ideals plus a graded ansatz — were run with progressively richer generator sets (up to a
1122×2318 system, 185 generators) and **all are inconsistent**. So the outer-step assembly is **not one
`linear_combination`**; it requires a genuine **multi-lemma inductive development** (matching how the
classical net-relation proof — Junyan Xu's Lean approach, and why Mathlib states `IsEllSequence` 4-index —
is structured). No fabricated certificate was claimed.

**Consequence for our pipeline.** The "design one certificate per case → single `linear_combination` →
kernel-verify" pipeline that closed Somos-4 (n=2) and can close the n=2,3 slices does **not** scale to the
full `normEDS_rec_one` outer step. The full theorem is a real multi-lemma formalization (weeks-scale,
human-directed), best done referencing the existing net-relation development rather than re-derived as
single certificates.

## n=3 slice step certificates — KERNEL-VERIFIED ✅

`n3_certificates.lean` — four abstract free-`V` `linear_combination` step lemmas
(`star1_n3_double_even/odd`, `star3_n3_double_even/odd`), the n=3 analogue of the Somos-4
step lemmas. **Kernel-verified on the warm server (`lake env lean`, EXIT=0, no errors/warnings,
first try).** Fable delivered them 4-way sympy-checked incl. a reparse-from-Lean-text `ring1==0`
test. These are the discovered certificates (the hard part); they are NOT yet the assembled n=3
`normEDS` theorem — that needs the mutual (★₁)+(★₃) induction over `preNormEDS`, base cases, and
the V→W transport (heavier than Somos-4's single-family induction).

## Next actions when resuming
1. Transcribe the 14 base-slice certificates as abstract free-`V` `linear_combination` lemmas
   (add `preNormEDS` doubling API + `e`-parity bookkeeping), kernel-verify on the server.
2. Formalize `V k = W k · b^(-e k)` bridge (or work the whole induction at V-level, transport at the end).
3. Run the R-descent (four-index relation) design pass for the outer step (`n ≥ 4`), then transcribe.
4. Assemble via `normEDSRec`; `IsEllSequence (normEDS) := isEllSequence_of_rec_one …`; optionally `IsDivSequence`.
