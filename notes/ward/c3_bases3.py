import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from vmachine import B, c, d, VE_expr, VO_expr
from solver import subwindow_solve

J8 = list(range(-3,5)); J7 = list(range(-3,4))
v8 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J8}
v7 = {j: sp.Symbol(f'v{j}'.replace('-','m')) for j in J7}

for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VE_expr(v8, -1) - c**2*VE_expr(v8, 1)*VE_expr(v8, 0)
        + d*VO_expr(v8, 0, par_t)**2 )
    subwindow_solve(f"slice-3(I) m=2t+1, t%2={par_t}", E, v8, J8, par_t)
for par_t in [0,1]:
    E = sp.expand( VO_expr(v7, 1, (par_t+1)%2)*VE_expr(v7, -1)
        - c*VE_expr(v7, 1)*VO_expr(v7, -1, (par_t+1)%2)
        + d*VO_expr(v7, 0, par_t)*VE_expr(v7, 0) )
    subwindow_solve(f"slice-2(II) m=2t, t%2={par_t}", E, v7, J7, par_t)
for par_t in [0,1]:
    E = sp.expand( VE_expr(v8, 2)*VO_expr(v8, -1, (par_t+1)%2)
        - c*VO_expr(v8, 1, (par_t+1)%2)*VE_expr(v8, 0)
        + d*VE_expr(v8, 1)*VO_expr(v8, 0, par_t) )
    subwindow_solve(f"slice-2(II) m=2t+1, t%2={par_t}", E, v8, J8, par_t)
print("\nDONE")
