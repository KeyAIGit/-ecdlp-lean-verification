import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import reduce_full

b, c, d = sp.symbols('b c d')
w = {j: sp.Symbol(f'w{j}'.replace('-','m')) for j in range(-3,4)}
def O(r):  return w[r+2]*w[r]**3 - w[r-1]*w[r+1]**3
def Ev(r): return w[r-1]**2*w[r]*w[r+2] - w[r-2]*w[r]*w[r+1]**2
def Evm(r): # Ev mirrored: (t -> -t) image of Ev(0) around center r
    return w[r+1]**2*w[r]*w[r-2] - w[r+2]*w[r]*w[r-1]**2
S = {i: w[i+2]*w[i-2] - b**2*w[i+1]*w[i-1] + c*w[i]**2 for i in [-1,0,1]}
H3  = w[3]*w[-3] - c**2*w[1]*w[-1] + b**2*d*w[0]**2
Tp  = w[1]*w[3]*w[-2]**2 - w[2]**2*w[-1]*w[-3] - d*Ev(0)     # T'(t)
Tpm = w[-1]*w[-3]*w[2]**2 - w[-2]**2*w[1]*w[3] - d*Evm(0)    # T'(-t) mirror
print("mirror consistency Tpm = -Tp - d*(Ev+Evm)?", sp.expand(Tpm + Tp) )  # expect -d*(Ev(0)+Evm(0)) = 0? check
E = sp.expand(O(1)*O(-2) - c**2*O(0)*O(-1) + d*Ev(0)**2)
gens = [w[j] for j in range(-3,4)] + [b, c, d]

base = [("Star3(t)", H3, w[3]*w[-3]), ("S(t+1)", S[1], w[3]*w[-1]),
        ("S(t-1)", S[-1], w[1]*w[-3]), ("S(t)", S[0], w[2]*w[-2])]
phaseA = base + [("T'(t)",  Tp,  w[1]*w[3]*w[-2]**2)]
phaseB = base + [("T'(-t)", Tpm, w[-1]*w[-3]*w[2]**2)]

total_cof = {}
rem = E
for it in range(12):
    rules = phaseA if it % 2 == 0 else phaseB
    rem, cof = reduce_full(rem, rules, gens)
    for k_, v_ in cof.items():
        total_cof[k_] = sp.expand(total_cof.get(k_, 0) + v_)
    print("phase", it, "remaining terms:", len(sp.Poly(rem, *gens).terms()) if rem != 0 else 0)
    if rem == 0:
        break
print("final remainder:", rem)
if rem == 0:
    rbn = dict([(n_, r_) for n_, r_, _ in phaseA + phaseB])
    s = E
    for n_, cf in total_cof.items():
        s = s - cf*rbn[n_]
    print("CERT1 exact check expand(E - sum cof*hyp) == 0:", sp.expand(s) == 0)
    for n_, cf in sorted(total_cof.items()):
        print(f"  coeff[{n_}] =", sp.factor(cf))
