import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

# rebuild the c4 greedy tail, then numerically check it vanishes on real double windows
Prng = list(range(-2,3)); Qrng = list(range(-2,3))
Awin = list(range(-3,4)); Twin = list(range(-3,4))
P = mk('P', Prng); Q = mk('Q', Qrng); A = mk('A', Awin); T = mk('T', Twin)
E = ( VE_expr(P,0)*VE_expr(Q,0)
    - VO_expr(A,0,0)*VO_expr(A,-1,1)*VE_expr(T,0)**2
    + VO_expr(T,0,0)*VO_expr(T,-1,1)*VE_expr(A,0)**2 )
prules = pairing_rules(P, Q, A, T, 0, 0, Prng, Qrng)
arules = [(n_.replace('(t','(s'), r_, l_) for n_, r_, l_ in window_rules(A, Awin, 0, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules = window_rules(T, Twin, 0, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
gens = [P[a] for a in Prng]+[Q[b_] for b_ in Qrng]+[A[i] for i in Awin]+[T[j] for j in Twin]+[B,c,d]
tail, cof1 = reduce_full(sp.expand(E), prules+arules+trules, gens)
print("tail terms:", len(sp.Poly(tail,*gens).terms()))
sp.pickle = None
with open('c4_tail.txt','w') as f: f.write(sp.srepr(tail))

ok = True
for (bv,cv,dv) in [(2,3,5),(3,7,2)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 80)
    for (s_, t_) in [(8,4),(10,6),(12,8)]:   # s,t even
        subs = {B: bv**4, c: cv, d: dv}
        for i in Awin: subs[A[i]] = V(s_+i)
        for j in Twin: subs[T[j]] = V(t_+j)
        val = tail.subs(subs)
        if sp.simplify(val) != 0:
            ok = False; print("tail nonzero at", (bv,cv,dv,s_,t_), val)
print("c4 tail vanishes on real double windows:", ok)
