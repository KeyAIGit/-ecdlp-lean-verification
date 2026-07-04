import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from sympy.polys.orderings import grevlex
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules
from tracked_gb2 import TrackedGB

def unit_lead(expr, gens):
    p = sp.Poly(sp.expand(expr), *gens)
    Bi = gens.index(B); ci = gens.index(c); di = gens.index(d)
    cands = [(m_, co) for m_, co in p.terms() if co in (1, -1)]
    if not cands: return None, None
    m_, co = max(cands, key=lambda t: grevlex(t[0]))
    mono = sp.prod([g**k for g, k in zip(gens, m_)])
    return mono, co

def outer_case(tag, which):
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
            rempq, cofpq = reduce_full(sp.expand(pq), prules, gens)
            if set(rempq.free_symbols) & set(list(P.values())+list(Q.values())): continue
            Cij = sp.expand(dbl_A(x)*dbl_T(y) - rempq)
            ld, co = unit_lead(Cij, gens)
            if ld is None: 
                print("   no unit lead for", nm); continue
            coup.append((nm, Cij*co if co == 1 else -Cij, ld))  # ensure +1 coeff on lead
    # fix orientation: rel must contain lead with coeff +1
    coup = [(nm, rel if sp.Poly(rel, *gens).coeff_monomial(ld)==1 else -rel, ld) for nm, rel, ld in coup]
    print(f"{tag}: {len(coup)} couplings usable", flush=True)
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
    allrules = prules + coup + arules + trules
    names=[n_ for n_,_,_ in allrules]; exprs=[r_ for _,r_,_ in allrules]
    total = {}
    rem = sp.expand(E)
    gbA = TrackedGB([r_ for _,r_,_ in arules], gens)
    gbT = TrackedGB([r_ for _,r_,_ in trules], gens)
    print(f"   per-window GBs built ({time.time()-t0:.0f}s)", flush=True)
    for it in range(25):
        rem, cf = reduce_full(rem, allrules, gens)
        for k_,v_ in cf.items(): total[k_] = sp.expand(total.get(k_,0)+v_)
        if rem == 0: break
        for gbX, rl in [(gbA, arules), (gbT, trules)]:
            if rem == 0: break
            okX, cofX, rem = gbX.express(rem)
            rn = [n_ for n_,_,_ in rl]
            for k_, cf_ in cofX.items():
                total[rn[k_]] = sp.expand(total.get(rn[k_],0) + cf_)
            rem = sp.expand(rem) if rem != 0 else rem
        nt = 0 if rem == 0 else len(sp.Poly(rem,*gens).terms())
        print(f"   iter {it}: rem terms {nt} ({time.time()-t0:.0f}s)", flush=True)
        if rem == 0: break
    print(f"   FINAL rem == 0: {rem == 0}", flush=True)
    if rem == 0:
        nm2expr = {}
        for n_, r_, _ in allrules: nm2expr[n_] = r_
        s = E - sum(cf*nm2expr[n_] for n_, cf in total.items())
        print("   exact recheck:", sp.expand(s) == 0, flush=True)
        for n_, cf in total.items():
            if cf != 0:
                isint = all(sp.Rational(x).q==1 for x in sp.Poly(cf,*gens).coeffs())
                print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}", flush=True)
    else:
        print("   residue:", sp.factor(rem), flush=True)

outer_case("OUTER-EVEN (I)(2s,2t) s,t even", 'even')
outer_case("OUTER-ODD (I)(2s,2t+1) s,t even", 'odd')
print("\nDONE", flush=True)
