import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from eds_common import reduce_full, e
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, star1_rhs, star3_rhs, window_rules

v = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in range(-3,4)}
gens = [v[j] for j in range(-3,4)] + [B, c, d]

for par_t in [0, 1]:
    E = ( VO_expr(v, 1, (par_t+1)%2)*VO_expr(v, -2, (par_t+2)%2)
        - c**2*VO_expr(v, 0, par_t)*VO_expr(v, -1, (par_t+1)%2)
        + B*d*VE_expr(v, 0)**2 )
    rules = window_rules(v, range(-3,4), par_t,
                         {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    ideal = [r_ for _, r_, _ in rules]
    G = sp.groebner(ideal, *gens, order='grevlex')
    _, r = G.reduce(sp.expand(E))
    print(f"par_t={par_t}: E in <all in-window I/II instances>: {r == 0}")
    if r != 0:
        print("   residue:", sp.factor(sp.expand(r)))
