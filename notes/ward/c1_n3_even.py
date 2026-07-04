import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import reduce_full, check_certificate

# W-level. m = 2t (even). Window symbols w[j] = W(t+j), j=-3..3, plus b,c,d
# and u[j] = W(2t+j) for the doubled values, j in {-3,-1,0,1,3}.
b, c, d = sp.symbols('b c d')
w = {j: sp.Symbol(f'w{j}'.replace('-','m')) for j in range(-3,4)}
u = {j: sp.Symbol(f'u{j}'.replace('-','m')) for j in [-3,-1,0,1,3]}

def O(r):   # ODD(r) RHS in window coords, r relative to t: W(t+r+2)W(t+r)^3 - W(t+r-1)W(t+r+1)^3
    return w[r+2]*w[r]**3 - w[r-1]*w[r+1]**3
def Ev(r):  # EVEN(r) RHS: W(t+r-1)^2 W(t+r) W(t+r+2) - W(t+r-2) W(t+r) W(t+r+1)^2
    return w[r-1]**2*w[r]*w[r+2] - w[r-2]*w[r]*w[r+1]**2

# hypotheses (expr == 0):
ODDdef = {r: u[2*r+1] - O(r) for r in [-2,-1,0,1]}        # W(2t+2r+1) = O(t+r)
EVENdef = {0: b*u[0] - Ev(0)}                              # b W(2t) = Ev(t)
S = {i: w[i+2]*w[i-2] - b**2*w[i+1]*w[i-1] + c*w[i]**2 for i in [-1,0,1]}  # Somos at k=t+i
H3 = w[3]*w[-3] - c**2*w[1]*w[-1] + b**2*d*w[0]**2         # Star3 at t (IH)

# Goal: Star(2t,3):  W(2t+3)W(2t-3) - c^2 W(2t+1)W(2t-1) + b^2 d W(2t)^2 == 0
G = u[3]*u[-3] - c**2*u[1]*u[-1] + b**2*d*u[0]**2

# Step 1: peel off the doubling hypotheses explicitly:
# G = od(t+1)*W(2t-3) + O(t+1)*od(t-2) - c^2[od(t)*W(2t-1) + O(t)*od(t-1)] + d*(bW(2t)+Ev(t))*ev(t) + E
E = O(1)*O(-2) - c**2*O(0)*O(-1) + d*Ev(0)**2
peel = (ODDdef[1]*u[-3] + O(1)*ODDdef[-2]
        - c**2*(ODDdef[0]*u[-1] + O(0)*ODDdef[-1])
        + d*(b*u[0] + Ev(0))*EVENdef[0])
print("peel exact:", sp.expand(G - peel - E) == 0)

# Step 2: reduce E modulo S(t-1), S(t), S(t+1), Star3(t)
gens = [w[j] for j in range(-3,4)] + [b, c, d]
rules = [
    ("Star3(t)",  H3,   w[3]*w[-3]),
    ("S(t+1)",    S[1], w[3]*w[-1]),
    ("S(t-1)",    S[-1],w[1]*w[-3]),
    ("S(t)",      S[0], w[2]*w[-2]),
]
rem, cof = reduce_full(E, rules, gens)
print("remainder:", rem)
if rem == 0:
    rbn = {n: r for n, r, _ in rules}
    print("check:", check_certificate(E, rbn, cof))
    for n_, cf in cof.items():
        print(f"  coeff[{n_}] =", sp.factor(cf))
