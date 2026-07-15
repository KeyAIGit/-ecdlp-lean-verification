import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import reduce_full, e

B, c, d = sp.symbols('B c d')
# concrete small V-values as polynomials in B, c, d  (V = preNormEDS(b^4=B, c, d))
Vsmall = {0: sp.Integer(0), 1: sp.Integer(1), 2: sp.Integer(1), 3: c, 4: d}
def vsmall(k):
    k = abs(k) if k >= 0 or True else k
    if k < 0: return -vsmall(-k)
    if k in Vsmall: return Vsmall[k]
    if k % 2 == 0:
        r = k//2
        val = vsmall(r-1)**2*vsmall(r)*vsmall(r+2) - vsmall(r-2)*vsmall(r)*vsmall(r+1)**2
    else:
        r = (k-1)//2
        val = B**e(r)*vsmall(r+2)*vsmall(r)**3 - B**e(r+1)*vsmall(r-1)*vsmall(r+1)**3
    Vsmall[k] = sp.expand(val)
    return Vsmall[k]

def VE_expr(V, r):   # V(2r) in terms of V(r-2..r+2); V is a dict j->symbol relative indexing handled by caller
    return V[r-1]**2*V[r]*V[r+2] - V[r-2]*V[r]*V[r+1]**2
def VO_expr(V, r, par_r):  # V(2r+1); par_r = parity of r as 0/1 meaning r%2
    er, er1 = (1,0) if par_r == 0 else (0,1)   # e(r), e(r+1)
    return B**er*V[r+2]*V[r]**3 - B**er1*V[r-1]*V[r+1]**3

def star1_rhs(V, i, np_, par_mi):
    """RHS of VStar1(m', n') with m'=center+i, n'=np_ concrete>=2, par_mi = (m') % 2.
       V(m'+n')V(m'-n') = B^{e(m'+1)e(n')} V(m'+1)V(m'-1) V(n')^2 - B^{e(m')e(n'+1)} V(n'+1)V(n'-1) V(m')^2"""
    a = e(par_mi+1)*e(np_); b_ = e(par_mi)*e(np_+1)
    return B**a*V[i+1]*V[i-1]*vsmall(np_)**2 - B**b_*vsmall(np_+1)*vsmall(np_-1)*V[i]**2
def star3_rhs(V, i, np_):
    """RHS of VStarOdd(m', n'), m'=center+i, n'=np_: V(m'+n'+1)V(m'-n') =
       V(n'+1)V(n') V(m'+2)V(m'-1) - V(n'+2)V(n'-1) V(m'+1)V(m')   (B-free)"""
    return vsmall(np_+1)*vsmall(np_)*V[i+2]*V[i-1] - vsmall(np_+2)*vsmall(np_-1)*V[i+1]*V[i]

def window_rules(V, J, par_center, allow):
    """Rewrite rules for products v_a v_b (a>b, a-b>=4) within index set J.
       allow: dict name-prefix -> bool/legality predicate, e.g. which families permitted.
       par_center = center parity (0 even,1 odd). Returns list for reduce_full."""
    rules = []
    pairs = sorted([(a,b_) for a in J for b_ in J if a > b_ and a-b_ >= 4],
                   key=lambda ab: -(ab[0]-ab[1]))
    for a, b_ in pairs:
        sprd = a - b_
        if sprd % 2 == 0:
            i = (a+b_)//2; np_ = sprd//2
            if np_ == 2 and allow.get('VS', True):
                name = f"VStar1(t{i:+d},2)"
            elif np_ == 3 and allow.get('VSl3', False):
                name = f"VStar1(t{i:+d},3)"
            else:
                continue
            if i+1 not in J or i-1 not in J: continue
            par_mi = (par_center + i) % 2
            rel = V[a]*V[b_] - star1_rhs(V, i, np_, par_mi)
        else:
            i = (a+b_-1)//2; np_ = (sprd-1)//2
            if np_ == 2 and allow.get('VG3', False):
                name = f"VStarOdd(t{i:+d},2)"
            elif np_ == 3 and allow.get('VSlOdd3', False):
                name = f"VStarOdd(t{i:+d},3)"
            else:
                continue
            if i+2 not in J or i-1 not in J: continue
            rel = V[a]*V[b_] - star3_rhs(V, i, np_)
        rules.append((name, sp.expand(rel), V[a]*V[b_]))
    return rules
