import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, window_rules
from tracked_gb import TrackedGB

def solve(tag, E, J, par_t):
    v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J}
    # E is built by caller with same symbol naming; rebuild gens
    gens = [v[j] for j in J] + [B, c, d]
    rules = window_rules(v, J, par_t, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    names = [n_ for n_, _, _ in rules]; exprs = [r_ for _, r_, _ in rules]
    gb = TrackedGB(exprs, gens)
    ok, cof, rem = gb.express(E)
    print(f"\n=== {tag}: expressed = {ok}")
    if not ok:
        print("   residue:", sp.factor(rem)); return
    s = E - sum(cf*ex for cf, ex in zip(cof, exprs))
    print("   exact recheck:", sp.expand(s) == 0)
    used = []
    for n_, cf in zip(names, cof):
        cf = sp.expand(cf)
        if cf != 0:
            pol = sp.Poly(cf, *gens)
            isint = all(sp.Rational(x).q == 1 for x in pol.coeffs())
            used.append(n_)
            print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}")
    return used

# symbols shared
J7 = list(range(-3,4)); J8 = list(range(-3,5))
v7 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J7}
v8 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J8}

# ---- slice-3(I), m = 2t+1: E = VE(t+2)VE(t-1) - c^2 VE(t+1)VE(t) + d VO(t)^2 ----
for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VE_expr(v8, -1)
        - c**2*VE_expr(v8, 1)*VE_expr(v8, 0)
        + d*VO_expr(v8, 0, par_t)**2 )
    solve(f"slice-3(I) m=2t+1, t%2={par_t}", E, J8, par_t)

# ---- slice-2(II): V(m+3)V(m-2) = c V(m+2)V(m-1) - d V(m+1)V(m) ----
# m = 2t:  VO(t+1)VE(t-1) - c VE(t+1)VO(t-1) + d VO(t)VE(t)
for par_t in [0,1]:
    E = sp.expand( VO_expr(v7, 1, (par_t+1)%2)*VE_expr(v7, -1)
        - c*VE_expr(v7, 1)*VO_expr(v7, -1, (par_t+1)%2)
        + d*VO_expr(v7, 0, par_t)*VE_expr(v7, 0) )
    solve(f"slice-2(II) m=2t, t%2={par_t}", E, J7, par_t)
# m = 2t+1: VE(t+2)VO(t-1) - c VO(t+1)VE(t) + d VE(t+1)VO(t)
for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VO_expr(v8, -1, (par_t+1)%2)
        - c*VO_expr(v8, 1, (par_t+1)%2)*VE_expr(v8, 0)
        + d*VE_expr(v8, 1)*VO_expr(v8, 0, par_t) )
    solve(f"slice-2(II) m=2t+1, t%2={par_t}", E, J8, par_t)
