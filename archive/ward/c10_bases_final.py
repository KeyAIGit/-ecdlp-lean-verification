import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from tracked_gb2 import TrackedGB

J7 = list(range(-3,4)); J8 = list(range(-3,5))
v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J8}
_gb = {}
def gb7(par):
    if par not in _gb:
        t0 = time.time()
        rules = window_rules(v, J7, par, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
        gens = [v[j] for j in J7] + [B, c, d]
        _gb[par] = (TrackedGB([r_ for _,r_,_ in rules], gens), rules, gens)
        print(f"[J7 GB par={par} built {time.time()-t0:.0f}s]", flush=True)
    return _gb[par]

def solve(tag, E, J, par):
    t0 = time.time()
    gens = [v[j] for j in J] + [B, c, d]
    rules = window_rules(v, J, par, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    names = [n_ for n_,_,_ in rules]; exprs = [r_ for _,r_,_ in rules]
    rem1, cof1 = reduce_full(sp.expand(E), rules, gens)
    total = {n_: sp.expand(cof1.get(n_,0)) for n_ in names}
    print(f"\n=== {tag}: greedy left {0 if rem1==0 else len(sp.Poly(rem1,*gens).terms())} terms", flush=True)
    if rem1 != 0:
        gbo, rules7, gens7 = gb7(par)
        ok, cof2, rem2 = gbo.express(rem1)
        print(f"   J7-GB expressed={ok} ({time.time()-t0:.0f}s)", flush=True)
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

# K certificate (both parities) via J7 GB directly
def K_rel(i, par):
    ek = e(par+i); ek1 = e(par+i+1)
    return ( c*B**ek*v[i]**3*v[i+2] + c*B**ek1*v[i-1]*v[i+1]**3
           + c*v[i-1]**2*v[i+2]**2 - c**2*v[i]**2*v[i+1]**2
           - (B+d)*v[i-1]*v[i]*v[i+1]*v[i+2] )
for par in [0,1]:
    gbo, rules7, gens7 = gb7(par)
    ok, cof, rem = gbo.express(sp.expand(K_rel(0, par)))
    print(f"\n=== K(t) certificate par={par}: expressed={ok}", flush=True)
    if ok:
        n7 = [n_ for n_,_,_ in rules7]; e7 = [r_ for _,r_,_ in rules7]
        s = K_rel(0, par) - sum(cof.get(k_,0)*e7[k_] for k_ in range(len(e7)))
        print("   exact recheck:", sp.expand(s) == 0, flush=True)
        for k_, cf_ in sorted(cof.items()):
            if cf_ != 0:
                print(f"   [{n7[k_]}] * ({sp.factor(cf_)})", flush=True)

for par in [0,1]:
    E = sp.expand( VE_expr(v,2)*VE_expr(v,-1) - c**2*VE_expr(v,1)*VE_expr(v,0)
        + d*VO_expr(v,0,par)**2 )
    solve(f"slice-3(I) m=2t+1, t%2={par}", E, J8, par)
for par in [0,1]:
    E = sp.expand( VO_expr(v,1,(par+1)%2)*VE_expr(v,-1)
        - c*VE_expr(v,1)*VO_expr(v,-1,(par+1)%2) + d*VO_expr(v,0,par)*VE_expr(v,0) )
    solve(f"slice-2(II) m=2t, t%2={par}", E, J7, par)
for par in [0,1]:
    E = sp.expand( VE_expr(v,2)*VO_expr(v,-1,(par+1)%2)
        - c*VO_expr(v,1,(par+1)%2)*VE_expr(v,0) + d*VE_expr(v,1)*VO_expr(v,0,par) )
    solve(f"slice-2(II) m=2t+1, t%2={par}", E, J8, par)
print("\nDONE", flush=True)
