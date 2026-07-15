import sys, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk, pairing_rules

par_s = par_t = 0
Prng = list(range(-1,3)); Qrng = list(range(-2,2))
Awin = list(range(-3,4)); Twin = list(range(-2,4))
P = mk('P', Prng); Q = mk('Q', Qrng); A = mk('A', Awin); T = mk('T', Twin)
gens = [P[a] for a in Prng]+[Q[b_] for b_ in Qrng]+[A[i] for i in Awin]+[T[j] for j in Twin]+[B,c,d]
prules = pairing_rules(P, Q, A, T, par_s, par_t, Prng, Qrng)

def dbl_A(x):
    return VE_expr(A, x//2) if x % 2 == 0 else VO_expr(A, (x-1)//2, ((x-1)//2) % 2)
def dbl_T(y):
    return VE_expr(T, y//2) if y % 2 == 0 else VO_expr(T, (y-1)//2, ((y-1)//2) % 2)

couplings = []
for i in range(-2,3):
    for j in range(-2,3):
        # family I cross: needs P[i+1],P[i-1],Q[j+1],Q[j-1],P[i],Q[j]
        if (i-j) % 2 == 0 and all(k in Prng for k in [i-1,i,i+1]) and all(k in Qrng for k in [j-1,j,j+1]):
            al = e(i+1)*e(j); be = e(i)*e(j+1)
            pq = B**al*P[i+1]*P[i-1]*Q[j]**2 - B**be*Q[j+1]*Q[j-1]*P[i]**2
            x = i+j; y = i-j; name = f"X1({i},{j})"
            rempq, _ = reduce_full(sp.expand(pq), prules, gens)
            if set(rempq.free_symbols) & set(list(P.values())+list(Q.values())): continue
            couplings.append((name, sp.expand(dbl_A(x)*dbl_T(y) - rempq)))
        if (i-j) % 2 == 1 and all(k in Prng for k in [i-1,i,i+1,i+2]) and all(k in Qrng for k in [j-1,j,j+1,j+2]):
            pq = Q[j+1]*Q[j]*P[i+2]*P[i-1] - Q[j+2]*Q[j-1]*P[i+1]*P[i]
            x = i+j+1; y = i-j; name = f"X2({i},{j})"
            rempq, _ = reduce_full(sp.expand(pq), prules, gens)
            if set(rempq.free_symbols) & set(list(P.values())+list(Q.values())): continue
            couplings.append((name, sp.expand(dbl_A(x)*dbl_T(y) - rempq)))
print(f"built {len(couplings)} couplings: {[n for n,_ in couplings]}", flush=True)

E = ( VO_expr(P,0,0)*VO_expr(Q,-1,1)
    - VO_expr(A,0,0)*VO_expr(A,-1,1)*VO_expr(T,0,0)**2
    + B*VE_expr(T,1)*VE_expr(T,0)*VE_expr(A,0)**2 )
arules = [(n_.replace('(t','(s'), r_, l_) for n_, r_, l_ in window_rules(A, Awin, 0, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})]
trules = window_rules(T, Twin, 0, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
tail, _ = reduce_full(sp.expand(E), prules+arules+trules, gens)
print("tail terms:", len(sp.Poly(tail,*gens).terms()), flush=True)

tgens = [A[i] for i in Awin] + [T[j] for j in Twin] + [B, c, d]
idealg = [r_ for _,r_,_ in arules] + [r_ for _,r_,_ in trules] + [x_ for _, x_ in couplings]
t0 = time.time()
G = sp.groebner(idealg, *tgens, order='grevlex')
print(f"GB built ({time.time()-t0:.0f}s)", flush=True)
_, r = G.reduce(tail)
print("OUTER-ODD tail in <windows + cross-couplings>:", r == 0, flush=True)
if r != 0:
    print("residue terms:", len(sp.Poly(sp.expand(r), *tgens).terms()), flush=True)
