from dataclasses import dataclass
from typing import Optional

Point=Optional[tuple[int,int]]
@dataclass
class Curve:
    p:int; a:int; b:int
    def add(self,P:Point,Q:Point)->Point:
        if P is None:return Q
        if Q is None:return P
        p=self.p; x1,y1=P; x2,y2=Q
        if x1==x2 and (y1+y2)%p==0:return None
        m=((3*x1*x1+self.a)*pow(2*y1,-1,p) if P==Q else (y2-y1)*pow(x2-x1,-1,p))%p
        x3=(m*m-x1-x2)%p
        return x3,(m*(x1-x3)-y1)%p
    def mul(self,k:int,P:Point)->Point:
        if k<0:return self.mul(-k,(P[0],-P[1]%self.p))
        R=None; A=P
        while k:
            if k&1:R=self.add(R,A)
            A=self.add(A,A); k//=2
        return R

INST=[
 (Curve(43,0,7),31,(2,12)),(Curve(67,0,7),79,(2,22)),
 (Curve(79,0,7),67,(1,18)),(Curve(127,0,7),127,(1,32)),
 (Curve(163,0,7),139,(2,34))]

def ycoeff(E,Q):
    p=E.p;x,y=Q; inv=pow(2*y,-1,p)
    c1=(3*x*x+E.a)*inv%p
    c2=(3*x-c1*c1)*inv%p
    c3=(1-2*c1*c2)*inv%p
    return c1,c2,c3

def line_local(E,P,R,Q):
    p=E.p
    if P is None or R is None:return 0,1
    x1,y1=P;x2,y2=R;xq,yq=Q
    if x1==x2 and (y1+y2)%p==0:
        d=(xq-x1)%p; return (0,d) if d else (1,1)
    m=((3*x1*x1+E.a)*pow(2*y1,-1,p) if P==R else (y2-y1)*pow(x2-x1,-1,p))%p
    z=(yq-y1-m*(xq-x1))%p
    if z:return 0,z
    c1,c2,c3=ycoeff(E,Q)
    if (c1-m)%p:return 1,(c1-m)%p
    if c2:return 2,c2
    if c3:return 3,c3
    raise AssertionError('contact order >3')

def vertical_local(E,S,Q):
    if S is None:return 0,1
    d=(Q[0]-S[0])%E.p
    return (0,d) if d else (1,1)

def g_local(E,P,R,Q):
    vl,cl=line_local(E,P,R,Q); vv,cv=vertical_local(E,E.add(P,R),Q)
    return vl-vv,cl*pow(cv,-1,E.p)%E.p

def mmul(E,u,v):return u[0]+v[0],u[1]*v[1]%E.p
def mpow(E,u,e):return u[0]*e,pow(u[1],e,E.p)

def miller_local(E,m,P,Q):
    T=P; z=(0,1)
    for bit in bin(m)[3:]:
        z=mmul(E,mpow(E,z,2),g_local(E,T,T,Q)); T=E.add(T,T)
        if bit=='1':
            z=mmul(E,z,g_local(E,T,P,Q)); T=E.add(T,P)
    return z

def leg(E,x):return 1 if pow(x%E.p,(E.p-1)//2,E.p)==1 else -1

def affine_decoder_exists(E,n,G):
    vals=[]
    for k in range(1,n):
        Q=E.mul(k,G)
        fn=miller_local(E,n,G,Q)[1]; f3=miller_local(E,3,G,Q)[1]
        vals.append((fn,f3,1 if k%2==0 else -1))
    p=E.p
    for a,b in [(1,b) for b in range(p)]+[(0,1)]:
        for c in range(p):
            ok=True
            for x,y,t in vals:
                z=(a*x+b*y+c)%p
                if z==0 or leg(E,z)!=t:ok=False;break
            if ok:return True
    return False

def pair_separates(E,n,G):
    seen={}
    for k in range(1,n):
        Q=E.mul(k,G)
        st=(miller_local(E,n,G,Q),miller_local(E,3,G,Q))
        if st in seen and seen[st]!=(k&1):return False
        seen[st]=k&1
    return True

def main():
    declared=lambda n:[n,n-1,(n-1)//2,(n+1)//2,2,3,5,7,8]
    total=0; wrong_single=0; separating=0; affine_fail=0
    for E,n,G in INST:
        for m in declared(n):
            exact=True
            for k in range(1,n):
                Q=E.mul(k,G); v,c=miller_local(E,m,G,Q)
                expected=m if Q==G else (-1 if Q==E.mul(m,G) else 0)
                if Q==G and Q==E.mul(m,G):expected=m-1
                assert v==expected
                if leg(E,c)!=(1 if k%2==0 else -1):exact=False
                total+=1
            if not exact:wrong_single+=1
        separating+=pair_separates(E,n,G)
        affine_fail+=not affine_decoder_exists(E,n,G)
    assert wrong_single==5*9
    assert separating==5
    assert affine_fail==5
    print('UORC056_REGULARIZED_ANCHOR_MILLER_C36_OK')
    print('regularized_scalar_checks=',total)
    print('single_character_failures=',wrong_single)
    print('Fn_F3_pair_separates_curves=',separating)
    print('affine_character_decoder_failures=',affine_fail)

if __name__=='__main__':main()
