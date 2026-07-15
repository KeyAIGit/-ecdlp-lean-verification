import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, window_rules
from tracked_gb2 import TrackedGB

J8 = list(range(-3,5)); J7 = list(range(-3,4))
v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J8}
V5 = vsmall(5)  # B*d - c^3
_gb = {}
def gb7(par):
    if par not in _gb:
        rules = window_rules(v, J7, par, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
        gens = [v[j] for j in J7] + [B, c, d]
        _gb[par] = (TrackedGB([r_ for _,r_,_ in rules], gens), rules)
    return _gb[par]

def solve(tag, E, J, par):
    gens = [v[j] for j in J] + [B, c, d]
    rules = window_rules(v, J, par, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    names = [n_ for n_,_,_ in rules]; exprs = [r_ for _,r_,_ in rules]
    rem1, cof1 = reduce_full(sp.expand(E), rules, gens)
    total = {n_: sp.expand(cof1.get(n_,0)) for n_ in names}
    print(f"\n=== {tag}: greedy left {0 if rem1==0 else len(sp.Poly(rem1,*gens).terms())} terms", flush=True)
    if rem1 != 0:
        gbo, rules7 = gb7(par)
        ok, cof2, rem2 = gbo.express(rem1)
        print(f"   J7-GB expressed={ok}", flush=True)
        if not ok:
            print("   residue:", sp.factor(rem2), flush=True); return
        n7 = [n_ for n_,_,_ in rules7]
        for k_, cf_ in cof2.items():
            nm = n7[k_]
            if nm not in total:
                total[nm] = 0; names.append(nm); exprs.append(rules7[k_][1])
            total[nm] = sp.expand(total[nm] + cf_)
    s = E - sum(total[n_]*ex for n_, ex in zip(names, exprs))
    print("   exact recheck:", sp.expand(s) == 0, flush=True)
    for n_ in names:
        cf = total.get(n_, 0)
        if cf != 0:
            isint = all(sp.Rational(x).q == 1 for x in sp.Poly(cf, *gens).coeffs())
            print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}", flush=True)

# slice-3(II): V(m+4)V(m-3) - c*d*V(m+2)V(m-1) + (B*d - c^3)*V(m+1)V(m) = 0
# m = 2t: VE(t+2)*VO(t-2) - c*d*VE(t+1)*VO(t-1) + V5*VO(t)*VE(t)
for par in [0,1]:
    E = sp.expand( VE_expr(v,2)*VO_expr(v,-2,(par+2)%2)
        - c*d*VE_expr(v,1)*VO_expr(v,-1,(par+1)%2)
        + V5*VO_expr(v,0,par)*VE_expr(v,0) )
    solve(f"slice-3(II) m=2t, t%2={par}", E, J8, par)
# m = 2t+1: VO(t+2)*VE(t-1) - c*d*VO(t+1)*VE(t) + V5*VE(t+1)*VO(t)
for par in [0,1]:
    E = sp.expand( VO_expr(v,2,(par+2)%2)*VE_expr(v,-1)
        - c*d*VO_expr(v,1,(par+1)%2)*VE_expr(v,0)
        + V5*VE_expr(v,1)*VO_expr(v,0,par) )
    solve(f"slice-3(II) m=2t+1, t%2={par}", E, J8, par)
print("\nDONE", flush=True)
