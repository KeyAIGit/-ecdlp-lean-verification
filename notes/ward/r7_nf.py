import sys, time, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import pairing_rules
from rwin import Rdef, Asym, Tsym, Psym, Qsym
t0=time.time()
Awin=Twin=Pwin=Qwin=list(range(-3,4))
Ad={i:Asym[i] for i in Awin}; Td={j:Tsym[j] for j in Twin}
Pd={i:Psym[i] for i in Pwin}; Qd={j:Qsym[j] for j in Qwin}
Avars=[Asym[i] for i in Awin]; Tvars=[Tsym[j] for j in Twin]
Pvars=[Psym[i] for i in Pwin]; Qvars=[Qsym[j] for j in Qwin]
allgens=Avars+Tvars+Pvars+Qvars+[B,c,d]
def gb_of(win,dic):
    rls=window_rules(dic,win,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
    return sp.groebner([r_ for _,r_,_ in rls],*allgens,order='grevlex')
GA=gb_of(Awin,Ad);GT=gb_of(Twin,Td);GP=gb_of(Pwin,Pd);GQ=gb_of(Qwin,Qd)
print(f"GBs built ({time.time()-t0:.0f}s)",flush=True)
def NF(x):
    x=sp.expand(x)
    for _ in range(5):
        prev=x
        for G in (GA,GT,GP,GQ):
            if x==0: return sp.Integer(0)
            _,x=G.reduce(x)
        if sp.expand(x-prev)==0: break
    return sp.expand(x)
E=sp.expand( VE_expr(Pd,0)*VE_expr(Qd,0) - VO_expr(Ad,0,0)*VO_expr(Ad,-1,1)*VE_expr(Td,0)**2
    + VE_expr(Ad,0)**2*VO_expr(Td,0,0)*VO_expr(Td,-1,1) )
Enf=NF(E)
print(f"NF(E) terms {len(sp.Poly(Enf,*allgens).terms())} ({time.time()-t0:.0f}s)",flush=True)

# TRUE grading as form in (s2,st,t2,s,t,K)
def wt(sym):
    for i in Awin:
        if sym==Asym[i]: return (1,0,0,2*i,0, i*i-1-3*e(i))
    for j in Twin:
        if sym==Tsym[j]: return (0,0,1,0,2*j, j*j-1-3*e(j))
    for i in Pwin:
        if sym==Psym[i]: return (1,2,1,2*i,2*i, i*i-1-3*e(i))
    for j in Qwin:
        if sym==Qsym[j]: return (1,-2,1,2*j,-2*j, j*j-1-3*e(j))
    if sym==B: return (0,0,0,0,0,12)
    if sym==c: return (0,0,0,0,0,8)
    if sym==d: return (0,0,0,0,0,12)
    raise ValueError(sym)
def pw(expr):
    p=sp.Poly(sp.expand(expr),*allgens); ws=set()
    for mono,_ in p.terms():
        v=(0,)*6
        for g,k in zip(allgens,mono):
            if k: w=wt(g); v=tuple(a+k*b_ for a,b_ in zip(v,w))
        ws.add(v)
    return ws
WE=pw(Enf); print("NF(E) weight(s):",WE,flush=True); assert len(WE)==1; WT=next(iter(WE))

Prng=list(range(-2,3)); Qrng=list(range(-2,3))
prules=pairing_rules({i:Psym[i] for i in Prng},{j:Qsym[j] for j in Qrng},Ad,Td,0,0,Prng,Qrng)
gens=[('pair:'+n_,r_) for n_,r_,_ in prules]
st=(1,1,0); smt=(1,-1,0); sform=(1,0,0); tform=(0,1,0)
for lbl,(P1,P2) in {'Rst(':(sform,tform),'Rp(':(st,smt)}.items():
    for u in range(-2,3):
        for v in range(-2,3):
            if u==v: continue
            try: pol,ok=Rdef(P1,P2,(0,0,u),(0,0,v))
            except Exception: continue
            if ok and pol!=0: gens.append((f"{lbl}{u},{v})",sp.expand(pol)))
print(f"{len(gens)} generators ({time.time()-t0:.0f}s)",flush=True)

def msets(win,n): return itertools.combinations_with_replacement(win,n)
cols=[]
for nm,g in gens:
    wg=pw(g)
    if len(wg)!=1: continue
    wg=next(iter(wg))
    cs2,cst,ct2,cs,ct,K=tuple(a-b_ for a,b_ in zip(WT,wg))  # cofactor target form
    if cst%2: continue
    # nA+nP+nQ=cs2 ; nT+nP+nQ=ct2 ; nP-nQ=cst/2
    dpq=cst//2
    for nP in range(0,cs2+1):
        nQ=nP-dpq
        if nQ<0: continue
        nA=cs2-nP-nQ; nT=ct2-nP-nQ
        if nA<0 or nT<0: continue
        if nA+nT+nP+nQ>6: continue  # degree cap for tractability
        for am in msets(Awin,nA):
         for pm in msets(Pwin,nP):
          for qm in msets(Qwin,nQ):
           for tm in msets(Twin,nT):
            if sum(2*i for i in am)+sum(2*i for i in pm)+sum(2*j for j in qm)!=cs: continue
            if sum(2*j for j in tm)+sum(2*i for i in pm)+sum(-2*j for j in qm)!=ct: continue
            Krem=K-sum(x*x-1-3*e(x) for x in am+tm+pm+qm)
            if Krem<0: continue
            for gg in range(Krem//12+1):
             for dd in range((Krem-12*gg)//12+1):
              r2=Krem-12*gg-12*dd
              if r2>=0 and r2%8==0:
               mono=sp.prod([Asym[i] for i in am])*sp.prod([Tsym[j] for j in tm])*sp.prod([Psym[i] for i in pm])*sp.prod([Qsym[j] for j in qm])*B**gg*d**dd*c**(r2//8)
               cols.append((nm,mono,g))
print(f"unknowns {len(cols)} ({time.time()-t0:.0f}s)",flush=True)
mats=[]
for k_,(nm,mono,g) in enumerate(cols):
    img=NF(mono*g)
    mats.append({} if img==0 else {m_:co for m_,co in sp.Poly(img,*allgens).terms()})
    if (k_+1)%100==0: print(f"  imaged {k_+1}/{len(cols)} ({time.time()-t0:.0f}s)",flush=True)
tvec={m_:co for m_,co in sp.Poly(Enf,*allgens).terms()}
allm=set(tvec); [allm.update(pv) for pv in mats]
xs=sp.symbols(f'x0:{len(cols)}')
eqs=[sp.Eq(sum(sp.Rational(pv[m_])*xs[k_] for k_,pv in enumerate(mats) if m_ in pv),sp.Rational(tvec.get(m_,0))) for m_ in allm]
print(f"solving {len(eqs)}x{len(cols)} ({time.time()-t0:.0f}s)",flush=True)
sol=sp.linsolve(eqs,*xs)
if not sol:
    print("NO SOLUTION",flush=True)
else:
    v0=list(sol)[0]; sub={x:0 for x in xs}
    vals=[a.subs(sub) if a.free_symbols else a for a in v0]
    combo=sum(vals[k_]*cols[k_][1]*cols[k_][2] for k_ in range(len(cols)))
    print("SOLUTION; NF(E-combo)==0:", NF(E-combo)==0,flush=True)
    import collections
    agg=collections.defaultdict(lambda: sp.Integer(0))
    for k_ in range(len(cols)):
        if vals[k_]!=0: agg[cols[k_][0]]+=vals[k_]*cols[k_][1]
    print(f"uses {len(agg)} generators:",flush=True)
    for nm in sorted(agg):
        print(f"   [{nm}] * ({sp.factor(sp.expand(agg[nm]))})",flush=True)
