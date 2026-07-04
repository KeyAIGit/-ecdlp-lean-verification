import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from vmachine import B, c, d, VE_expr, VO_expr
from outer_common import mk, run_case

# (I) at (m,n)=(2s,2t), s,t even. Goal B-free:
# E = VE|P(s+t) * VE|Q(s-t) - VO(s)VO(s-1) * VE|T(t)^2 + VO(t)VO(t-1) * VE|A(s)^2
P = mk('P', range(-2,3)); Q = mk('Q', range(-2,3))
A = mk('A', range(-3,4)); T = mk('T', range(-3,4))
VEP = VE_expr(P, 0)          # V(2(s+t)) with P_j = V(s+t+j)
VEQ = VE_expr(Q, 0)          # V(2(s-t))
VOs   = VO_expr(A, 0, 0)     # V(2s+1), s even
VOsm1 = VO_expr(A, -1, 1)    # V(2s-1) = VO(s-1), s-1 odd
VOt   = VO_expr(T, 0, 0)
VOtm1 = VO_expr(T, -1, 1)
VET = VE_expr(T, 0); VEA = VE_expr(A, 0)
E = VEP*VEQ - VOs*VOsm1*VET**2 + VOt*VOtm1*VEA**2
run_case("OUTER-EVEN (I)(2s,2t) s,t even", E, P, Q, A, T, 0, 0,
         list(range(-2,3)), list(range(-2,3)), list(range(-3,4)), list(range(-3,4)))
print("\nDONE")
