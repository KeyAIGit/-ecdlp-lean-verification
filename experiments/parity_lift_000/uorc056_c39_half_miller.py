from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


def legendre(a:int,p:int)->int:
    a%=p
    if a==0:return 0
    return 1 if pow(a,(p-1)//2,p)==1 else -1

def least_nonsquare(p:int)->int:
    return next(d for d in range(2,p) if legendre(d,p)==-1)

def sqrt_mod_brute(a:int,p:int):
    a%=p
    return next((x for x in range(p) if x*x%p==a),None)

@dataclass(frozen=True)
class Fp2:
    a:int; b:int; p:int; d:int
    def __post_init__(self):
        object.__setattr__(self,'a',self.a%self.p);object.__setattr__(self,'b',self.b%self.p)
    @classmethod
    def coerce(cls,x,p,d):
        if isinstance(x,Fp2):
            assert x.p==p and x.d==d;return x
        return cls(int(x),0,p,d)
    def __add__(self,o):o=Fp2.coerce(o,self.p,self.d);return Fp2(self.a+o.a,self.b+o.b,self.p,self.d)
    __radd__=__add__
    def __neg__(self):return Fp2(-self.a,-self.b,self.p,self.d)
    def __sub__(self,o):return self+(-Fp2.coerce(o,self.p,self.d))
    def __rsub__(self,o):return Fp2.coerce(o,self.p,self.d)-self
    def __mul__(self,o):
        o=Fp2.coerce(o,self.p,self.d);return Fp2(self.a*o.a+self.d*self.b*o.b,self.a*o.b+self.b*o.a,self.p,self.d)
    __rmul__=__mul__
    def conj(self):return Fp2(self.a,-self.b,self.p,self.d)
    def norm(self):return (self.a*self.a-self.d*self.b*self.b)%self.p
    def inv(self):
        z=self.norm()
        if z==0:raise ZeroDivisionError
        z=pow(z,-1,self.p);c=self.conj();return Fp2(c.a*z,c.b*z,self.p,self.d)
    def __truediv__(self,o):return self*Fp2.coerce(o,self.p,self.d).inv()
    def __rtruediv__(self,o):return Fp2.coerce(o,self.p,self.d)*self.inv()
    def __pow__(self,e:int):
        if e<0:return self.inv()**(-e)
        r=Fp2(1,0,self.p,self.d);x=self
        while e:
            if e&1:r=r*x
            x=x*x;e//=2
        return r
    def __bool__(self):return self.a!=0 or self.b!=0
    def __eq__(self,o):
        try:o=Fp2.coerce(o,self.p,self.d)
        except Exception:return False
        return self.a==o.a and self.b==o.b
    def tuple(self):return self.a,self.b

Point=Optional[tuple[Fp2,Fp2]]
@dataclass(frozen=True)
class Curve:
    p:int;a:int;b:int;d:int
    def c(self,x):return Fp2.coerce(x,self.p,self.d)
    def on_curve(self,P:Point)->bool:
        if P is None:return True
        x,y=P;return y*y==x*x*x+self.a*x+self.b
    def neg(self,P:Point)->Point:return None if P is None else (P[0],-P[1])
    def add(self,P:Point,Q:Point)->Point:
        if P is None:return Q
        if Q is None:return P
        x1,y1=P;x2,y2=Q
        if x1==x2:
            if y1+y2==0 or y1==0:return None
            m=(3*x1*x1+self.a)/(2*y1)
        else:m=(y2-y1)/(x2-x1)
        R=(m*m-x1-x2,m*(x1-(m*m-x1-x2))-y1);assert self.on_curve(R);return R
    def mul(self,k:int,P:Point)->Point:
        if k<0:return self.mul(-k,self.neg(P))
        R=None;A=P
        while k:
            if k&1:R=self.add(R,A)
            A=self.add(A,A);k//=2
        return R

def embed(E:Curve,xy:tuple[int,int])->Point:return E.c(xy[0]),E.c(xy[1])
def line_eval(E:Curve,A:Point,B:Point,Z:Point)->Fp2:
    assert Z is not None
    if A is None or B is None:return E.c(1)
    x1,y1=A;x2,y2=B;x,y=Z
    if x1==x2:
        if y1+y2==0:return x-x1
        m=(3*x1*x1+E.a)/(2*y1)
    else:m=(y2-y1)/(x2-x1)
    return y-y1-m*(x-x1)
def vertical_eval(E:Curve,P:Point,Z:Point)->Fp2:
    assert Z is not None;return E.c(1) if P is None else Z[0]-P[0]
def g_eval(E:Curve,A:Point,B:Point,Z:Point)->Fp2:return line_eval(E,A,B,Z)/vertical_eval(E,E.add(A,B),Z)
def miller(E:Curve,m:int,P:Point,Z:Point)->Fp2:
    assert m>=1 and P is not None and Z is not None
    T=P;f=E.c(1)
    for bit in bin(m)[3:]:
        f=f*f*g_eval(E,T,T,Z);T=E.add(T,T)
        if bit=='1':f=f*g_eval(E,T,P,Z);T=E.add(T,P)
    assert T==E.mul(m,P);return f
def trace_zero_shift(E:Curve)->Point:
    for x in range(E.p):
        b=sqrt_mod_brute((x**3+E.a*x+E.b)*pow(E.d,-1,E.p),E.p)
        if b not in (None,0):
            P=(E.c(x),Fp2(0,b,E.p,E.d))
            if E.on_curve(P):return P
    raise AssertionError
def shifted(E:Curve,m:int,P:Point,Q:Point,S:Point)->Fp2:return miller(E,m,P,E.add(S,Q))/miller(E,m,P,S)
def sigma(k:int,n:int)->int:return 1 if (k%n)%2==0 else -1

TOYS=((43,31,(2,12),6,5),(67,79,(2,22),29,23),(79,67,(1,18),23,29),(127,127,(1,32),19,107),(163,139,(2,34),58,96))
def environment(row):
    p,n,g,beta,lam=row;E=Curve(p,0,7,least_nonsquare(p));G=embed(E,g);S=trace_zero_shift(E);return E,n,G,S,beta,lam
def half_sequence(row):
    E,n,G,S,beta,lam=environment(row);h=(n-1)//2
    return E,n,G,S,beta,lam,h,[E.c(1)]+[shifted(E,h,G,E.mul(k,G),S) for k in range(1,n)]
