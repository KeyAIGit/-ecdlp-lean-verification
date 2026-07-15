import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from rwin import Rdef, numverify_Rinst, Vexp, Asym, Tsym, Psym, Qsym, AW, TW, PW, QW
from vmachine import B, c, d, VE_expr, VO_expr

# master defect (V-level even-even) as before:
E = sp.expand( VE_expr(Psym,0)*VE_expr(Qsym,0)
    - VO_expr(Asym,0,0)*VO_expr(Asym,-1,1)*VE_expr(Tsym,0)**2
    + VE_expr(Asym,0)**2*VO_expr(Tsym,0,0)*VO_expr(Tsym,-1,1) )
# sanity: master = R(2s,2t,1,0) V-level?
Rm, ok = Rdef((2,0,0),(0,2,0),(0,0,1),(0,0,0))
print("master matches R(2s,2t,1,0):", ok and sp.expand(E - Rm) == 0, flush=True)

# probe candidate coupling instances R(s+t, s-t, u, v)
st=(1,1,0); smt=(1,-1,0)
print("\nCoupling instances R(s+t, s-t, u, v):", flush=True)
for u in range(-2,3):
    for v in range(-2,3):
        if u==v: continue
        r=(0,0,u); s=(0,0,v)
        try:
            res = numverify_Rinst(st,smt,r,s)
        except Exception as ex:
            res = f"ERR {ex}"
        print(f"  R(s+t,s-t,{u},{v}): {res}", flush=True)
