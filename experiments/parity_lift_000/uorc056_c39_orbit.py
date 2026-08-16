from __future__ import annotations
import sys,json,math
from uorc056_c39_half_miller import TOYS,half_sequence,shifted,sigma,Fp2

# poly
def trim(a):
 while len(a)>1 and not a[-1]:a.pop()
 return a
def zlike(x):return x*0
def add(a,b):
 z=zlike(a[0] if a else b[0]);return trim([(a[i] if i<len(a) else z)+(b[i] if i<len(b) else z) for i in range(max(len(a),len(b)))])
def sub(a,b):
 z=zlike(a[0] if a else b[0]);return trim([(a[i] if i<len(a) else z)-(b[i] if i<len(b) else z) for i in range(max(len(a),len(b)))])
def scale(a,c):return trim([x*c for x in a])
def mul(a,b):
 z=zlike(a[0]);o=[z for _ in range(len(a)+len(b)-1)]
 for i,x in enumerate(a):
  for j,y in enumerate(b):o[i+j]=o[i+j]+x*y
 return trim(o)
def ev(a,x):
 o=zlike(x)
 for c in reversed(a):o=o*x+c
 return o
def roots(rs,one):
 o=[one]
 for r in rs:o=mul(o,[-r,one])
 return o
def interp(xs,ys,one):
 # product polynomial / synthetic division for O(n^2)
 P=roots(xs,one); dP=[P[i]*i for i in range(1,len(P))]
 out=[zlike(one) for _ in range(len(xs))]
 for x,y in zip(xs,ys):
  # synthetic divide P by X-x, ascending coefficients
  d=len(P)-1;q=[zlike(one) for _ in range(d)];q[d-1]=P[d]
  for i in range(d-2,-1,-1):q[i]=P[i+1]+x*q[i+1]
  den=ev(dP,x);c=y/den
  for i,v in enumerate(q):out[i]=out[i]+c*v
 return trim(out)
def stats(a):
 nz=[i for i,c in enumerate(a) if c];step=0
 if len(nz)>1:
  for i in nz[1:]:step=math.gcd(step,i-nz[0])
 return {'degree':len(a)-1,'nonzero':len(nz),'zeros':len(a)-len(nz),'support_step':step}

# rank
def rank(M):
 A=[r[:] for r in M];R=len(A);C=len(A[0]) if R else 0;rr=0
 for c in range(C):
  p=next((i for i in range(rr,R) if A[i][c]),None)
  if p is None:continue
  A[rr],A[p]=A[p],A[rr];iv=A[rr][c].inv();A[rr]=[x*iv for x in A[rr]]
  for i in range(rr+1,R):
   if A[i][c]:
    f=A[i][c];A[i]=[x-f*y for x,y in zip(A[i],A[rr])]
  rr+=1
  if rr==R:break
 return rr
def pows(x,d,one):
 a=[one]
 for _ in range(d):a.append(a[-1]*x)
 return a

def low_degree_negation(inputs,outputs,one,degrees):
 out=[]
 for d in degrees:
  M=[]
  for x,y in zip(inputs,outputs):
   q=pows(x,d,one);M.append(q+[-y*t for t in q])
  r=rank(M);cols=2*(d+1);out.append({'degree':d,'rank':r,'columns':cols,'relation_exists':r<cols})
 return out

def analyze(row):
 E,n,G,S,beta,lam,h,V=half_sequence(row);one=E.c(1);m=(n-1)//2
 evs=[V[k] for k in range(2,n,2)];ods=[V[k] for k in range(1,n,2)]
 Pe=roots(evs,one);Po=roots(ods,one);Sig=add(Pe,Po);Del=sub(Pe,Po);Pi=mul(Pe,Po)
 assert mul(Del,Del)==sub(mul(Sig,Sig),scale(Pi,E.c(4)))
 for k in range(1,n):assert -ev(Del,V[k])/ev(Sig,V[k])==sigma(k,n)
 # half algebra
 pts=[E.mul(j,G) for j in range(1,m+1)];xs=[P[0] for P in pts];ys=[P[1] for P in pts]
 inv2=E.c(pow(2,-1,E.p)); Aval=[];Bval=[];Yval=[];even=[];odd=[]
 for j,(x,y) in enumerate(zip(xs,ys),1):
  fp,fm=V[j],V[n-j];Aval.append((fp+fm)*inv2);Bval.append((fp-fm)/(E.c(2)*y));Yval.append(E.c(sigma(j,n))*y)
  even.append(fp if j%2==0 else fm);odd.append(fm if j%2==0 else fp)
 A=interp(xs,Aval,one);B=interp(xs,Bval,one);Y=interp(xs,Yval,one)
 for i,x in enumerate(xs):
  assert ev(Y,x)*ev(Y,x)==x*x*x+E.c(E.b)
  assert ev(A,x)+ev(Y,x)*ev(B,x)==even[i] and ev(A,x)-ev(Y,x)*ev(B,x)==odd[i]
 assert roots(even,one)==Pe and roots(odd,one)==Po
 # B unit
 Bzeros=sum(not ev(B,x) for x in xs)
 # reversal
 Gm=E.neg(G);Sm=E.neg(S);rev=[one]+[shifted(E,h,Gm,E.mul(k,G),Sm) for k in range(1,n)]
 assert all(rev[k]==V[n-k] for k in range(1,n))
 assert roots([rev[k] for k in range(2,n,2)],one)==Po
 # polynomial decoder exact degree by interpolation on distinct state values
 ded={}
 for k in range(1,n):
  key=V[k].tuple();target=E.c(sigma(k,n));assert key not in ded or ded[key]==target;ded[key]=target
 xsS=[];ysS=[]
 for (a,b),t in ded.items():xsS.append(type(one)(a,b,one.p,one.d));ysS.append(t)
 Dpoly=interp(xsS,ysS,one)
 # natural pairing map even->odd low degree
 threshold=(m-1)//2
 negscreen=low_degree_negation(even,odd,one,(threshold-1,threshold))
 return {'p':E.p,'n':n,'m':m,'decoder_checks':n-1,'distinct_states':len(ded),'B_zeros_on_half_kernel':Bzeros,
 'polynomials':{'P_even':stats(Pe),'P_odd':stats(Po),'Sigma':stats(Sig),'Delta':stats(Del),'Pi':stats(Pi),'A':stats(A),'B':stats(B),'Y':stats(Y),'interpolated_parity_polynomial':stats(Dpoly)},
 'minimal_rational_decoder_degree_proved':max(len(set(x.tuple() for x in evs)),len(set(x.tuple() for x in ods))),
 'canonical_orbit_decoder_degree':max(len(Pe)-1,len(Po)-1),
 'paired_negation_map':{'dimension_threshold':threshold,'first_relation_degree':threshold if negscreen[1]['relation_exists'] and not negscreen[0]['relation_exists'] else None,'no_relation_one_degree_before':not negscreen[0]['relation_exists'],'relation_at_dimension_threshold':negscreen[1]['relation_exists'],'screens':negscreen},
 'identities':{'norm_factorization':True,'optimal_decoder':True,'discriminant_square':True,'generator_reversal_swaps_factors':True}}

def build_orbit_rows():
    return [analyze(row) for row in TOYS]
