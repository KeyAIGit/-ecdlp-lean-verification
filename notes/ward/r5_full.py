import sys, time, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from sympy.polys.orderings import grevlex
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules
from rwin import Rdef, numverify_Rinst, Asym, Tsym, Psym, Qsym, AW, TW, PW, QW
t0=time.time()

Prng=list(range(-2,3)); Qrng=list(range(-2,3)); Awin=list(range(-3,4)); Twin=list(range(-3,4))
Pd={i:Psym[i] for i in Prng}; Qd={j:Qsym[j] for j in Qrng}
Ad={i:Asym[i] for i in Awin}; Td={j:Tsym[j] for j in Twin}
allgens=[Psym[i] for i in PW]+[Qsym[j] for j in QW]+[Asym[i] for i in AW]+[Tsym[j] for j in TW]+[B,c,d]

prules=pairing_rules(Pd,Qd,Ad,Td,0,0,Prng,Qrng)
arules=[(n_.replace('(t','(s'),r_,l_) for n_,r_,l_ in window_rules(Ad,Awin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules=window_rules(Td,Twin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
prules_P=window_rules(Pd,Prng,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
qrules_Q=window_rules(Qd,Qrng,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})

def unit_lead_rule(name, defect):
    p=sp.Poly(sp.expand(defect),*allgens)
    if p.is_zero: return None
    units=[(m_,co) for m_,co in p.terms() if co in (1,-1)]
    if not units: return None
    m_,co=max(units,key=lambda t_:grevlex(t_[0]))
    mono=sp.prod([g**k for g,k in zip(allgens,m_)])
    rel=sp.expand(defect/co)  # lead coeff +1
    return (name, rel, mono)

# coupling families
def build_couplings():
    fams=[]
    st=(1,1,0); smt=(1,-1,0); sform=(1,0,0); tform=(0,1,0)
    combos={
      'R(s,t,u,v)':(sform,tform),
      'R(s+t,s-t,u,v)':(st,smt),
      'R(s+t,t,u,v)':(st,tform),
      'R(s,s-t,u,v)':(sform,smt),
    }
    rules=[]
    for lbl,(P1,P2) in combos.items():
        for u in range(-2,3):
            for v in range(-2,3):
                if u==v: continue
                try:
                    pol,ok=Rdef(P1,P2,(0,0,u),(0,0,v))
                except Exception: continue
                if not ok or pol==0: continue
                r=unit_lead_rule(f"{lbl[:-6]}{u},{v})", pol)
                if r: rules.append(r)
    return rules
coup=build_couplings()
print(f"built {len(coup)} coupling rewrite rules ({time.time()-t0:.0f}s)",flush=True)

E = sp.expand( VE_expr(Pd,0)*VE_expr(Qd,0)
    - VO_expr(Ad,0,0)*VO_expr(Ad,-1,1)*VE_expr(Td,0)**2
    + VE_expr(Ad,0)**2*VO_expr(Td,0,0)*VO_expr(Td,-1,1) )

rulesets={'pair':prules,'A':arules,'T':trules,'P':prules_P,'Q':qrules_Q,'coup':coup}
allrules=[]
for k in rulesets: allrules+=rulesets[k]
nm2rel={n_:r_ for n_,r_,_ in allrules}
total={}
rem=E
for it in range(60):
    rem2,cf=reduce_full(rem,allrules,allgens)
    for k_,v_ in cf.items(): total[k_]=sp.expand(total.get(k_,0)+v_)
    nt=0 if rem2==0 else len(sp.Poly(rem2,*allgens).terms())
    if rem2==0:
        print(f"iter {it}: REM 0 ({time.time()-t0:.0f}s)",flush=True); rem=0; break
    if sp.expand(rem2-rem)==0:
        print(f"iter {it}: stalled at {nt} terms ({time.time()-t0:.0f}s)",flush=True); rem=rem2; break
    rem=rem2
    print(f"iter {it}: {nt} terms ({time.time()-t0:.0f}s)",flush=True)
print("FINAL rem==0:", rem==0, flush=True)
if rem==0:
    s=E-sum(cf*nm2rel[n_] for n_,cf in total.items())
    print("exact certificate check expand(E - sum)==0:", sp.expand(s)==0, flush=True)
    used=[(n_,cf) for n_,cf in total.items() if cf!=0]
    print(f"uses {len(used)} instances", flush=True)
    import collections
    bykind=collections.Counter()
    for n_,cf in used:
        kind='coup' if n_.startswith('R(') else ('pair' if 'Star' in n_ and ('s' in n_.split('(')[1][:3] or n_.startswith('VStar1(s') or n_.startswith('VStarOdd(s')) else 'win')
        bykind[n_[:8]]+=1
    for n_,cf in sorted(used)[:40]:
        print(f"   [{n_}] * ({sp.factor(cf)})", flush=True)
else:
    print("residue terms:", len(sp.Poly(rem,*allgens).terms()), flush=True)
    print("residue (factored):", sp.factor(rem), flush=True)
