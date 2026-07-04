import sys
sys.path.insert(0,'/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp
from rwin import Rdef, numverify_Rinst, Asym,Tsym,Psym,Qsym
from vmachine import B,c,d
pol,ok=Rdef((1,0,0),(0,1,0),(0,0,1),(0,0,0))
print("R(s,t,1,0) B-expressible:",ok,"; numverify:",numverify_Rinst((1,0,0),(0,1,0),(0,0,1),(0,0,0)))
print("R(s,t,1,0) V-level defect =", sp.expand(pol))
print()
print("R(s+t,s-t,1,0)=(star1)(s+t,s-t) numverify:",numverify_Rinst((1,1,0),(1,-1,0),(0,0,1),(0,0,0)))
