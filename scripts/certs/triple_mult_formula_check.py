#!/usr/bin/env python3
"""N7@3 certificate — the tripling x-coordinate formula x(3•P) = Φ₃/ΨSq₃ for y²=x³+7.

Verifies the two-step certificate transcribed in Ecdlp/Proved/TripleMultiplicationFormula.lean:
  step A (from hℓ3):  (s3²−(s2²−2x)−x)·d² = W² − ((s2²−2x)+x)·d²,  d=s2²−3x, W=−(s2·d+y)−y
  step B (master):    (W²−((s2²−2x)+x)d²)·ΨSq₃ − Φ₃·d²,  times (2y)⁴, lies in ⟨2y·s2−3x², y²−x³−7⟩
with ΨSq₃=9x⁸+504x⁵+7056x², Φ₃=x⁹−672x⁶+2352x³+21952. Prints CERT_OK.
Nothing here enters Lean; it is transcription insurance for the CAS-derived linear_combination.
"""
import sympy as sp

def main() -> int:
    x, y, s2, s3 = sp.symbols('x y s2 s3')
    d = s2**2 - 3*x
    W = -(s2*d + y) - y
    PsiSq3 = 9*x**8 + 504*x**5 + 7056*x**2
    Phi3   = x**9 - 672*x**6 + 2352*x**3 + 21952
    g_sl2, g_curve = 2*y*s2 - 3*x**2, y**2 - (x**3 + 7)

    # step A: (s3²−(s2²−2x)−x)·d² − (W²−((s2²−2x)+x)d²) = (d·s3+W)(d·s3−W)
    X3 = s3**2 - (s2**2 - 2*x) - x
    stepA = sp.expand((X3*d**2 - (W**2 - ((s2**2-2*x)+x)*d**2)) - (d*s3+W)*(d*s3 - W))
    # step B: (2y)⁴·MB ∈ ideal
    MB = sp.expand((W**2 - ((s2**2-2*x)+x)*d**2)*PsiSq3 - Phi3*d**2)
    _, r = sp.reduced(sp.expand((2*y)**4 * MB), [g_sl2, g_curve], s2, y, x, order='lex')
    # end-to-end: group-law tripling equals Φ₃/ΨSq₃ (on the variety, y≠0, d≠0)
    l2 = (3*x**2)/(2*y); x2 = sp.simplify(l2**2 - 2*x); y2 = sp.simplify(l2*(x-x2)-y)
    l3 = (y2 - y)/(x2 - x); x3 = l3**2 - x2 - x
    diff = sp.numer(sp.together(sp.simplify(x3 - Phi3/PsiSq3)))
    diff = sp.rem(sp.Poly(sp.expand(diff), y), sp.Poly(y**2-(x**3+7), y)).as_expr()

    ok = (stepA == 0) and (sp.expand(r) == 0) and (sp.simplify(diff) == 0)
    print("CERT_OK" if ok else "CERT_FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
