import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, e

# V-level R: each term T_i = product of 4 V's times b^(2*g_i), g_i in {sum of two e's}.
# term1: e(p+q)+e(r+s); term2: e(p+r)+e(q+s); term3: e(p+s)+e(q+r).
def g1(p,q,r,s): return e(p+q)+e(r+s)
def g2(p,q,r,s): return e(p+r)+e(q+s)
def g3(p,q,r,s): return e(p+s)+e(q+r)
# Claim: g1,g2,g3 differ by an even amount? Check min and residual. Actually parities:
# The three "matchings" of {p,q,r,s} pairs. Their e-sums.
def show(p,q,r,s):
    return (g1(p,q,r,s), g2(p,q,r,s), g3(p,q,r,s))

# Determine the common b-power to factor. Since W = V b^e, term_i has b^(2 g_i).
# Factor b^(2*gmin). Then V-level:  sum_i (-1)^? B^(g_i-gmin) * (V-product_i) = 0, B=b^2? No: b^(2g)= (b^2)^g.
# But our EDS uses B=b^4. Let's just define Bh=b^2 and verify numerically.
b,c,d = sp.symbols('b c d')
def Vprod(V,term):
    p,q,r,s = term
    return None

def VR(V, p,q,r,s, bh):
    # bh = b^2 symbol/value
    gm = min(g1(p,q,r,s), g2(p,q,r,s), g3(p,q,r,s))
    t1 = bh**(g1(p,q,r,s)-gm) * V(p+q)*V(p-q)*V(r+s)*V(r-s)
    t2 = bh**(g2(p,q,r,s)-gm) * V(p+r)*V(p-r)*V(q+s)*V(q-s)
    t3 = bh**(g3(p,q,r,s)-gm) * V(p+s)*V(p-s)*V(q+r)*V(q-r)
    return t1 - t2 + t3

ok = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 80)
    bh = bv**2
    for p in range(-4,5):
        for q in range(-4,5):
            for r in range(-3,4):
                for s in range(-3,4):
                    if sp.expand(VR(V,p,q,r,s,bh)) != 0: ok=False; print("VR fail",p,q,r,s)
print("V-level R (with bh=b^2, factor b^(2 gmin)) == 0 :", ok, flush=True)

# distribution of (g1,g2,g3) patterns => the b-decoration is fully determined by parities of p,q,r,s.
pats = {}
for p in range(0,4):
    for q in range(0,4):
        for r in range(0,4):
            for s in range(0,4):
                key = (p%2,q%2,r%2,s%2)
                gm = min(g1(p,q,r,s),g2(p,q,r,s),g3(p,q,r,s))
                pats[key] = (g1(p,q,r,s)-gm, g2(p,q,r,s)-gm, g3(p,q,r,s)-gm)
print("b^2-exponent pattern (t1,t2,t3) by (p,q,r,s) parities:", flush=True)
for k in sorted(pats): print("  ", k, "->", pats[k], flush=True)

# star3 as a normalized R-instance: structurally, star3 defect should be b^? * VR(...) for some args.
# Numerically identify: b*W(m+n+1)W(m-n) - [W(n+1)W(n)W(m+2)W(m-1) - W(n+2)W(n-1)W(m+1)W(m)]
# Compare to R(m+1, n+1, m, n) style. Try to match to an R with p-q etc producing m+n+1 and m-n:
# want an R term W(p+q)W(p-q) with {p+q,p-q} = {m+n+1, m-n}? p+q=m+n+1... but m-n and m+n+1 differ by 2n+1 (odd) => p,q half-integers. So star3 is a *b-normalized* R, i.e. R at half-integer offset. 
# Known: star3 = R(m+1, n+ ... ). Let's brute force over R(a,b2,cc,dd) with a,b2,cc,dd in terms of m,n small combos to find identical W-support to star3.
bv,cv,dv = 2,3,5
V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 120); W = make_W(V, sp.Integer(bv))
def Rw(p,q,r,s): return ( W(p+q)*W(p-q)*W(r+s)*W(r-s) - W(p+r)*W(p-r)*W(q+s)*W(q-s) + W(p+s)*W(p-s)*W(q+r)*W(q-r))
# star3 rewritten as R(m+1,m,n+1,n): check the three products
for (P,Q,Rr,S,label) in [
    (sp.Symbol('m')+1, sp.Symbol('m'), sp.Symbol('n')+1, sp.Symbol('n'), "R(m+1,m,n+1,n)"),
]:
    pass
# numeric structural test: is  R(m+1,m,n+1,n) == b-power * star3-family (all identically 0)? 
# Instead verify the *pairing identity* directly: R(m+1,m,n+1,n) expands to terms; show it equals
#   W(2m+1)W(1)W(2n+1)W(1) - W(m+n+1)W(m-n)W(m+n+1)W(m-n)?? let's just print R(m+1,m,n+1,n) support:
mm,nn=5,3
val = Rw(mm+1,mm,nn+1,nn)
print("R(m+1,m,n+1,n) value (should be 0):", val, flush=True)
# Its three terms:
def terms(p,q,r,s):
    return [W(p+q)*W(p-q)*W(r+s)*W(r-s), -W(p+r)*W(p-r)*W(q+s)*W(q-s), W(p+s)*W(p-s)*W(q+r)*W(q-r)]
p,q,r,s = mm+1,mm,nn+1,nn
print("  arg pairs:", [(p+q,p-q),(r+s,r-s)],[(p+r,p-r),(q+s,q-s)],[(p+s,p-s),(q+r,q-r)], flush=True)
