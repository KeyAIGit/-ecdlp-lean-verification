import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, reduce_full, check_certificate, e

# --- numeric check of V-level T' (parity-uniform, B-free) ---
ok = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 40)
    for k in range(-12,13):
        expr = V(k+1)*V(k+3)*V(k-2)**2 - V(k+2)**2*V(k-1)*V(k-3) \
             - dv*(V(k-1)**2*V(k)*V(k+2) - V(k-2)*V(k)*V(k+1)**2)
        if expr != 0: ok=False; print("T'_V fail", (bv,cv,dv), k)
print("T'_V numeric (parity-uniform, B-free):", ok)

# --- Certificate 1: Star_W(2t,3), W-level, greedy division with T' added ---
b, c, d = sp.symbols('b c d')
w = {j: sp.Symbol(f'w{j}'.replace('-','m')) for j in range(-3,4)}
def O(r):  return w[r+2]*w[r]**3 - w[r-1]*w[r+1]**3
def Ev(r): return w[r-1]**2*w[r]*w[r+2] - w[r-2]*w[r]*w[r+1]**2
S = {i: w[i+2]*w[i-2] - b**2*w[i+1]*w[i-1] + c*w[i]**2 for i in [-1,0,1]}
H3 = w[3]*w[-3] - c**2*w[1]*w[-1] + b**2*d*w[0]**2
Tp = w[1]*w[3]*w[-2]**2 - w[2]**2*w[-1]*w[-3] - d*Ev(0)
E = sp.expand(O(1)*O(-2) - c**2*O(0)*O(-1) + d*Ev(0)**2)
gens = [w[j] for j in range(-3,4)] + [b, c, d]
rules = [
    ("Star3(t)", H3,  w[3]*w[-3]),
    ("S(t+1)",   S[1], w[3]*w[-1]),
    ("S(t-1)",   S[-1],w[1]*w[-3]),
    ("S(t)",     S[0], w[2]*w[-2]),
    ("T'(t)",    Tp,  w[1]*w[3]*w[-2]**2),
]
rem, cof = reduce_full(E, rules, gens)
print("Cert1 E-remainder:", rem)
rbn = {n: r for n, r, _ in rules}
print("Cert1 E-check:", check_certificate(E, rbn, cof))
for n_, cf in sorted(cof.items()):
    print(f"  coeff[{n_}] =", sp.factor(cf))
