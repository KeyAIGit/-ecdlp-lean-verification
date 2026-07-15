import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from sympy.polys.orderings import grevlex
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

import importlib
c15 = importlib.import_module  # avoid re-running c15
# inline build_case copy
def build_case(which):
    if which == 'even':
        Prng = list(range(-2,3)); Qrng = list(range(-2,3))
        Awin = list(range(-3,4)); Twin = list(range(-3,4))
    else:
        Prng = list(range(-1,3)); Qrng = list(range(-2,2))
        Awin = list(range(-3,4)); Twin = list(range(-2,4))
    P = mk('P',Prng); Q = mk('Q',Qrng); A = mk('A',Awin); T = mk('T',Twin)
    gens = [P[a] for a in Prng]+[Q[b_] for b_ in Qrng]+[A[i] for i in Awin]+[T[j] for j in Twin]+[B,c,d]
    prules = pairing_rules(P,Q,A,T,0,0,Prng,Qrng)
    def dbl_A(x): return VE_expr(A,x//2) if x%2==0 else VO_expr(A,(x-1)//2,((x-1)//2)%2)
    def dbl_T(y): return VE_expr(T,y//2) if y%2==0 else VO_expr(T,(y-1)//2,((y-1)//2)%2)
    coup = []
    for i in range(-2,3):
        for j in range(-2,3):
            if (i-j)%2==0 and all(k in Prng for k in [i-1,i,i+1]) and all(k in Qrng for k in [j-1,j,j+1]):
                al=e(i+1)*e(j); be=e(i)*e(j+1)
                pq = B**al*P[i+1]*P[i-1]*Q[j]**2 - B**be*Q[j+1]*Q[j-1]*P[i]**2
                x=i+j; y=i-j; nm=f"X1({i},{j})"
            elif (i-j)%2==1 and all(k in Prng for k in [i-1,i,i+1,i+2]) and all(k in Qrng for k in [j-1,j,j+1,j+2]):
                pq = Q[j+1]*Q[j]*P[i+2]*P[i-1] - Q[j+2]*Q[j-1]*P[i+1]*P[i]
                x=i+j+1; y=i-j; nm=f"X2({i},{j})"
            else: continue
            rempq, _ = reduce_full(sp.expand(pq), prules, gens)
            if set(rempq.free_symbols) & set(list(P.values())+list(Q.values())): continue
            coup.append((nm, sp.expand(dbl_A(x)*dbl_T(y) - rempq)))
    arules = [(n_.replace('(t','(s'), r_, l_) for n_,r_,l_ in window_rules(A,Awin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
    trules = window_rules(T,Twin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    if which == 'even':
        E = ( VE_expr(P,0)*VE_expr(Q,0)
            - VO_expr(A,0,0)*VO_expr(A,-1,1)*VE_expr(T,0)**2
            + VO_expr(T,0,0)*VO_expr(T,-1,1)*VE_expr(A,0)**2 )
    else:
        E = ( VO_expr(P,0,0)*VO_expr(Q,-1,1)
            - VO_expr(A,0,0)*VO_expr(A,-1,1)*VO_expr(T,0,0)**2
            + B*VE_expr(T,1)*VE_expr(T,0)*VE_expr(A,0)**2 )
    tail, _ = reduce_full(sp.expand(E), prules+arules+trules, gens)
    return P,Q,A,T,Awin,Twin,coup,arules,trules,tail,gens

def run(which):
    t0 = time.time()
    P,Q,A,T,Awin,Twin,coup,arules,trules,tail,gens = build_case(which)
    tgens = [A[i] for i in Awin] + [T[j] for j in Twin] + [B,c,d]
    # monic-scaled coupling rewrite rules by grevlex lead
    crules = []
    for nm, C in coup:
        p = sp.Poly(C, *tgens)
        if p.is_zero: continue
        lm, lc = max(p.terms(), key=lambda t_: grevlex(t_[0]))
        mono = sp.prod([g**k for g, k in zip(tgens, lm)])
        crules.append((nm, sp.expand(C/lc), mono))
    GA = sp.groebner([r_ for _,r_,_ in arules], *tgens, order='grevlex')
    GT = sp.groebner([r_ for _,r_,_ in trules], *tgens, order='grevlex')
    def NF(expr):
        _, r1 = GA.reduce(sp.expand(expr))
        if r1 == 0: return sp.Integer(0)
        _, r2 = GT.reduce(r1)
        return sp.expand(r2)
    rem = sp.expand(tail)
    print(f"[{which}] tail {len(sp.Poly(rem,*tgens).terms())} terms, {len(crules)} coupling rules", flush=True)
    for it in range(30):
        rem2, cf = reduce_full(rem, crules, tgens)
        rem3 = NF(rem2)
        nt = 0 if rem3 == 0 else len(sp.Poly(rem3, *tgens).terms())
        print(f"  iter {it}: after couplings+NF -> {nt} terms ({time.time()-t0:.0f}s)", flush=True)
        if rem3 == 0:
            print(f"  MEMBERSHIP ESTABLISHED for {which} outer step", flush=True)
            return True
        if sp.expand(rem3 - rem) == 0:
            print(f"  stalled for {which}", flush=True)
            return False
        rem = rem3
    return False

r1 = run('even')
r2 = run('odd')
print("RESULT even:", r1, "odd:", r2, flush=True)
