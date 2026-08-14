#!/usr/bin/env python3
"""Exact C17 replay for odd GLV trace/norm invariant circuits.

The extension corpus is generated before screening by a public arithmetic rule.
No external point, unknown scalar, wallet, private key, or production target is
accepted.
"""
from __future__ import annotations

import json
import pathlib



def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def curve_order(p: int) -> int:
    total = 1
    for x in range(p):
        rhs = (x * x * x + 7) % p
        if rhs == 0:
            total += 1
        else:
            symbol = pow(rhs, (p - 1) // 2, p)
            total += 2 if symbol == 1 else 0
    return total


def first_affine_point(p: int):
    for x in range(p):
        rhs = (x * x * x + 7) % p
        for y in range(p):
            if y * y % p == rhs:
                return x, y
    raise AssertionError("curve has no affine point")


def public_extension_corpus(limit: int = 7):
    cases = []
    p = 7
    while len(cases) < limit:
        if is_prime(p) and p % 3 == 1:
            n = curve_order(p)
            if is_prime(n) and n % 3 == 1 and n > 7:
                G = first_affine_point(p)
                beta = next(x for x in range(2, p) if (x * x + x + 1) % p == 0)
                context = RFContext(p, G, beta)
                points = context.points(n)
                target = (beta * G[0] % p, G[1])
                lam = points.index(target)
                if (lam * lam + lam + 1) % n:
                    raise AssertionError("GLV eigenvalue certificate failed")
                cases.append((p, n, G, beta, lam))
        p += 1
    return cases


def gauge_vector(n: int) -> list[int]:
    m = (n - 1) // 2
    primitive = [
        -1 if (k & 1 and 1 <= k <= m)
        else 1 if (not (k & 1) and m < k < n)
        else 0
        for k in range(n)
    ]
    if n % 4 == 3:
        r = (n + 1) // 4
        class_index = r * (2 * r - 1) % n
    else:
        r = (n - 1) // 4
        class_index = r * (2 * r + 1) % n
    gauge = primitive[:]
    gauge[class_index] -= 1
    gauge[0] += 1
    if sum(gauge) or sum(k * gauge[k] for k in range(n)) % n:
        raise AssertionError("gauge divisor is not principal")
    return gauge


def parity_orbit_counts(n: int, lam: int) -> list[int]:
    visited = {0}
    counts = [0, 0, 0, 0]
    for k in range(1, n):
        if k in visited:
            continue
        orbit = [k, lam * k % n, lam * lam * k % n]
        visited.update(orbit)
        counts[sum(index % 2 == 0 for index in orbit)] += 1
    if counts[0] != counts[3] or counts[1] != counts[2]:
        raise AssertionError("negation pairing failed")
    return counts

class RFContext:
 def __init__(self,p,G,beta):
  self.p=p;self.G=G;self.beta=beta;self.F=[7,0,0,1]
 def tr(self,P):
  p=self.p;P=[x%p for x in P]
  while len(P)>1 and P[-1]==0:P.pop()
  return P
 def addp(self,P,Q):
  p=self.p;m=max(len(P),len(Q));R=[0]*m
  for i in range(m):R[i]=((P[i] if i<len(P) else 0)+(Q[i] if i<len(Q) else 0))%p
  return self.tr(R)
 def negp(self,P):return self.tr([-x for x in P])
 def subp(self,P,Q):return self.addp(P,self.negp(Q))
 def sc(self,P,c):return self.tr([c*x for x in P])
 def mulp(self,P,Q):
  p=self.p;R=[0]*(len(P)+len(Q)-1)
  for i,x in enumerate(P):
   for j,y in enumerate(Q):R[i+j]=(R[i+j]+x*y)%p
  return self.tr(R)
 def divmodp(self,N,D):
  p=self.p;N=self.tr(N);D=self.tr(D)
  if D==[0]:raise ZeroDivisionError
  if len(N)<len(D):return [0],N
  Q=[0]*(len(N)-len(D)+1);R=N[:]; inv=pow(D[-1],-1,p)
  while R!=[0] and len(R)>=len(D):
   k=len(R)-len(D); c=R[-1]*inv%p;Q[k]=c
   for i,d in enumerate(D):R[i+k]=(R[i+k]-c*d)%p
   R=self.tr(R)
  return self.tr(Q),R
 def exactdiv(self,N,D):
  q,r=self.divmodp(N,D)
  if r!=[0]:raise ValueError('not exact')
  return q
 def gcd(self,P,Q):
  p=self.p;P,Q=self.tr(P),self.tr(Q)
  if P==[0]:
   if Q==[0]:return [1]
   return self.sc(Q,pow(Q[-1],-1,p))
  if Q==[0]:return self.sc(P,pow(P[-1],-1,p))
  while Q!=[0]:
   _,r=self.divmodp(P,Q);P,Q=Q,r
  return self.sc(P,pow(P[-1],-1,p))
 def ev(self,P,x):
  p=self.p;s=0
  for c in reversed(P):s=(s*x+c)%p
  return s
 def subst_beta(self,P):
  p=self.p;beta=self.beta
  return self.tr([c*pow(beta,i,p) for i,c in enumerate(P)])
 def rf_norm(self,r):
  p=self.p;A,B,D=r;g=self.gcd(self.gcd(A,B),D)
  if g!=[1]:A=self.exactdiv(A,g);B=self.exactdiv(B,g);D=self.exactdiv(D,g)
  inv=pow(D[-1],-1,p)
  return self.tr(self.sc(A,inv)),self.tr(self.sc(B,inv)),self.tr(self.sc(D,inv))
 def rf_mul(self,r,s):
  A,B,D=r;C,E,H=s
  return self.rf_norm((self.addp(self.mulp(A,C),self.mulp(self.F,self.mulp(B,E))),self.addp(self.mulp(A,E),self.mulp(B,C)),self.mulp(D,H)))
 def rf_inv(self,r):
  A,B,D=r;den=self.subp(self.mulp(A,A),self.mulp(self.F,self.mulp(B,B)))
  return self.rf_norm((self.mulp(D,A),self.negp(self.mulp(D,B)),den))
 def rf_div(self,r,s):return self.rf_mul(r,self.rf_inv(s))
 def rf_add(self,r,s):
  A,B,D=r;C,E,H=s
  return self.rf_norm((self.addp(self.mulp(A,H),self.mulp(C,D)),self.addp(self.mulp(B,H),self.mulp(E,D)),self.mulp(D,H)))
 def rf_scale(self,r,c):
  A,B,D=r; return self.rf_norm((self.sc(A,c),self.sc(B,c),D))
 def rf_phi(self,r):
  A,B,D=r;return self.rf_norm((self.subst_beta(A),self.subst_beta(B),self.subst_beta(D)))
 def ec_add(self,P,Q):
  p=self.p
  if P is None:return Q
  if Q is None:return P
  x1,y1=P;x2,y2=Q
  if x1==x2 and (y1+y2)%p==0:return None
  if P==Q:s=(3*x1*x1)*pow(2*y1,-1,p)%p
  else:s=(y2-y1)*pow(x2-x1,-1,p)%p
  x3=(s*s-x1-x2)%p;y3=(s*(x1-x3)-y1)%p
  return x3,y3
 def points(self,n):
  out=[None];R=None
  for _ in range(1,n):R=self.ec_add(R,self.G);out.append(R)
  assert self.ec_add(R,self.G) is None
  return out
 def lineq(self,A,B):
  p=self.p
  if A is None or B is None:return ([1],[0],[1])
  x1,y1=A;x2,y2=B
  if x1==x2 and (y1+y2)%p==0:return ([-x1,1],[0],[1])
  s=(3*x1*x1)*pow(2*y1,-1,p)%p if A==B else (y2-y1)*pow(x2-x1,-1,p)%p
  L=[(s*x1-y1)%p,(-s)%p];S=self.ec_add(A,B)
  return self.rf_norm((L,[1],[1] if S is None else [-S[0],1]))
 def list_miller(self,points):
  r=([1],[0],[1]);total=None
  for P in points:r=self.rf_mul(r,self.lineq(total,P));total=self.ec_add(total,P)
  return r
 def principal(self,pos,neg):return self.rf_div(self.list_miller(pos),self.list_miller(neg))
 def series_val(self,r,P,K=10):
  p=self.p
  if P is None:return None
  def sadd(u,v):return [(u[i]+v[i])%p for i in range(K)]
  def smul(u,v):
   w=[0]*K
   for i,x in enumerate(u):
    for j,y in enumerate(v):
     if i+j<K:w[i+j]=(w[i+j]+x*y)%p
   return w
  def peval(poly,xs):
   q=[0]*K
   for c in reversed(poly):q=smul(q,xs);q[0]=(q[0]+c)%p
   return q
  x0,y0=P;xs=[x0,1]+[0]*(K-2);rhs=peval(self.F,xs);ys=[0]*K;ys[0]=y0;inv=pow(2*y0,-1,p)
  for d in range(1,K):ys[d]=(rhs[d]-sum(ys[i]*ys[d-i] for i in range(1,d))) * inv % p
  A,B,D=r;num=sadd(peval(A,xs),smul(ys,peval(B,xs)));den=peval(D,xs)
  def val(v):
   for i,x in enumerate(v):
    if x:return i
   return K
  return val(num)-val(den)
 def series_laurent(self,r,P,K=18):
  p=self.p
  if P is None:return {}
  def sadd(u,v):return [(u[i]+v[i])%p for i in range(K)]
  def smul(u,v):
   w=[0]*K
   for i,x in enumerate(u):
    for j,y in enumerate(v):
     if i+j<K:w[i+j]=(w[i+j]+x*y)%p
   return w
  def peval(poly,xs):
   q=[0]*K
   for c in reversed(poly):q=smul(q,xs);q[0]=(q[0]+c)%p
   return q
  def first(v):
   for i,x in enumerate(v):
    if x:return i
   return K
  x0,y0=P;xs=[x0,1]+[0]*(K-2);rhs=peval(self.F,xs);ys=[0]*K;ys[0]=y0;inv2=pow(2*y0,-1,p)
  for d in range(1,K):ys[d]=(rhs[d]-sum(ys[i]*ys[d-i] for i in range(1,d))) * inv2 % p
  A,B,D=r;num=sadd(peval(A,xs),smul(ys,peval(B,xs)));den=peval(D,xs)
  vn,vd=first(num),first(den)
  if vn==K:return {}
  if vd==K:raise AssertionError('denominator series vanished to truncation')
  nu=num[vn:]+[0]*vn;du=den[vd:]+[0]*vd
  q=[0]*K; q[0]=nu[0]*pow(du[0],-1,p)%p
  for d in range(1,K):
   q[d]=(nu[d]-sum(du[i]*q[d-i] for i in range(1,d+1))) * pow(du[0],-1,p) % p
  base=vn-vd
  return {base+i:c for i,c in enumerate(q) if c}

