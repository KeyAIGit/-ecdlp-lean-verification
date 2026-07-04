import sys, time, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules
from rwin import Rdef, Asym, Tsym, Psym, Qsym, AW, TW, PW, QW
t0=time.time()

# Use the SAME window symbols as outer_common for pairing (P_i,Q_j,A_i,T_j).
# Map rwin symbols onto outer_common style: rebuild pairing on rwin symbols.
Prng=list(range(-2,3)); Qrng=list(range(-2,3)); Awin=list(range(-3,4)); Twin=list(range(-3,4))
# pairing_rules expects dict windows P,Q,A,T with those keys; use rwin's (they include these).
Pd={i:Psym[i] for i in Prng}; Qd={j:Qsym[j] for j in Qrng}
Ad={i:Asym[i] for i in Awin}; Td={j:Tsym[j] for j in Twin}
prules = pairing_rules(Pd,Qd,Ad,Td,0,0,Prng,Qrng)
arules = [(n_.replace('(t','(s'), r_, l_) for n_,r_,l_ in window_rules(Ad,Awin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules = window_rules(Td,Twin,0,{'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
allgens = [Psym[i] for i in PW]+[Qsym[j] for j in QW]+[Asym[i] for i in AW]+[Tsym[j] for j in TW]+[B,c,d]

# master defect
E = sp.expand( VE_expr(Pd,0)*VE_expr(Qd,0)
    - VO_expr(Ad,0,0)*VO_expr(Ad,-1,1)*VE_expr(Td,0)**2
    + VE_expr(Ad,0)**2*VO_expr(Td,0,0)*VO_expr(Td,-1,1) )
# reduce E by pairing -> tail (pure A,T)
tail, cof_pair = reduce_full(E, prules, allgens)
tsyms = tail.free_symbols
has_pq = any(Psym[i] in tsyms for i in PW) or any(Qsym[j] in tsyms for j in QW)
print(f"tail pure A,T: {not has_pq}; terms {len(sp.Poly(tail,*allgens).terms())} ({time.time()-t0:.0f}s)", flush=True)

# D(u,v): coupling R(s+t,s-t,u,v) reduced by pairing -> pure A,T relation
st=(1,1,0); smt=(1,-1,0)
Ds=[]
for u in range(-2,3):
    for v in range(-2,3):
        if u==v: continue
        pol,ok = Rdef(st,smt,(0,0,u),(0,0,v))
        if not ok: continue
        red, _ = reduce_full(sp.expand(pol), prules, allgens)
        rs = red.free_symbols
        if any(Psym[i] in rs for i in PW) or any(Qsym[j] in rs for j in QW):
            # try two passes
            red, _ = reduce_full(red, prules, allgens)
            rs = red.free_symbols
        pure = not (any(Psym[i] in rs for i in PW) or any(Qsym[j] in rs for j in QW))
        if red != 0 and pure:
            Ds.append((f"D({u},{v})", sp.expand(red)))
print(f"built {len(Ds)} nonzero pure-A,T couplings D(u,v) ({time.time()-t0:.0f}s)", flush=True)

# membership: tail in ideal < A-rules, T-rules, D(u,v) > over A,T gens?
ATgens=[Asym[i] for i in AW]+[Tsym[j] for j in TW]+[B,c,d]
ideal=[r_ for _,r_,_ in arules]+[r_ for _,r_,_ in trules]+[pol for _,pol in Ds]
print(f"running GB on {len(ideal)} gens over {len(ATgens)} vars ...", flush=True)
G=sp.groebner(ideal, *ATgens, order='grevlex')
print(f"GB size {len(G.exprs)} ({time.time()-t0:.0f}s)", flush=True)
_,rem=G.reduce(tail)
print("MASTER TAIL in <I_A + I_T + couplings D>:", rem==0, f"({time.time()-t0:.0f}s)", flush=True)
if rem!=0:
    print("residue terms:", len(sp.Poly(sp.expand(rem),*ATgens).terms()), flush=True)
