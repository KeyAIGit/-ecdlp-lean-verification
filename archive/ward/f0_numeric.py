import sys, random
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, e

def run_checks(bval, cval, dval, N=26, MN=12):
    B = bval**4
    V = make_V(bval, cval, dval, 2*N+8)
    W = make_W(V, bval)
    ok = True
    # W-level EVEN / ODD as stated in the task
    for m in range(-N, N+1):
        lhs = W(2*m)*bval
        rhs = W(m-1)**2*W(m)*W(m+2) - W(m-2)*W(m)*W(m+1)**2
        if sp.expand(lhs - rhs) != 0: print("EVEN fail", m); ok=False
        lhs = W(2*m+1)
        rhs = W(m+2)*W(m)**3 - W(m-1)*W(m+1)**3
        if sp.expand(lhs - rhs) != 0: print("ODD fail", m); ok=False
    # W Somos-4 and Ward master (as stated)
    for k in range(-MN, MN+1):
        if sp.expand(W(k+2)*W(k-2) - (bval**2*W(k+1)*W(k-1) - cval*W(k)**2)) != 0:
            print("Somos fail", k); ok=False
    for m in range(-MN, MN+1):
        for n in range(-MN, MN+1):
            g = W(m+n)*W(m-n) - (W(m+1)*W(m-1)*W(n)**2 - W(n+1)*W(n-1)*W(m)**2)
            if sp.expand(g) != 0: print("STAR fail", m, n); ok=False
    # V-level Somos: VS(k): V(k+2)V(k-2) = B^e(k+1) V(k+1)V(k-1) - c V(k)^2
    for k in range(-MN, MN+1):
        g = V(k+2)*V(k-2) - (B**e(k+1)*V(k+1)*V(k-1) - cval*V(k)**2)
        if sp.expand(g) != 0: print("VS fail", k); ok=False
    # V-level Star3: V(k+3)V(k-3) = c^2 V(k+1)V(k-1) - B^e(k) d V(k)^2
    for k in range(-MN, MN+1):
        g = V(k+3)*V(k-3) - (cval**2*V(k+1)*V(k-1) - B**e(k)*dval*V(k)**2)
        if sp.expand(g) != 0: print("VSTAR3 fail", k); ok=False
    # V-level master with parity decorations:
    # V(m+n)V(m-n) = B^{e(m+1)e(n)} V(m+1)V(m-1)V(n)^2 - B^{e(m)e(n+1)} V(n+1)V(n-1)V(m)^2
    for m in range(-MN, MN+1):
        for n in range(-MN, MN+1):
            a = e(m+1)*e(n); bb = e(m)*e(n+1)
            g = V(m+n)*V(m-n) - (B**a*V(m+1)*V(m-1)*V(n)**2 - B**bb*V(n+1)*V(n-1)*V(m)**2)
            if sp.expand(g) != 0: print("VSTAR fail", m, n); ok=False
    return ok

random.seed(7)
allok = True
for (bv, cv, dv) in [(2,3,5), (-3,7,11), (random.randrange(2,50), random.randrange(2,50), random.randrange(2,50))]:
    r = run_checks(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv))
    print("numeric b,c,d =", (bv,cv,dv), "->", r)
    allok = allok and r
# small fully symbolic check
b, c, d = sp.symbols('b c d')
r = run_checks(b, c, d, N=8, MN=6)
print("symbolic b,c,d ->", r)
print("ALL OK:", allok and r)
