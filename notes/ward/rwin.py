import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, e
from vmachine import B, c, d, vsmall, VE_expr, VO_expr

# Window symbol tables (V-level). A_i=V(s+i), T_j=V(t+j), P_i=V(s+t+i), Q_j=V(s-t+j).
AW = list(range(-4,5)); TW = list(range(-4,5)); PW = list(range(-4,5)); QW = list(range(-4,5))
Asym = {i: sp.Symbol(f'A{i}'.replace('-','m')) for i in AW}
Tsym = {j: sp.Symbol(f'T{j}'.replace('-','m')) for j in TW}
Psym = {i: sp.Symbol(f'P{i}'.replace('-','m')) for i in PW}
Qsym = {j: sp.Symbol(f'Q{j}'.replace('-','m')) for j in QW}
# s,t assumed EVEN (this parity class). e(alpha*s+beta*t+g) = g%2.

def e_off(form):
    a,b_,g = form
    return g % 2

def add(f1,f2): return (f1[0]+f2[0], f1[1]+f2[1], f1[2]+f2[2])
def sub(f1,f2): return (f1[0]-f2[0], f1[1]-f2[1], f1[2]-f2[2])

def Vexp(form):
    """V-level window polynomial for V(alpha*s+beta*t+g), s,t even."""
    a,b_,g = form
    if a==0 and b_==0:
        # V is odd: V(-k) = -V(k); vmachine.vsmall mishandles negatives, so sign here.
        return vsmall(g) if g >= 0 else -vsmall(-g)
    if a==1 and b_==1:   # window P
        return Psym[g] if g in Psym else _need('P',g)
    if a==1 and b_==-1:  # window Q
        return Qsym[g] if g in Qsym else _need('Q',g)
    if a==-1 and b_==1:  # -(s-t) = t-s -> V(t-s+g) = V(-(s-t-g)) = -Q_{... } : V odd? V(-k)=-V(k)
        # t - s + g = -(s - t - g) => = -Q_{-g}? Q_j=V(s-t+j); we want V(s-t + (-g))* (-1)?? 
        inner = ('Q', -g)  # V(-(s-t-g)) = -V(s-t-g) = -Q_{-g}
        return -(Qsym[-g] if -g in Qsym else _need('Q',-g))
    if a==-1 and b_==-1: # -(s+t)+g
        return -(Psym[-g] if -g in Psym else _need('P',-g))
    if a==1 and b_==0:   # window A
        return Asym[g] if g in Asym else _need('A',g)
    if a==-1 and b_==0:
        return -(Asym[-g] if -g in Asym else _need('A',-g))
    if a==0 and b_==1:   # window T
        return Tsym[g] if g in Tsym else _need('T',g)
    if a==0 and b_==-1:
        return -(Tsym[-g] if -g in Tsym else _need('T',-g))
    if a==2 and b_==0:   # V(2s+g): even g -> VE_A(g/2); odd g -> VO_A((g-1)/2)
        return _double(Asym, g)
    if a==0 and b_==2:
        return _double(Tsym, g)
    if a==2 and b_==2:   # V(2(s+t)+g) -> double of P
        return _double(Psym, g)
    if a==2 and b_==-2:
        return _double(Qsym, g)
    if a==-2 and b_==0:
        return -_double(Asym, -g)
    if a==0 and b_==-2:
        return -_double(Tsym, -g)
    raise ValueError(("Vexp unhandled", form))

def _double(sym, g):
    # V(2*center + g): center-window symbols sym[i]=V(center+i)
    if g % 2 == 0:
        r = g//2
        return VE_expr(sym, r)
    else:
        r = (g-1)//2
        # parity of center is even (s,t,s+t,s-t all even) -> VO_expr(sym, r, e(center+r)=r%2)
        return VO_expr(sym, r, r % 2)

def _need(w,g):
    raise ValueError(("window too narrow", w, g))

def Rdef(p,q,r,s):
    """V-level defect of R(p,q,r,s) with p,q,r,s linear forms (a,b,g), s,t even.
       Returns (poly, ok_flag). Factors common b^(2 gmin); residual uses B=b^4."""
    g1 = e_off(add(p,q))+e_off(add(r,s))
    g2 = e_off(add(p,r))+e_off(add(q,s))
    g3 = e_off(add(p,s))+e_off(add(q,r))
    gm = min(g1,g2,g3)
    dec = []
    for gi in (g1,g2,g3):
        diff = gi-gm
        if diff % 2 != 0:
            return None, False   # needs b^2, not B-expressible
        dec.append(B**(diff//2))
    t1 = dec[0]*Vexp(add(p,q))*Vexp(sub(p,q))*Vexp(add(r,s))*Vexp(sub(r,s))
    t2 = dec[1]*Vexp(add(p,r))*Vexp(sub(p,r))*Vexp(add(q,s))*Vexp(sub(q,s))
    t3 = dec[2]*Vexp(add(p,s))*Vexp(sub(p,s))*Vexp(add(q,r))*Vexp(sub(q,r))
    return sp.expand(t1 - t2 + t3), True

def numverify_Rinst(p,q,r,s, trials=3):
    """Plug real V-windows (s,t even) for the symbolic instance; check ==0."""
    import random
    poly, ok = Rdef(p,q,r,s)
    if not ok: return 'not-B-expressible'
    good = True
    for (bv,cv,dv) in [(2,3,5),(-3,7,11)]:
        Vf = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 200)
        for (sv,tv) in [(8,4),(10,6),(12,4)]:
            subs = {B: bv**4, c: cv, d: dv}
            for i in AW: subs[Asym[i]] = Vf(sv+i)
            for j in TW: subs[Tsym[j]] = Vf(tv+j)
            for i in PW: subs[Psym[i]] = Vf(sv+tv+i)
            for j in QW: subs[Qsym[j]] = Vf(sv-tv+j)
            if sp.simplify(poly.subs(subs)) != 0:
                good = False
    return good
