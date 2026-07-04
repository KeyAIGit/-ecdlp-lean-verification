import sys, time, itertools
from fractions import Fraction
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

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

    def wt(sym):
        for i in Awin:
            if sym == A[i]: return (1,0,i,0,i*i-1-3*e(i))
        for j in Twin:
            if sym == T[j]: return (0,1,0,j,j*j-1-3*e(j))
        if sym == B: return (0,0,0,0,12)
        if sym == c: return (0,0,0,0,8)
        if sym == d: return (0,0,0,0,12)
        raise ValueError(sym)
    def poly_wt(expr):
        p = sp.Poly(sp.expand(expr), *tgens)
        ws = set()
        for mono, _ in p.terms():
            v = (0,0,0,0,0)
            for g, k in zip(tgens, mono):
                if k:
                    w = wt(g)
                    v = tuple(a+k*b_ for a, b_ in zip(v, w))
            ws.add(v)
        return ws

    print(f"[{which}] tail terms {len(sp.Poly(tail,*tgens).terms())}, couplings {len(coup)} ({time.time()-t0:.0f}s)", flush=True)
    wt_tail = poly_wt(tail)
    assert len(wt_tail) == 1, ("tail not homogeneous", wt_tail)
    wt_tail = next(iter(wt_tail))
    print(f"  tail weight: {wt_tail}", flush=True)
    GA = sp.groebner([r_ for _,r_,_ in arules], *tgens, order='grevlex')
    GT = sp.groebner([r_ for _,r_,_ in trules], *tgens, order='grevlex')
    def NF(expr):
        _, r1 = GA.reduce(sp.expand(expr))
        if r1 == 0: return sp.Integer(0)
        _, r2 = GT.reduce(r1)
        return sp.expand(r2)

    Asyms = [A[i] for i in Awin]; Tsyms = [T[j] for j in Twin]
    cols = []
    cdict = dict(coup)
    for nm, C in coup:
        wtC = poly_wt(C)
        if len(wtC) != 1:
            print(f"  {nm} NOT homogeneous, skipped", flush=True); continue
        wtC = next(iter(wtC))
        delta = tuple(a-b_ for a,b_ in zip(wt_tail, wtC))
        dA, dT, sI, sJ, K = delta
        if dA < 0 or dT < 0: continue
        cnt = 0
        for am in itertools.combinations_with_replacement(Awin, dA):
            if sum(am) != sI: continue
            Ka = sum(i*i-1-3*e(i) for i in am)
            for tm in itertools.combinations_with_replacement(Twin, dT):
                if sum(tm) != sJ: continue
                Kt = sum(j*j-1-3*e(j) for j in tm)
                rem = K - Ka - Kt
                if rem < 0: continue
                for gg in range(rem//12+1):
                    for dd in range((rem-12*gg)//12+1):
                        r2 = rem - 12*gg - 12*dd
                        if r2 >= 0 and r2 % 8 == 0:
                            mono = sp.prod([A[i] for i in am])*sp.prod([T[j] for j in tm])*B**gg*d**dd*c**(r2//8)
                            cols.append((nm, mono))
                            cnt += 1
        print(f"  {nm}: {cnt} cofactor monomials", flush=True)
    print(f"  total unknowns: {len(cols)} ({time.time()-t0:.0f}s)", flush=True)

    target = NF(tail)
    mats = []
    for k_, (nm, mono) in enumerate(cols):
        img = NF(mono*cdict[nm])
        mats.append({} if img == 0 else {m_: co for m_, co in sp.Poly(img, *tgens).terms()})
        if (k_+1) % 25 == 0: print(f"    imaged {k_+1}/{len(cols)} ({time.time()-t0:.0f}s)", flush=True)
    tvec = {m_: co for m_, co in sp.Poly(target, *tgens).terms()}

    allmonos = set(tvec)
    for pv in mats: allmonos.update(pv)
    allmonos = sorted(allmonos)
    n = len(cols)
    xs = sp.symbols(f'x0:{n}')
    eqs = []
    for m_ in allmonos:
        lhs = sum(sp.Rational(pv[m_])*xs[k_] for k_, pv in enumerate(mats) if m_ in pv)
        eqs.append(sp.Eq(lhs, sp.Rational(tvec.get(m_, 0))))
    print(f"  system: {len(eqs)} eqs x {n} unknowns ({time.time()-t0:.0f}s)", flush=True)
    solset = sp.linsolve(eqs, *xs)
    if not solset:
        print("  NO SOLUTION with current coupling set", flush=True)
        return None
    solv = list(solset)[0]
    subst = {x_: 0 for x_ in xs}
    vals = [v_.subs(subst) if v_.free_symbols else v_ for v_ in solv]
    combo = sum(vals[k_]*cols[k_][1]*cdict[cols[k_][0]] for k_ in range(n))
    check = NF(sp.expand(tail - combo))
    print(f"  SOLUTION FOUND; verify NF(tail - sum) == 0: {check == 0} ({time.time()-t0:.0f}s)", flush=True)
    for k_ in range(n):
        if vals[k_] != 0:
            print(f"   [{cols[k_][0]}] cofactor += ({vals[k_]}) * {cols[k_][1]}", flush=True)
    return True

run('even')
print("\n===============\n", flush=True)
run('odd')
print("\nDONE", flush=True)
