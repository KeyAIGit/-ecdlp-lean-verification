import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from tracked_gb import TrackedGB

v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in range(-3,4)}
gens = [v[j] for j in range(-3,4)] + [B, c, d]

for par_t in [0, 1]:
    E = sp.expand( VO_expr(v, 1, (par_t+1)%2)*VO_expr(v, -2, (par_t+2)%2)
        - c**2*VO_expr(v, 0, par_t)*VO_expr(v, -1, (par_t+1)%2)
        + B*d*VE_expr(v, 0)**2 )
    rules = window_rules(v, range(-3,4), par_t,
                         {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    names = [n_ for n_, _, _ in rules]
    exprs = [r_ for _, r_, _ in rules]
    gb = TrackedGB(exprs, gens)
    ok, cof, rem = gb.express(E)
    print(f"\n=== slice-3(I) m=2t, t%2={par_t}: expressed = {ok}")
    if ok:
        s = E - sum(cf*ex for cf, ex in zip(cof, exprs))
        exact = sp.expand(s) == 0
        print("   exact recheck:", exact)
        for n_, cf in zip(names, cof):
            cf = sp.expand(cf)
            if cf != 0:
                # integrality check
                pol = sp.Poly(cf, *gens)
                dens = [sp.Rational(x).q for x in pol.coeffs()]
                print(f"   [{n_}] * ({sp.factor(cf)})   int={all(q==1 for q in dens)}")
