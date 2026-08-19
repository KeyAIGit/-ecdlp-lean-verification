from __future__ import annotations
from dataclasses import dataclass
from uorc056_c52_deformation_core import Curve

class Series:
    __slots__=("c","p","L")
    def __init__(self,coeffs,p,L):
        z=list(coeffs)+[0]*L;self.c=tuple(v%p for v in z[:L]);self.p=p;self.L=L
    @classmethod
    def const(cls,v,p,L):return cls([v],p,L)
    def coerce(self,o):
        if isinstance(o,Series):
            if (o.p,o.L)!=(self.p,self.L):raise ValueError
            return o
        return Series.const(o,self.p,self.L)
    def __add__(self,o):o=self.coerce(o);return Series([a+b for a,b in zip(self.c,o.c)],self.p,self.L)
    __radd__=__add__
    def __neg__(self):return Series([-a for a in self.c],self.p,self.L)
    def __sub__(self,o):return self+(-self.coerce(o))
    def __rsub__(self,o):return self.coerce(o)-self
    def __mul__(self,o):
        o=self.coerce(o);r=[0]*self.L;p=self.p
        for i,a in enumerate(self.c):
            if not a:continue
            for j,b in enumerate(o.c[:self.L-i]):
                if b:r[i+j]=(r[i+j]+a*b)%p
        return Series(r,p,self.L)
    __rmul__=__mul__
    def inv(self):
        if not self.c[0]:raise ZeroDivisionError
        p=self.p;r=[0]*self.L;r[0]=pow(self.c[0],-1,p)
        for m in range(1,self.L):r[m]=(-r[0]*sum(self.c[i]*r[m-i] for i in range(1,m+1)))%p
        return Series(r,p,self.L)
    def __truediv__(self,o):return self*self.coerce(o).inv()
    def __rtruediv__(self,o):return self.coerce(o)*self.inv()
    def __pow__(self,e):
        if e<0:return self.inv()**(-e)
        r=Series.const(1,self.p,self.L);b=self
        while e:
            if e&1:r=r*b
            b=b*b;e//=2
        return r
    def der(self):return Series([(i+1)*self.c[i+1] for i in range(self.L-1)],self.p,self.L)

@dataclass(frozen=True)
class DualSeries:
    f:Series;e:Series
    def coerce(self,o):
        if isinstance(o,DualSeries):return o
        return DualSeries(self.f.coerce(o),Series.const(0,self.f.p,self.f.L))
    def __add__(self,o):o=self.coerce(o);return DualSeries(self.f+o.f,self.e+o.e)
    __radd__=__add__
    def __neg__(self):return DualSeries(-self.f,-self.e)
    def __sub__(self,o):return self+(-self.coerce(o))
    def __rsub__(self,o):return self.coerce(o)-self
    def __mul__(self,o):o=self.coerce(o);return DualSeries(self.f*o.f,self.f*o.e+self.e*o.f)
    __rmul__=__mul__
    def inv(self):q=self.f.inv();return DualSeries(q,-self.e*q*q)
    def __truediv__(self,o):return self*self.coerce(o).inv()
    def __rtruediv__(self,o):return self.coerce(o)*self.inv()
    def __pow__(self,e):
        if e<0:return self.inv()**(-e)
        r=self.coerce(1);b=self
        while e:
            if e&1:r=r*b
            b=b*b;e//=2
        return r

def sqrt_series(rhs,y0):
    p,L=rhs.p,rhs.L;r=[0]*L;r[0]=y0%p;i2=pow(2*y0,-1,p)
    for m in range(1,L):r[m]=((rhs.c[m]-sum(r[i]*r[m-i] for i in range(1,m)))*i2)%p
    return Series(r,p,L)

class DivisionDualSeries:
    def __init__(self,E:Curve,P,L=7):
        p=E.p;x0,y0=P;zero=Series.const(0,p,L);xb=Series([x0,1],p,L)
        self.x=DualSeries(xb,zero);self.a=DualSeries(Series.const(E.a,p,L),Series.const(1,p,L));self.b=DualSeries(Series.const(E.b,p,L),zero)
        yb=sqrt_series(xb**3+E.a*xb+E.b,y0);ye=xb/(2*yb);self.y=DualSeries(yb,ye);self.i2y=(2*self.y).inv()
        x,a,b,y=self.x,self.a,self.b,self.y;self.cache={0:self.c(0),1:self.c(1),2:2*y}
        self.cache[3]=3*x**4+6*a*x**2+12*b*x-a**2
        self.cache[4]=4*y*(x**6+5*a*x**4+20*b*x**3-5*a**2*x**2-4*a*b*x-8*b**2-a**3)
    def c(self,v):return DualSeries(Series.const(v,self.x.f.p,self.x.f.L),Series.const(0,self.x.f.p,self.x.f.L))
    def psi(self,n):
        if n<0:return -self.psi(-n)
        if n in self.cache:return self.cache[n]
        if n&1:
            m=(n-1)//2;v=self.psi(m+2)*self.psi(m)**3-self.psi(m-1)*self.psi(m+1)**3
        else:
            m=n//2;v=self.psi(m)*self.i2y*(self.psi(m+2)*self.psi(m-1)**2-self.psi(m-2)*self.psi(m+1)**2)
        self.cache[n]=v;return v

def moduli_covariant_derivatives(E:Curve,n:int,P,L=7):
    lab=DivisionDualSeries(E,P,L);f=lab.psi(n)
    if f.f.c[0] or not f.f.c[1]:raise AssertionError('torsion series')
    ua=-f.e/f.f.der();R=lab.x.f*ua
    values=[];current=R
    for _ in range(4):
        values.append(current.c[0]);current=2*lab.y.f*current.der()
    return tuple(values),ua.c[0]


def connection_defect(connection_at_query: int, scalar: int, connection_at_anchor: int, prime: int) -> int:
    """Scalar model of Delta_k^nabla(G)."""
    return (connection_at_query - scalar * connection_at_anchor) % prime


def gauge_changed_defect(
    old_defect: int,
    gauge_at_query: int,
    scalar: int,
    gauge_at_anchor: int,
    prime: int,
) -> int:
    return (old_defect + gauge_at_query - scalar * gauge_at_anchor) % prime


def recover_scalar_from_known_defect(
    connection_at_query: int,
    defect: int,
    connection_at_anchor: int,
    prime: int,
) -> int:
    if connection_at_anchor % prime == 0:
        raise ZeroDivisionError("anchor connection scalar is zero")
    return (
        (connection_at_query - defect)
        * pow(connection_at_anchor, -1, prime)
    ) % prime
