import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, e
from vmachine import B, c, d, VE_expr, VO_expr, window_rules

# --- numeric check of V-level U with decoration B^{e(k)} on the c V(k)^3 term ---
ok = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 40)
    Bv = bv**4
    for k in range(-12,13):
        x = cv*(V(k+1)**2*V(k-2) + V(k+2)*V(k-1)**2) \
          - (Bv+dv)*V(k+1)*V(k)*V(k-1) + Bv**e(k)*cv*V(k)**3
        if x != 0: ok = False; print("U_V fail", (bv,cv,dv), k)
print("U_V numeric (with B^{e(k)} c V(k)^3):", ok)

def U_rel(v, i, par_center):
    ek = e(par_center + i)
    return ( c*(v[i+1]**2*v[i-2] + v[i+2]*v[i-1]**2)
           - (B+d)*v[i+1]*v[i]*v[i-1] + B**ek*c*v[i]**3 )

# --- is U in the per-window two-family ideal? ---
J7 = list(range(-3,4))
v7 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J7}
gens7 = [v7[j] for j in J7] + [B, c, d]
for par_t in [0,1]:
    rules = window_rules(v7, J7, par_t, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    G = sp.groebner([r_ for _,r_,_ in rules], *gens7, order='grevlex')
    _, r = G.reduce(sp.expand(U_rel(v7, 0, par_t)))
    print(f"par={par_t}: U in <window I/II instances>: {r == 0}")
