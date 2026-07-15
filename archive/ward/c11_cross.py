import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

par_s = par_t = 0
Awin = list(range(-3,4)); Twin = list(range(-3,4))
Prng = list(range(-2,3)); Qrng = list(range(-2,3))
P = mk('P', Prng); Q = mk('Q', Qrng); A = mk('A', Awin); T = mk('T', Twin)
gens = [P[a] for a in Prng]+[Q[b_] for b_ in Qrng]+[A[i] for i in Awin]+[T[j] for j in Twin]+[B,c,d]

prules = pairing_rules(P, Q, A, T, par_s, par_t, Prng, Qrng)
prule_map = {l_: (n_, r_) for n_, r_, l_ in prules}

def dbl_A(x):
    """V(2s+x) expanded into A window; x even -> VE(A at s+x/2); x odd -> VO(A at s+(x-1)/2)."""
    if x % 2 == 0:
        return VE_expr(A, x//2)
    return VO_expr(A, (x-1)//2, (par_s + (x-1)//2) % 2)
def dbl_T(y):
    if y % 2 == 0:
        return VE_expr(T, y//2)
    return VO_expr(T, (y-1)//2, (par_t + (y-1)//2) % 2)

# cross instances -> pure A,T couplings
couplings = []
for i in range(-1,2):
    for j in range(-1,2):
        try:
            if (i - j) % 2 == 0:
                al = e(i+1)*e(j); be = e(i)*e(j+1)   # s,t even: e(s+t+i+1)e(s-t+j) etc.
                pq = B**al*P[i+1]*P[i-1]*Q[j]**2 - B**be*Q[j+1]*Q[j-1]*P[i]**2
                x = i+j; y = i-j
                name = f"X1({i},{j})"
            else:
                pq = Q[j+1]*Q[j]*P[i+2]*P[i-1] - Q[j+2]*Q[j-1]*P[i+1]*P[i]
                x = i+j+1; y = i-j
                name = f"X2({i},{j})"
        except KeyError:
            continue
        lhs = sp.expand(dbl_A(x)*dbl_T(y))
        # reduce pq via pairing rules to pure A,T
        rempq, cofpq = reduce_full(sp.expand(pq), prules, gens)
        if rempq != 0 and (set(rempq.free_symbols) & set(list(P.values())+list(Q.values()))):
            print("  pairing residue for", name); continue
        Cij = sp.expand(lhs - rempq)
        couplings.append((name, Cij))
print(f"built {len(couplings)} couplings", flush=True)

# tail of the outer-even case (rebuild)
E = ( VE_expr(P,0)*VE_expr(Q,0)
    - VO_expr(A,0,0)*VO_expr(A,-1,1)*VE_expr(T,0)**2
    + VO_expr(T,0,0)*VO_expr(T,-1,1)*VE_expr(A,0)**2 )
arules = [(n_.replace('(t','(s'), r_, l_) for n_, r_, l_ in window_rules(A, Awin, par_s, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules = window_rules(T, Twin, par_t, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
tail, cof1 = reduce_full(sp.expand(E), prules+arules+trules, gens)
print("tail terms:", len(sp.Poly(tail,*gens).terms()), flush=True)

# Groebner membership: tail in < A-rules, T-rules, couplings >?
tgens = [A[i] for i in Awin] + [T[j] for j in Twin] + [B, c, d]
idealg = [r_ for _,r_,_ in arules] + [r_ for _,r_,_ in trules] + [Cij for _, Cij in couplings]
t0 = time.time()
G = sp.groebner(idealg, *tgens, order='grevlex')
print(f"GB built ({time.time()-t0:.0f}s), size {len(G.exprs)}", flush=True)
_, r = G.reduce(tail)
print("tail in <windows + cross-couplings>:", r == 0, flush=True)
if r != 0:
    print("residue terms:", len(sp.Poly(sp.expand(r), *tgens).terms()))
    print(sp.factor(r))
