#!/usr/bin/env python3
"""EDS `linear_combination` cofactor generator (N7 algebra-wall grind tooling).

The N7-uniform algebra walls (`even_x/odd_x/even_y/odd_y_algebra` in
`Ecdlp/Targets/n7_uniform_carrier_induction.lean`) and the shared doubling
identities (I)/(II) reduce to curve-generic scalar cores whose inductive step
lemmas each need a `linear_combination (norm := ring1) …` cofactor bundle over a
FREE `normEDS` sequence `W : ℤ → R` — exactly the shape of the proven
`somos4_odd_step` / `somos4_even_step_scaled` (`Ecdlp/Proved/NormEDSSomos4.lean`).

`notes/N7_EVEN_X_REDUCTION.md` recorded the reduction but noted the cofactor
bundles "must be machine-generated (sympy Groebner / linear-solve over ℤ[β,c,d,x])"
and — at the time — that this was infeasible in-container. **It is not: sympy is
available and does it.** This script is that generator.

Two things it provides, both kernel-agnostic (the Lean kernel remains the sole
judge — a generated bundle is only trusted once `lake`/`n7-stem-check` accepts it):

1. `self_test()` — reproduces the KNOWN `somos4_odd_step` bundle and checks the
   residual is exactly 0, validating the free-sequence encoding and the solver.
2. `solve_cofactors(goal, hyps, gens, max_deg)` — an ansatz linear-solve that
   returns cofactors **against the original hypotheses** (Lean-ready, unlike a
   raw Groebner reduction which is against the basis), or None if no bundle of
   the given degree budget exists.

Usage: `python3 scripts/certs/eds_cofactor_gen.py` runs the self-test.
Downstream (subsequent grind cycles): import `solve_cofactors`, feed the CORE-I /
CORE-II even/odd step goals + hypotheses, transcribe the returned bundle into the
Lean step lemma, and let CI judge.
"""

import sympy as sp


def solve_cofactors(goal, hyps, gens, order='lex'):
    """Return Lean-ready cofactors q_i with goal == sum_i q_i * hyps_i, or None.

    Uses multivariate division (`sympy.reduced`) of `goal` by the ORIGINAL
    hypothesis list — so the returned quotients are cofactors against exactly the
    hypotheses a Lean `linear_combination (norm := ring1) …` cites (not against a
    Groebner basis). Order `gens` with the "output"/doubled-index variables FIRST
    so the (triangular, linear-in-one-var) recurrence hypotheses eliminate them and
    the remainder collapses to 0. Returns None if the remainder is nonzero (goal not
    reducible by these hyps in this order → widen the hypothesis set or reorder).
    """
    Q, r = sp.reduced(goal, hyps, *gens, order=order)
    if sp.expand(r) != 0:
        return None
    Q = [sp.expand(q) for q in Q]
    assert sp.expand(goal - sum(q * h for q, h in zip(Q, hyps))) == 0
    return Q


def self_test():
    """Reproduce + re-solve the proven somos4_odd_step bundle."""
    b, c = sp.symbols('b c')
    Wm2, Wm1, W0, W1, W2, W3 = sp.symbols('Wm2 Wm1 W0 W1 W2 W3')
    D2M_m1, D2M, D2M_p1, D2M_p2, D2M_p3 = sp.symbols('D2M_m1 D2M D2M_p1 D2M_p2 D2M_p3')
    hyps = [
        D2M_p3 - (W3 * W1**3 - W0 * W2**3),
        D2M_p2 * b - (W0**2 * W1 * W3 - Wm1 * W1 * W2**2),
        D2M * b - (Wm1**2 * W0 * W2 - Wm2 * W0 * W1**2),
        D2M_p1 - (W2 * W0**3 - Wm1 * W1**3),
        D2M_m1 - (W1 * Wm1**3 - Wm2 * W0**3),
        W2 * Wm2 - (b**2 * W1 * Wm1 - c * W0**2),
        W3 * Wm1 - (b**2 * W2 * W0 - c * W1**2),
    ]
    goal = D2M_p3 * D2M_m1 - (b**2 * D2M_p2 * D2M - c * D2M_p1**2)
    # 1) validate the KNOWN bundle (from NormEDSSomos4.lean)
    known = (D2M_m1 * hyps[0] + (-b * D2M) * hyps[1]
             + (-(W0**2 * W1 * W3 - Wm1 * W1 * W2**2)) * hyps[2]
             + (c * (D2M_p1 + (W2 * W0**3 - Wm1 * W1**3))) * hyps[3]
             + (W3 * W1**3 - W0 * W2**3) * hyps[4]
             + (W0 * W2 * (W2 * W0**3 - Wm1 * W1**3)) * hyps[5]
             + (-Wm1 * W1 * (W2 * W0**3 - Wm1 * W1**3)) * hyps[6])
    assert sp.expand(goal - known) == 0, "known somos4 bundle residual != 0"
    # 2) the solver itself must (re)produce a valid bundle from scratch. Order the
    #    doubled-index vars first so the (triangular) recurrence hyps eliminate them.
    gens = [D2M_p3, D2M_p2, D2M_p1, D2M, D2M_m1, W3, W2, W1, W0, Wm1, Wm2, b, c]
    Q = solve_cofactors(goal, hyps, gens)
    assert Q is not None, "solver failed to find a bundle"
    assert sp.expand(goal - sum(q * h for q, h in zip(Q, hyps))) == 0
    print("self_test OK: known bundle residual 0; solver reproduced a valid bundle "
          f"({sum(1 for q in Q if q != 0)}/{len(Q)} nonzero cofactors).")


if __name__ == '__main__':
    self_test()
