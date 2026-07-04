import sys, itertools, random, time
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import e
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from outer_common import mk

par_s = par_t = 0
Awin = list(range(-3,4)); Twin = list(range(-3,4))
A = mk('A', Awin); T = mk('T', Twin)

def f_form(a, b_):
    """A,T-window form of P_a*Q_b via family I/II instance; returns (name, expr)."""
    if (a+b_) % 2 == 0:
        i = (a+b_)//2; j = (a-b_)//2
        al = e(par_s+i+1)*e(par_t+j); be = e(par_s+i)*e(par_t+j+1)
        return (f"VStar1(s{i:+d},t{j:+d})",
                B**al*A[i+1]*A[i-1]*T[j]**2 - B**be*T[j+1]*T[j-1]*A[i]**2)
    else:
        i = (a+b_-1)//2; j = (a-b_-1)//2
        return (f"VStarOdd(s{i:+d},t{j:+d})",
                T[j+1]*T[j]*A[i+2]*A[i-1] - T[j+2]*T[j-1]*A[i+1]*A[i])

# VE(P;0) monomials: +P(-1)^2 P0 P2, -P(-2) P0 P1^2 ; same for Q
Pmons = [ (1, [-1,-1,0,2]), (-1, [-2,0,1,1]) ]
Qmons = [ (1, [-1,-1,0,2]), (-1, [-2,0,1,1]) ]

# pure A,T part of E:
Erest = sp.expand( - VO_expr(A,0,0)*VO_expr(A,-1,1)*VE_expr(T,0)**2
                   + VO_expr(T,0,0)*VO_expr(T,-1,1)*VE_expr(A,0)**2 )

def variant_tail(perms):
    """perms: dict (mi,ni) -> permutation tuple of range(4). Returns A,T tail expr + usage list."""
    total = 0; usage = []
    for (mi,(sgnP, plist)) in enumerate(Pmons):
        for (ni,(sgnQ, qlist)) in enumerate(Qmons):
            perm = perms[(mi,ni)]
            prod = sgnP*sgnQ
            expr = sp.Integer(1)
            for k_ in range(4):
                a = plist[k_]; b_ = qlist[perm[k_]]
                nm, ff = f_form(a, b_)
                expr = expr * ff
                usage.append(nm)
            total += prod*sp.expand(expr)
    return sp.expand(total + Erest), usage

gens = [A[i] for i in Awin] + [T[j] for j in Twin] + [B, c, d]
arules = window_rules(A, Awin, par_s, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
trules = window_rules(T, Twin, par_t, {'VS':True,'VSl3':True,'VG3':True,'VSlOdd3':True})
GA = sp.groebner([r_ for _,r_,_ in arules], *gens, order='grevlex')
GT = sp.groebner([r_ for _,r_,_ in trules], *gens, order='grevlex')
print("window GBs built", flush=True)

def member(expr):
    _, r1 = GA.reduce(expr)
    if r1 == 0: return True
    _, r2 = GT.reduce(r1)
    return r2 == 0

random.seed(1)
perms4 = list(itertools.permutations(range(4)))
tried = set()
t0 = time.time()
found = None
# canonical first: identity and reverse for all four blocks, then random
cands = [ {k: p for k in [(0,0),(0,1),(1,0),(1,1)]} for p in [tuple(range(4)), (3,2,1,0)] ]
while len(cands) < 220:
    cands.append({k: random.choice(perms4) for k in [(0,0),(0,1),(1,0),(1,1)]})
for idx, pm in enumerate(cands):
    key = tuple(sorted(pm.items()))
    if key in tried: continue
    tried.add(key)
    tail, usage = variant_tail(pm)
    if member(tail):
        found = (pm, usage)
        print(f"FOUND variant {idx} after {time.time()-t0:.0f}s: {pm}", flush=True)
        break
    if idx % 20 == 0:
        print(f"  tried {idx} ({time.time()-t0:.0f}s)", flush=True)
if not found:
    print("no variant found in sample", flush=True)
