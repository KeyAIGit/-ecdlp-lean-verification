import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, e

def RW(W,p,q,r,s):
    return ( W(p+q)*W(p-q)*W(r+s)*W(r-s)
           - W(p+r)*W(p-r)*W(q+s)*W(q-s)
           + W(p+s)*W(p-s)*W(q+r)*W(q-r) )

# 1) numeric: R == 0 for all integer p,q,r,s in a box; and specializations
ok_R = True; ok_star1 = True; ok_star3 = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 80)
    W = make_W(V, sp.Integer(bv))
    for p in range(-4,5):
        for q in range(-4,5):
            for r in range(-3,4):
                for s in range(-3,4):
                    if sp.expand(RW(W,p,q,r,s)) != 0: ok_R=False
    # (star1) = R(m,n,1,0)
    for m in range(-9,10):
        for n in range(-9,10):
            lhs = W(m+n)*W(m-n) - (W(m+1)*W(m-1)*W(n)**2 - W(n+1)*W(n-1)*W(m)**2)
            if sp.expand(lhs - RW(W,m,n,1,0)) != 0: ok_star1=False
    # (star3): b*W(m+n+1)*W(m-n) - [W(n+1)W(n)W(m+2)W(m-1) - W(n+2)W(n-1)W(m+1)W(m)]
    # claim = normalized R-instance R(m+1, m, n+1, n)? test a few candidate instances
    for m in range(-6,7):
        for n in range(-6,7):
            star3 = ( bv*W(m+n+1)*W(m-n)
                    - (W(n+1)*W(n)*W(m+2)*W(m-1) - W(n+2)*W(n-1)*W(m+1)*W(m)) )
            if star3 != 0: ok_star3=False
    print(f"  b,c,d={ (bv,cv,dv)}: R==0 {ok_R}, star1=R(m,n,1,0) {ok_star1}, star3 identity {ok_star3}", flush=True)

# Which R-instance equals star3? Search over small templates for a match to star3's *support*.
bv,cv,dv = 2,3,5
V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 80); W = make_W(V, sp.Integer(bv))
# star3 involves indices m+n+1, m-n, n+1,n,n+2,n-1, m+2,m-1,m+1,m. Try R(m+1,n, m, n+1)? etc.
import itertools
found=[]
for (P,Q,Rr,S) in itertools.permutations([sp.Symbol('A'),sp.Symbol('B'),sp.Symbol('C'),sp.Symbol('D')]):
    pass
# direct: test R(m+1,n+1,m,n) etc. numerically as candidates b*star3-shaped
cands = {
 'R(m+1,n,1,0)@shift': lambda m,n: Rw_shift(W,m,n),
}
def Rw(p,q,r,s): return ( W(p+q)*W(p-q)*W(r+s)*W(r-s) - W(p+r)*W(p-r)*W(q+s)*W(q-s) + W(p+s)*W(p-s)*W(q+r)*W(q-r))
# Try to express star3 as an R with two args differing by 1 from m and n:
tests = {
 'R(m+1,n+1,1,0)': lambda m,n: Rw(m+1,n+1,1,0),
 'R(m+1,n,1,0)':   lambda m,n: Rw(m+1,n,1,0),
 'R(m,n+1,1,0)':   lambda m,n: Rw(m,n+1,1,0),
}
for nm,f in tests.items():
    diffs=set()
    for m in range(-4,5):
        for n in range(-4,5):
            s3 = ( bv*W(m+n+1)*W(m-n) - (W(n+1)*W(n)*W(m+2)*W(m-1) - W(n+2)*W(n-1)*W(m+1)*W(m)) )
            # s3 is identically 0, so can't match by value. Instead compare the **un-reduced** poly structure later.
    print(nm, "checked (star3 is identically 0; structural match handled at V-level in r1)")
