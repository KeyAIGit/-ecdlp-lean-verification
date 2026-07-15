import sys, time, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from sympy.polys.orderings import grevlex
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

def run(which):
    t0 = time.time()
    if which == 'even':
        Prng = list(range(-2,3)); Qrng = list(range(-2,3))
        Awin = list(range(-3,4)); Twin = list(range(-3,4))
    else:
        Prng = list(range(-1,3)); Qrng = list(range(-2,2))
        Awin = list(range(-3,4)); Twin = list(range(-2,4))
    P = mk('P',Prng); Q = mk('Q',Qrng); A = mk('A',Awin); T = mk('T',Twin)
    gens = [P[a] for a in Prng]+[Q[b_] for b_ in Qrng]+[A[i] for i in Awin]+[T[j] for j in Twin]+[B,c,d]
    prules = pairing_rules(P,Q,A,T,0,0,Prng,Qrng)
    fmap = {}
    for n_, r_, l_ in prules:
        # r_ = P_a Q_b - f  => f = lead - rel
        fmap[l_] = sp.expand(l_ - r_)
    def f(a,b_): return fmap[P[a]*Q[b_]]
    if which == 'even':
        E = ( VE_expr(P,0)*VE_expr(Q,0)
            - VO_expr(A,0,0)*VO_expr(A,-1,1)*VE_expr(T,0)**2
            + VO_expr(T,0,0)*VO_expr(T,-1,1)*VE_expr(A,0)**2 )
    else:
        E = ( VO_expr(P,0,0)*VO_expr(Q,-1,1)
            - VO_expr(A,0,0)*VO_expr(A,-1,1)*VO_expr(T,0,0)**2
            + B*VE_expr(T,1)*VE_expr(T,0)*VE_expr(A,0)**2 )
    arules = [(n_.replace('(t','(s'), r_, l_) for n_,r_,l_ in window_rules(A,Awin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
    trules = window_rules(T,Twin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    tail, _ = reduce_full(sp.expand(E), prules+arules+trules, gens)
    tgens = [A[i] for i in Awin] + [T[j] for j in Twin] + [B,c,d]
    # exchange generators
    exch = []
    for a, cc_ in itertools.combinations(Prng, 2):
        for b_, dd_ in itertools.combinations(Qrng, 2):
            X = sp.expand(f(a,b_)*f(cc_,dd_) - f(a,dd_)*f(cc_,b_))
            if X != 0:
                exch.append((f"EXCH[{a},{cc_}|{b_},{dd_}]", X))
    print(f"[{which}] tail {len(sp.Poly(tail,*tgens).terms())} terms; {len(exch)} nonzero exchanges ({time.time()-t0:.0f}s)", flush=True)
    # monic grevlex rules from exchanges
    xrules = []
    for nm, X in exch:
        p = sp.Poly(X, *tgens)
        lm, lc = max(p.terms(), key=lambda t_: grevlex(t_[0]))
        mono = sp.prod([g**k for g, k in zip(tgens, lm)])
        xrules.append((nm, sp.expand(X/lc), mono))
    GA = sp.groebner([r_ for _,r_,_ in arules], *tgens, order='grevlex')
    GT = sp.groebner([r_ for _,r_,_ in trules], *tgens, order='grevlex')
    def NF(expr):
        _, r1 = GA.reduce(sp.expand(expr))
        if r1 == 0: return sp.Integer(0)
        _, r2 = GT.reduce(r1)
        return sp.expand(r2)
    rem = sp.expand(tail)
    prev = None
    for it in range(40):
        rem2, cf = reduce_full(rem, xrules, tgens)
        rem3 = NF(rem2)
        nt = 0 if rem3 == 0 else len(sp.Poly(rem3, *tgens).terms())
        print(f"  iter {it}: -> {nt} terms ({time.time()-t0:.0f}s)", flush=True)
        if rem3 == 0:
            print(f"  MEMBERSHIP ESTABLISHED for {which} via exchanges", flush=True)
            return True
        if prev is not None and sp.expand(rem3 - prev) == 0:
            print(f"  stalled for {which}; residue terms {nt}", flush=True)
            return False
        prev = rem3
        rem = rem3
    return False

r1 = run('even')
r2 = run('odd')
print("RESULT even:", r1, "odd:", r2, flush=True)
