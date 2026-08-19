from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Iterable

Point = Optional[tuple[int, int]]


@dataclass(frozen=True)
class Curve:
    p: int
    a: int = 0
    b: int = 7

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, P: Point) -> Point:
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P: Point, Q: Point) -> Point:
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            if y1 % p == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def mul(self, k: int, P: Point, order: int | None = None) -> Point:
        if order is not None:
            k %= order
        if k < 0:
            return self.mul(-k, self.neg(P), order)
        out = None
        addend = P
        while k:
            if k & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return out


@dataclass(frozen=True)
class Dual:
    """Value and first partials with respect to x,a,b over F_p."""
    v: int
    dx: int
    da: int
    db: int
    p: int

    @classmethod
    def const(cls, v: int, p: int) -> "Dual":
        return cls(v % p, 0, 0, 0, p)

    def _coerce(self, other: int | "Dual") -> "Dual":
        if isinstance(other, Dual):
            if other.p != self.p:
                raise ValueError("field mismatch")
            return other
        return Dual.const(int(other), self.p)

    def __add__(self, other):
        o = self._coerce(other)
        p = self.p
        return Dual((self.v + o.v) % p, (self.dx + o.dx) % p,
                    (self.da + o.da) % p, (self.db + o.db) % p, p)

    __radd__ = __add__

    def __neg__(self):
        p = self.p
        return Dual(-self.v % p, -self.dx % p, -self.da % p, -self.db % p, p)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        o = self._coerce(other)
        p = self.p
        return Dual(
            self.v * o.v % p,
            (self.dx * o.v + self.v * o.dx) % p,
            (self.da * o.v + self.v * o.da) % p,
            (self.db * o.v + self.v * o.db) % p,
            p,
        )

    __rmul__ = __mul__

    def inverse(self):
        if self.v == 0:
            raise ZeroDivisionError("dual unit has zero value")
        p = self.p
        inv = pow(self.v, -1, p)
        inv2 = inv * inv % p
        return Dual(inv, -self.dx * inv2 % p, -self.da * inv2 % p,
                    -self.db * inv2 % p, p)

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()

    def __pow__(self, exponent: int):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Dual.const(1, self.p)
        base = self
        e = exponent
        while e:
            if e & 1:
                result = result * base
            base = base * base
            e >>= 1
        return result


class DivisionDual:
    """Division-polynomial value and x/a/b partials at one affine point."""

    def __init__(self, curve: Curve, point: tuple[int, int]):
        p = curve.p
        x0, y0 = point
        if y0 % p == 0:
            raise ValueError("2-torsion chart not supported")
        self.p = p
        self.curve = curve
        inv2y = pow(2 * y0, -1, p)
        x = Dual(x0, 1, 0, 0, p)
        a = Dual(curve.a, 0, 1, 0, p)
        b = Dual(curve.b, 0, 0, 1, p)
        y = Dual(
            y0,
            (3 * x0 * x0 + curve.a) * inv2y % p,
            x0 * inv2y % p,
            inv2y,
            p,
        )
        self.x, self.a, self.b, self.y = x, a, b, y
        self.inv_2y = (2 * y).inverse()
        self.cache: dict[int, Dual] = {
            0: Dual.const(0, p),
            1: Dual.const(1, p),
            2: 2 * y,
        }
        self.cache[3] = 3*x**4 + 6*a*x**2 + 12*b*x - a**2
        self.cache[4] = 4*y*(x**6 + 5*a*x**4 + 20*b*x**3
                             - 5*a**2*x**2 - 4*a*b*x - 8*b**2 - a**3)

    def psi(self, index: int) -> Dual:
        if index < 0:
            return -self.psi(-index)
        if index in self.cache:
            return self.cache[index]
        if index & 1:
            m = (index - 1)//2
            value = self.psi(m+2)*self.psi(m)**3 - self.psi(m-1)*self.psi(m+1)**3
        else:
            m = index//2
            value = self.psi(m)*self.inv_2y*(
                self.psi(m+2)*self.psi(m-1)**2
                - self.psi(m-2)*self.psi(m+1)**2
            )
        self.cache[index] = value
        return value


@lru_cache(maxsize=None)
def torsion_tangents(curve: Curve, n: int, P: tuple[int, int]):
    """Return a- and b-direction torsion lift tangents (dx,dy)."""
    p = curve.p
    d = DivisionDual(curve, P).psi(n)
    if d.v % p != 0:
        raise AssertionError("point is not n-torsion")
    if d.dx % p == 0:
        raise ZeroDivisionError("inseparable torsion root")
    inv_dx = pow(d.dx, -1, p)
    x, y = P
    ua = -d.da * inv_dx % p
    ub = -d.db * inv_dx % p
    inv2y = pow(2*y, -1, p)
    va = ((3*x*x + curve.a)*ua + x) * inv2y % p
    vb = ((3*x*x + curve.a)*ub + 1) * inv2y % p
    return (ua, va), (ub, vb), d


