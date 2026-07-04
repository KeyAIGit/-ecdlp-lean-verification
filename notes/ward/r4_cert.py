import sys, time, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules
from rwin import Rdef, Asym, Tsym, Psym, Qsym, AW, TW, PW, QW
t0=time.time()

Prng=list(range(-2,3)); Qrng=list(range(-2,3)); Awin=list(range(-3,4)); Twin=list(range(-3,4))
Pd={i:Psym[i] for i in Prng}; Qd={j:Qsym[j] for j in Qrng}
Ad={i:Asym[i] for i in Awin}; Td={j:Tsym[j] for j in Twin}
prules = pairing_rules(Pd,Qd,Ad,Td,0,0,Prng,Qrng)
arules = [(n_.replace('(t','(s'), r_, l_) for n_,r_,l_ in window_rules(Ad,Awin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules = window_rules(Td,Twin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
allgens = [Psym[i] for i in PW]+[Qsym[j] for j in QW]+[Asym[i] for i in AW]+[Tsym[j] for j in TW]+[B,c,d]

E = sp.expand( VE_expr(Pd,0)*VE_expr(Qd,0)
    - VO_expr(Ad,0,0)*VO_expr(Ad,-1,1)*VE_expr(Td,0)**2
    + VE_expr(Ad,0)**2*VO_expr(Td,0,0)*VO_expr(Td,-1,1) )
tail, cof_pair = reduce_full(E, prules, allgens)

st=(1,1,0); smt=(1,-1,0)
Ds=[]
for u in range(-2,3):
    for v in range(-2,3):
        if u==v: continue
        pol,ok = Rdef(st,smt,(0,0,u),(0,0,v))
        if not ok: continue
        red,_=reduce_full(sp.expand(pol),prules,allgens)
        for _ in range(3):
            rs=red.free_symbols
            if any(Psym[i] in rs for i in PW) or any(Qsym[j] in rs for j in QW):
                red,_=reduce_full(red,prules,allgens)
        rs=red.free_symbols
        pure=not(any(Psym[i] in rs for i in PW) or any(Qsym[j] in rs for j in QW))
        if red!=0 and pure: Ds.append((f"D({u},{v})",sp.expand(red)))

ATgens=[Asym[i] for i in AW]+[Tsym[j] for j in TW]+[B,c,d]
def wt(sym):
    for i in AW:
        if sym==Asym[i]: return (1,0,i,0,i*i-1-3*e(i))
    for j in TW:
        if sym==Tsym[j]: return (0,1,0,j,j*j-1-3*e(j))
    if sym==B: return (0,0,0,0,12)
    if sym==c: return (0,0,0,0,8)
    if sym==d: return (0,0,0,0,12)
    raise ValueError(sym)
def poly_wts(expr):
    p=sp.Poly(sp.expand(expr),*ATgens); ws=set()
    for mono,_ in p.terms():
        v=(0,0,0,0,0)
        for g,k in zip(ATgens,mono):
            if k:
                w=wt(g); v=tuple(a+k*b_ for a,b_ in zip(v,w))
        ws.add(v)
    return ws
wtT=poly_wts(tail)
print(f"tail weights {wtT} ({time.time()-t0:.0f}s); {len(Ds)} couplings",flush=True)
assert len(wtT)==1; W_tail=next(iter(wtT))

gens=[('A:'+n_,r_) for n_,r_,_ in arules]+[('T:'+n_,r_) for n_,r_,_ in trules]+[(n_,pol) for n_,pol in Ds]
Asyms=[Asym[i] for i in AW]; Tsyms=[Tsym[j] for j in TW]
cols=[]
for nm,g in gens:
    wg=poly_wts(g)
    if len(wg)!=1: 
        print("  skip non-homog",nm); continue
    wg=next(iter(wg))
    dA,dT,sI,sJ,K=tuple(a-b_ for a,b_ in zip(W_tail,wg))
    if dA<0 or dT<0: continue
    for am in itertools.combinations_with_replacement(AW,dA):
        if sum(am)!=sI: continue
        Ka=sum(i*i-1-3*e(i) for i in am)
        for tm in itertools.combinations_with_replacement(TW,dT):
            if sum(tm)!=sJ: continue
            Kt=sum(j*j-1-3*e(j) for j in tm)
            rem=K-Ka-Kt
            if rem<0: continue
            for gg in range(rem//12+1):
                for dd in range((rem-12*gg)//12+1):
                    r2=rem-12*gg-12*dd
                    if r2>=0 and r2%8==0:
                        mono=sp.prod([Asym[i] for i in am])*sp.prod([Tsym[j] for j in tm])*B**gg*d**dd*c**(r2//8)
                        cols.append((nm,mono,g))
print(f"unknowns {len(cols)} ({time.time()-t0:.0f}s)",flush=True)
gdict={nm:g for nm,g in gens}
mats=[]
for k_,(nm,mono,g) in enumerate(cols):
    img=sp.Poly(sp.expand(mono*g),*ATgens)
    mats.append({m_:co for m_,co in img.terms()})
    if (k_+1)%50==0: print(f"  imaged {k_+1}/{len(cols)} ({time.time()-t0:.0f}s)",flush=True)
tvec={m_:co for m_,co in sp.Poly(tail,*ATgens).terms()}
allm=set(tvec); [allm.update(pv) for pv in mats]
xs=sp.symbols(f'x0:{len(cols)}')
eqs=[sp.Eq(sum(sp.Rational(pv[m_])*xs[k_] for k_,pv in enumerate(mats) if m_ in pv), sp.Rational(tvec.get(m_,0))) for m_ in allm]
print(f"solving {len(eqs)}x{len(cols)} ({time.time()-t0:.0f}s)",flush=True)
sol=sp.linsolve(eqs,*xs)
if not sol:
    print("NO SOLUTION -> tail NOT in ideal with this coupling/window set",flush=True)
else:
    v0=list(sol)[0]; sub={x:0 for x in xs}
    vals=[a.subs(sub) if a.free_symbols else a for a in v0]
    combo=sum(vals[k_]*cols[k_][1]*cols[k_][2] for k_ in range(len(cols)))
    print(f"SOLUTION; verify tail-combo==0: {sp.expand(tail-combo)==0} ({time.time()-t0:.0f}s)",flush=True)
    # aggregate cofactor per generator
    from collections import defaultdict
    agg=defaultdict(lambda: sp.Integer(0))
    for k_ in range(len(cols)):
        if vals[k_]!=0: agg[cols[k_][0]]+=vals[k_]*cols[k_][1]
    for nm in sorted(agg):
        cff=sp.expand(agg[nm])
        isint=all(sp.Rational(x).q==1 for x in sp.Poly(cff,*ATgens).coeffs())
        print(f"   [{nm}] * ({sp.factor(cff)})  int={isint}",flush=True)
