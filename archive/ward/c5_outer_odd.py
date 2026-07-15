import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from vmachine import B, c, d, VE_expr, VO_expr
from outer_common import mk, run_case

# (I) at (m,n)=(2s,2t+1), s,t even:
# E = VO|P(s+t) * VO|Q(s-t-1) - VO(s)VO(s-1) * VO|T(t)^2 + B * VE|T(t+1)VE|T(t) * VE|A(s)^2
Prng = list(range(-1,3)); Qrng = list(range(-2,2))
Awin = list(range(-3,4)); Twin = list(range(-2,4))
P = mk('P', Prng); Q = mk('Q', Qrng); A = mk('A', Awin); T = mk('T', Twin)
VOP = VO_expr(P, 0, 0)      # V(2(s+t)+1), s+t even
VOQ = VO_expr(Q, -1, 1)     # V(2(s-t)-1), s-t-1 odd
VOs = VO_expr(A, 0, 0); VOsm1 = VO_expr(A, -1, 1)
VOt = VO_expr(T, 0, 0)
E = VOP*VOQ - VOs*VOsm1*VOt**2 + B*VE_expr(T,1)*VE_expr(T,0)*VE_expr(A,0)**2
run_case("OUTER-ODD (I)(2s,2t+1) s,t even", E, P, Q, A, T, 0, 0, Prng, Qrng, Awin, Twin)
print("\nDONE")
