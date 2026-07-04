# Ward's theorem (★₁) for `normEDS` — design + sympy-verified certificates

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

## Next actions when resuming
1. Transcribe the 14 base-slice certificates as abstract free-`V` `linear_combination` lemmas
   (add `preNormEDS` doubling API + `e`-parity bookkeeping), kernel-verify on the server.
2. Formalize `V k = W k · b^(-e k)` bridge (or work the whole induction at V-level, transport at the end).
3. Run the R-descent (four-index relation) design pass for the outer step (`n ≥ 4`), then transcribe.
4. Assemble via `normEDSRec`; `IsEllSequence (normEDS) := isEllSequence_of_rec_one …`; optionally `IsDivSequence`.
