# Generic analysis domain corpus (atomic claims + status)

Claim corpus for the **generic analysis** domain — the domain-neutral shelf of the Research
OS. It is not a research program and it belongs to no conjecture: it holds analysis and
measure-theory lemmas that are stated over pinned Mathlib objects, have **zero repository
prerequisites**, and are consumable by any domain. Each claim below is verified by the Lean
kernel in the `ResearchOS` library (`ResearchOS/Analysis/`), under the same no-`sorry` /
no-axiom gates as every other lane. No claim is asserted before the kernel accepts it.

**Why the shelf is separate.** A generic lemma filed inside a conjecture program's subtree
reads as that program's content. Keeping it here — with its own claim-id prefix (`MB-`) and
its own subtree (`ResearchOS/Analysis/`, machine-enforced by
`scripts/gen_researchos_registry.py`) — keeps the inventory honest in both directions: the
conjecture lanes do not inflate, and the generic lemma is still findable and reusable.

**No barrier effect.** Nothing on this shelf closes, advances, or partially closes any
barrier row of `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` or any `S1-*` item.
Generic machinery lowers the cost of a future exit but never retires a row. Nothing here
bears on the truth of the Riemann Hypothesis or of any other open problem.

Provenance: `domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md` (UPSTREAM-POOL §6), whose
statement surface MB1–MB4 was independently accepted 2026-08-07
(`notes/reviews/MELLIN_ACCEPTANCE_2026_08_07.md`) and promoted to the built surface under
`notes/reviews/MELLIN_PROMOTION_2026_08_07.md`. The contract lives in the RH lane's
directory because that lane's upstream pool proposed the item; the statements themselves
mention no object of that lane.

| id | claim | status | evidence |
|---|---|---|---|
| MB-1 | `‖mellin f s‖` is bounded by `∫ t in Ioi 0, t ^ (re s − 1) * ‖f t‖`, with no hypothesis at all | **verified** | `ResearchOS/Analysis/MellinBound.lean` (`norm_mellin_le`) |
| MB-2 | the same bound through a pointwise majorant `g ≥ ‖f‖` on `Ioi 0`, integrability assumed on the bound rather than on `f` | **verified** | `ResearchOS/Analysis/MellinBound.lean` (`norm_mellin_le_of_norm_le`) |
| MB-3A | `∫ t in Ioi 0, t ^ (σ − 1) * g t` is nondecreasing in `σ` for `g ≥ 0` vanishing on `Ioo 0 1` | **verified** | `ResearchOS/Analysis/MellinBound.lean` (`setIntegral_rpow_mul_mono_exponent`) |
| MB-3B | on that same integrand class, one integrability check at `re s = b` bounds `‖mellin f s‖` for every `s` with `re s ≤ b` | **verified** | `ResearchOS/Analysis/MellinBound.lean` (`norm_mellin_le_of_re_le`) |
| MB-4 | endpoint data at `re s = a` and `re s = b` bounds `‖mellin f s‖` by the sum of the two endpoint integrals, uniformly on `a ≤ re s ≤ b` | **verified** | `ResearchOS/Analysis/MellinBound.lean` (`norm_mellin_le_add_of_re_mem_Icc`) |

**Limits of the surface.** These are norm inequalities only. No Mellin transform is
evaluated, none is shown convergent (MB-2 … MB-4 *assume* integrability of the bound), and
no analytic continuation, functional equation, or growth statement is made anywhere.
