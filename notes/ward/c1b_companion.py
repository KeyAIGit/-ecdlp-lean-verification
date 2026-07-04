import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, reduce_full, check_certificate

b, c, d = sp.symbols('b c d')
w = {j: sp.Symbol(f'w{j}'.replace('-','m')) for j in range(-3,4)}
def O(r):  return w[r+2]*w[r]**3 - w[r-1]*w[r+1]**3
def Ev(r): return w[r-1]**2*w[r]*w[r+2] - w[r-2]*w[r]*w[r+1]**2
S = {i: w[i+2]*w[i-2] - b**2*w[i+1]*w[i-1] + c*w[i]**2 for i in [-1,0,1]}
H3 = w[3]*w[-3] - c**2*w[1]*w[-1] + b**2*d*w[0]**2
Tp = w[1]*w[3]*w[-2]**2 - w[2]**2*w[-1]*w[-3] - d*Ev(0)   # T'(t) defect
E = sp.expand(O(1)*O(-2) - c**2*O(0)*O(-1) + d*Ev(0)**2)
gens = [w[j] for j in range(-3,4)] + [b, c, d]

# 1) numeric check of T' on real EDS (three parameter choices, k in range)
ok = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 60)
    W = make_W(V, sp.Integer(bv))
    for k in range(-12,13):
        expr = W(k+1)*W(k+3)*W(k-2)**2 - W(k+2)**2*W(k-1)*W(k-3) - dv*(W(k-1)**2*W(k)*W(k+2) - W(k-2)*W(k)*W(k+1)**2)
        if expr != 0: ok = False; print("T' fails", (bv,cv,dv), k)
print("T' numeric:", ok)

# 2) is T' in the Somos ideal <S(t-1),S(t),S(t+1)>?
G = sp.groebner([S[-1], S[0], S[1]], *gens, order='grevlex')
_, r = G.reduce(sp.expand(Tp))
print("T' in <Somos>:", r == 0, "; residue:", sp.expand(r) if r != 0 else 0)
# 2b) with H3 too?
G2 = sp.groebner([S[-1], S[0], S[1], H3], *gens, order='grevlex')
_, r2 = G2.reduce(sp.expand(Tp))
print("T' in <Somos,Star3>:", r2 == 0, "; residue:", sp.expand(r2) if r2 != 0 else 0)

# 3) E in <Somos, Star3, T'>?
G3 = sp.groebner([S[-1], S[0], S[1], H3, Tp], *gens, order='grevlex')
_, r3 = G3.reduce(E)
print("E in <Somos,Star3,T'>:", r3 == 0)
