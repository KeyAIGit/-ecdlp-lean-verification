import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, e
from vmachine import B, c, d, window_rules

def K_rel(v, i, par):  # K(k) with k = center+i; par = parity of center
    ek = e(par + i); ek1 = e(par + i + 1)
    return ( c*B**ek*v[i]**3*v[i+2] + c*B**ek1*v[i-1]*v[i+1]**3
           + c*v[i-1]**2*v[i+2]**2 - c**2*v[i]**2*v[i+1]**2
           - (B+d)*v[i-1]*v[i]*v[i+1]*v[i+2] )

# 1) numeric
ok = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 40)
    Bv = bv**4
    for k in range(-12,13):
        x = ( cv*Bv**e(k)*V(k)**3*V(k+2) + cv*Bv**e(k+1)*V(k-1)*V(k+1)**3
            + cv*V(k-1)**2*V(k+2)**2 - cv**2*V(k)**2*V(k+1)**2
            - (Bv+dv)*V(k-1)*V(k)*V(k+1)*V(k+2) )
        if x != 0: ok = False; print("K fail", (bv,cv,dv), k)
print("K numeric:", ok)

# 2) K in full 7-window two-family ideal?
J7 = list(range(-3,4))
v7 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J7}
gens7 = [v7[j] for j in J7] + [B, c, d]
for par in [0,1]:
    rules = window_rules(v7, J7, par, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    G = sp.groebner([r_ for _,r_,_ in rules], *gens7, order='grevlex')
    _, r = G.reduce(sp.expand(K_rel(v7, 0, par)))
    print(f"par={par}: K(t) in <7-window I/II instances>: {r == 0}",
          "" if r == 0 else sp.factor(r))
