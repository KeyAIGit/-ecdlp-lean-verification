import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, window_rules
from tracked_gb2 import TrackedGB

def solve(tag, E, J, par_t):
    t0 = time.time()
    v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J}
    gens = [v[j] for j in J] + [B, c, d]
    rules = window_rules(v, J, par_t, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    names = [n_ for n_, _, _ in rules]; exprs = [r_ for _, r_, _ in rules]
    # phase 1: greedy
    rem1, cof1 = reduce_full(sp.expand(E), rules, gens)
    total = {names[i]: sp.expand(cof1.get(names[i], 0)) for i in range(len(names))}
    print(f"\n=== {tag}: greedy left {0 if rem1==0 else len(sp.Poly(rem1,*gens).terms())} terms ({time.time()-t0:.0f}s)", flush=True)
    if rem1 != 0:
        gb = TrackedGB(exprs, gens)
        ok, cof2, rem2 = gb.express(rem1)
        print(f"   GB done ({time.time()-t0:.0f}s), expressed={ok}", flush=True)
        if not ok:
            print("   residue:", sp.factor(rem2)); return
        for k_, cf_ in cof2.items():
            total[names[k_]] = sp.expand(total[names[k_]] + cf_)
    s = E - sum(total[n_]*ex for n_, ex in zip(names, exprs))
    print("   exact recheck:", sp.expand(s) == 0)
    for n_ in names:
        cf = total[n_]
        if cf != 0:
            pol = sp.Poly(cf, *gens)
            isint = all(sp.Rational(x).q == 1 for x in pol.coeffs())
            print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}")

J7 = list(range(-3,4)); J8 = list(range(-3,5))
v7 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J7}
v8 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J8}

for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VE_expr(v8, -1) - c**2*VE_expr(v8, 1)*VE_expr(v8, 0)
        + d*VO_expr(v8, 0, par_t)**2 )
    solve(f"slice-3(I) m=2t+1, t%2={par_t}", E, J8, par_t)
for par_t in [0,1]:
    E = sp.expand( VO_expr(v7, 1, (par_t+1)%2)*VE_expr(v7, -1)
        - c*VE_expr(v7, 1)*VO_expr(v7, -1, (par_t+1)%2)
        + d*VO_expr(v7, 0, par_t)*VE_expr(v7, 0) )
    solve(f"slice-2(II) m=2t, t%2={par_t}", E, J7, par_t)
for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VO_expr(v8, -1, (par_t+1)%2)
        - c*VO_expr(v8, 1, (par_t+1)%2)*VE_expr(v8, 0)
        + d*VE_expr(v8, 1)*VO_expr(v8, 0, par_t) )
    solve(f"slice-2(II) m=2t+1, t%2={par_t}", E, J8, par_t)
print("\nDONE")
