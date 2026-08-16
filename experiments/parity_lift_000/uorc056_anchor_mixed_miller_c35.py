from functools import lru_cache

P=43; N=31; G=(2,12)
A=0; B=7


def inv(x): return pow(x % P, -1, P)
def add(P1,P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1,y1=P1; x2,y2=P2
    if x1==x2 and (y1+y2)%P==0: return None
    if P1==P2: m=(3*x1*x1+A)*inv(2*y1)%P
    else: m=(y2-y1)*inv(x2-x1)%P
    x3=(m*m-x1-x2)%P
    return x3,(m*(x1-x3)-y1)%P

def mul(k,Q):
    R=None
    while k:
        if k&1: R=add(R,Q)
        Q=add(Q,Q); k//=2
    return R

def leg(x): return 1 if pow(x%P,(P-1)//2,P)==1 else -1

def psi(m,Q):
    x,y=Q
    @lru_cache(None)
    def f(j):
        if j==0:return 0
        if j==1:return 1
        if j==2:return 2*y%P
        if j==3:return (3*x**4+12*B*x)%P
        if j==4:return (4*y*(x**6+20*B*x**3-8*B**2))%P
        if j&1:
            r=(j-1)//2
            return (f(r+2)*pow(f(r),3,P)-f(r-1)*pow(f(r+1),3,P))%P
        r=j//2
        return (f(r)*inv(2*y)*(f(r+2)*pow(f(r-1),2,P)-f(r-2)*pow(f(r+1),2,P)))%P
    return f(m)

locations=[
    ('Q',1),('A',2),('T',(N-1)//2),('B',(N-1)//2-2),
    ('negT',(N+1)//2),('negB',(N+1)//2+2),('U',3)
]
features=[(m,name,u) for m in range(2,30) for name,u in locations]
base={(m,name):psi(m,mul(u,G)) for m,name,u in features}
assert all(base.values())

# Solve A*c=t over F2, where signs are normalized to +1 at k=1 and
# t(k)=(-1)^(k+1). Inconsistency certifies no product of declared atoms.
piv={}; witness=None; rows=0
for k in range(1,N):
    Q=mul(k,G); mask=0
    for i,(m,name,u) in enumerate(features):
        v=psi(m,mul(u,Q)); assert v
        if leg(v*inv(base[(m,name)]))==-1: mask |= 1<<i
    target=(k+1)&1
    x=mask | (target<<len(features))
    for j in sorted(piv,reverse=True):
        if (x>>j)&1: x ^= piv[j]
    fpart=x & ((1<<len(features))-1)
    if not fpart:
        if (x>>len(features))&1:
            witness=k
            break
    else:
        piv[fpart.bit_length()-1]=x
    rows += 1

assert witness is not None
print('UORC056_C35_CHARACTER_SPAN_INCONSISTENT')
print('curve=p43,n31,G=(2,12)')
print('features=',len(features))
print('processed_rows=',rows)
print('contradiction_at_k=',witness)
print('rank_before_contradiction=',len(piv))