def chi(v: int, p: int) -> int:
    v %= p
    if v == 0:
        return 0
    z = pow(v, (p-1)//2, p)
    return 1 if z == 1 else -1


def state(curve: Curve, n: int, G: tuple[int,int], P: tuple[int,int]):
    p = curve.p
    (ua, va), (ub, vb), _ = torsion_tangents(curve, n, P)
    (uag, vag), (ubg, vbg), _ = torsion_tangents(curve, n, G)
    x,y=P; xg,yg=G
    omega_a = ua * pow(2*y,-1,p) % p
    omega_b = ub * pow(2*y,-1,p) % p
    omega_ag = uag * pow(2*yg,-1,p) % p
    omega_bg = ubg * pow(2*yg,-1,p) % p
    if 0 in (omega_ag, omega_bg):
        raise ZeroDivisionError("anchor tangent chart singular")
    A = omega_a * pow(omega_ag,-1,p) % p
    B = omega_b * pow(omega_bg,-1,p) % p
    T = x**3 % p
    R = x*ua % p
    S = x*x*va*pow(y,-1,p) % p
    N = A*B % p
    return {
        "P":P,"x":x,"y":y,"ua":ua,"va":va,"ub":ub,"vb":vb,
        "A":A,"B":B,"N":N,"T":T,"R":R,"S":S,
        "omega_a":omega_a,"omega_b":omega_b,
        "omega_ag":omega_ag,"omega_bg":omega_bg,
    }


def tangent_add(
    curve: Curve,
    P: tuple[int, int],
    Q: tuple[int, int],
    tangent_P: tuple[int, int],
    tangent_Q: tuple[int, int],
    da: int,
    db: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Differentiate the affine group law along one public curve deformation."""
    p = curve.p
    x1, y1 = P
    x2, y2 = Q
    u1, v1 = tangent_P
    u2, v2 = tangent_Q
    if x1 == x2 and (y1 + y2) % p == 0:
        raise ZeroDivisionError("tangent addition reaches the identity")
    if P == Q:
        if y1 % p == 0:
            raise ZeroDivisionError("doubling a 2-torsion point")
        numerator = (3 * x1 * x1 + curve.a) % p
        denominator = (2 * y1) % p
        slope = numerator * pow(denominator, -1, p) % p
        d_numerator = (6 * x1 * u1 + da) % p
        d_denominator = (2 * v1) % p
        d_slope = (
            (d_numerator * denominator - numerator * d_denominator)
            * pow(denominator * denominator % p, -1, p)
        ) % p
    else:
        denominator = (x2 - x1) % p
        numerator = (y2 - y1) % p
        slope = numerator * pow(denominator, -1, p) % p
        d_numerator = (v2 - v1) % p
        d_denominator = (u2 - u1) % p
        d_slope = (
            (d_numerator * denominator - numerator * d_denominator)
            * pow(denominator * denominator % p, -1, p)
        ) % p
    x3 = (slope * slope - x1 - x2) % p
    u3 = (2 * slope * d_slope - u1 - u2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    v3 = (d_slope * (x1 - x3) + slope * (u1 - u3) - v1) % p
    R = (x3, y3)
    if not curve.on_curve(R):
        raise AssertionError("differentiated group law left the curve")
    if (
        2 * y3 * v3
        - (3 * x3 * x3 + curve.a) * u3
        - da * x3
        - db
    ) % p:
        raise AssertionError("output tangent violates the linearized curve equation")
    return R, (u3, v3)


def omega_from_tangent(P: tuple[int, int], tangent: tuple[int, int], p: int) -> int:
    return tangent[0] * pow(2 * P[1], -1, p) % p


def t_double(T: int, p: int) -> int:
    return T * pow(T-56,3,p) * pow(64*pow(T+7,3,p)%p,-1,p) % p


def r_double(T: int, R: int, p: int) -> int:
    D=(T*T+140*T-392)%p
    num=(T-56)*(R*D - 3*T*T + 42*T)
    den=16*pow(T+7,3,p)
    return num%p * pow(den%p,-1,p)%p


def b_transfer_double(T: int, p: int) -> int:
    D=(T*T+140*T-392)%p
    return 2*(T-56)*(T+7)%p * pow(D,-1,p)%p


def a_transfer_double(T: int, R: int, p: int) -> int:
    D=(T*T+140*T-392)%p
    return 2*(R*D - 3*T*T + 42*T)%p * pow((R*D)%p,-1,p)%p


def endpoint_e(P: tuple[int,int], p: int) -> int:
    x,y=P
    if x%p==0 or y%p==0:
        raise ZeroDivisionError("endpoint x/y chart singular")
    return x*pow(y,-1,p)%p


def B_direct(G: tuple[int,int], P: tuple[int,int], p: int) -> int:
    return endpoint_e(P,p)*pow(endpoint_e(G,p),-1,p)%p


def addition_cocycle_B(curve: Curve, G: tuple[int,int], P: tuple[int,int], Q: tuple[int,int]) -> int:
    R=curve.add(P,Q)
    if R is None:
        raise ZeroDivisionError("sum at identity")
    p=curve.p
    return endpoint_e(G,p)*endpoint_e(R,p)%p*pow(endpoint_e(P,p)*endpoint_e(Q,p)%p,-1,p)%p


def addition_cocycle_N(curve: Curve, n:int, G:tuple[int,int], P:tuple[int,int], Q:tuple[int,int]) -> int:
    Rpt=curve.add(P,Q)
    if Rpt is None:
        raise ZeroDivisionError("sum at identity")
    sG=state(curve,n,G,G); sP=state(curve,n,G,P); sQ=state(curve,n,G,Q); sR=state(curve,n,G,Rpt)
    p=curve.p
    return sR["N"]*pow(sP["N"]*sQ["N"]%p,-1,p)%p


def multiplier_cocycle(values: dict[int,int], m:int, k:int, n:int, p:int) -> int:
    target=(m*k)%n
    if target==0:
        raise ZeroDivisionError("multiplier hits identity")
    return values[target]*pow(pow(values[k],m,p),-1,p)%p


def point_count(curve: Curve) -> int:
    total=1
    for x in range(curve.p):
        rhs=(x**3+curve.a*x+curve.b)%curve.p
        s=chi(rhs,curve.p)
        total += 1 if s==0 else 2 if s==1 else 0
    return total


def is_prime(n:int)->bool:
    if n<2:return False
    small=(2,3,5,7,11,13,17,19,23,29,31,37)
    for q in small:
        if n%q==0:return n==q
    d=n-1;s=0
    while d%2==0:s+=1;d//=2
    for a in (2,3,5,7,11):
        if a>=n:continue
        x=pow(a,d,n)
        if x in (1,n-1):continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1:break
        else:return False
    return True


def find_beta(p:int)->int:
    for g in range(2,p):
        beta=pow(g,(p-1)//3,p)
        if beta not in (0,1) and pow(beta,3,p)==1:
            return beta
    raise ValueError("no cube root")


def find_point(curve:Curve)->tuple[int,int]:
    for x in range(1,curve.p):
        rhs=(x**3+curve.b)%curve.p
        for y in range(1,curve.p):
            if y*y%curve.p==rhs:
                return x,y
    raise ValueError("no point")


def find_lambda(curve:Curve,n:int,G:tuple[int,int],beta:int)->int:
    target=(beta*G[0]%curve.p,G[1])
    P=None
    for k in range(n):
        if P==target:
            return k
        P=curve.add(P,G)
    raise ValueError("lambda not found")


def generate_rows(start:int, stop:int, count:int)->list[tuple[int,int,tuple[int,int],int,int]]:
    out=[]
    for p in range(start,stop+1):
        if len(out)>=count:break
        if p%3!=1 or not is_prime(p):continue
        E=Curve(p)
        n=point_count(E)
        if n==p or not is_prime(n):continue
        G=find_point(E)
        if E.mul(n,G) is not None:continue
        beta=find_beta(p)
        lam=find_lambda(E,n,G,beta)
        if lam in (0,1) or (lam*lam+lam+1)%n:continue
        out.append((p,n,G,beta,lam))
    return out


def poly_from_roots(roots:list[int],p:int)->list[int]:
    out=[1]
    for r in roots:
        nxt=[0]*(len(out)+1)
        for i,c in enumerate(out):
            nxt[i]=(nxt[i]-r*c)%p
            nxt[i+1]=(nxt[i+1]+c)%p
        out=nxt
    return out


def berlekamp_massey(sequence:list[int],p:int)->int:
    C=[1]; B=[1]; L=0; m=1; b=1
    for N in range(len(sequence)):
        d=sequence[N]%p
        for i in range(1,L+1):
            if i<len(C): d=(d+C[i]*sequence[N-i])%p
        if d==0:
            m+=1; continue
        coef=d*pow(b,-1,p)%p
        T=C[:]
        need=len(B)+m
        if len(C)<need:C += [0]*(need-len(C))
        for i,v in enumerate(B):
            C[i+m]=(C[i+m]-coef*v)%p
        if 2*L<=N:
            L=N+1-L; B=T; b=d; m=1
        else:
            m+=1
    return L
