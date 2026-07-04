import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import make_V, make_W, reduce_full, e
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, star1_rhs, star3_rhs, window_rules

# ---------- (0) numeric verification of the second master family (*3) ----------
okW = okV = True
for (bv,cv,dv) in [(2,3,5),(-3,7,11),(13,4,9)]:
    V = make_V(sp.Integer(bv), sp.Integer(cv), sp.Integer(dv), 40)
    W = make_W(V, sp.Integer(bv))
    for m in range(-9,10):
        for n in range(-9,10):
            x = bv*W(m+n+1)*W(m-n) - (W(n+1)*W(n)*W(m+2)*W(m-1) - W(n+2)*W(n-1)*W(m+1)*W(m))
            if x != 0: okW = False; print("W *3 fail", m, n)
            y = V(m+n+1)*V(m-n) - (V(n+1)*V(n)*V(m+2)*V(m-1) - V(n+2)*V(n-1)*V(m+1)*V(m))
            if y != 0: okV = False; print("V *3 fail", m, n)
print("(*3) W-level b*W(m+n+1)W(m-n)=... :", okW)
print("(*3) V-level B-free parity-uniform:", okV)

# ---------- V-level slice-3 of family I, m = 2t : certificates for t even / t odd ----------
# goal defect: E = VO(t+1)VO(t-2) - c^2 VO(t)VO(t-1) + B d VE(t)^2   (uses e(m)=e(2t)=1... exponent B^{e(2t)}=B)
v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in range(-3,4)}
gens = [v[j] for j in range(-3,4)] + [B, c, d]
for par_t in [0, 1]:
    E = ( VO_expr(v, 1, (par_t+1)%2)*VO_expr(v, -2, (par_t+2)%2)
        - c**2*VO_expr(v, 0, par_t)*VO_expr(v, -1, (par_t+1)%2)
        + B*d*VE_expr(v, 0)**2 )
    rules = window_rules(v, range(-3,4), par_t,
                         {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    rem, cof = reduce_full(sp.expand(E), rules, gens)
    print(f"\n== slice-3(I), m=2t, t%2={par_t}:  remainder = {rem}")
    if rem == 0:
        chk = E
        rbn = {n_: r_ for n_, r_, _ in rules}
        for n_, cf in cof.items(): chk = chk - cf*rbn[n_]
        print("   exact:", sp.expand(chk) == 0)
        for n_, cf in sorted(cof.items()):
            if cf != 0: print(f"   [{n_}] * ({sp.factor(cf)})")
