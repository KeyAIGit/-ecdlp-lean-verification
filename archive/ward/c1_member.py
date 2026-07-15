import sys
sys.path.insert(0, '/tmp/claude-0/-home-user--ecdlp-lean-verification/a3e81a8a-87b5-5b62-8db4-c6e19b0f93d5/scratchpad/ward')
import sympy as sp

b, c, d = sp.symbols('b c d')
w = {j: sp.Symbol(f'w{j}'.replace('-','m')) for j in range(-3,4)}
def O(r):  return w[r+2]*w[r]**3 - w[r-1]*w[r+1]**3
def Ev(r): return w[r-1]**2*w[r]*w[r+2] - w[r-2]*w[r]*w[r+1]**2
S = {i: w[i+2]*w[i-2] - b**2*w[i+1]*w[i-1] + c*w[i]**2 for i in [-1,0,1]}
H3 = w[3]*w[-3] - c**2*w[1]*w[-1] + b**2*d*w[0]**2
E = sp.expand(O(1)*O(-2) - c**2*O(0)*O(-1) + d*Ev(0)**2)

gens = [w[j] for j in range(-3,4)] + [b, c, d]
G = sp.groebner([S[-1], S[0], S[1], H3], *gens, order='grevlex')
Q, r = G.reduce(E)
print("membership in <S(t-1),S(t),S(t+1),Star3(t)>:", r == 0)
if r != 0:
    print("residue:", sp.expand(r))
