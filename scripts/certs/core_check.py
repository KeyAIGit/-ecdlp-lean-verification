#!/usr/bin/env python3
"""Numeric ground-truth for the two SCALAR CORE identities behind the secp256k1
division-polynomial doubling identities (I)/(II) — the residual of the N7 `even_x_algebra`
wall (see `notes/N7_EVEN_X_REDUCTION.md` (the reduction plan)).

Builds the REAL `normEDS b c d` sequence (Mathlib's well-founded `preNormEDS'` recurrence,
first parameter `b^4`, times the `if Even` `b`-factor) over a toy field `F_pp`, at random
`x` with a genuine square root `beta^2 = 4x^3+28`, and checks for k=0..11:

  * scaled CORE-I : (w(k-1)^2 w(k+2) - w(k-2) w(k+1)^2)^2 = 4 beta^2 (A^3 + 7 B^3)
  * CORE-II       : w(2k+1) w(2k-1) = 3A^4 + 4P A^3 + 84 A B^3 + 28 P B^3

with A = x w(k)^2 - w(k+1)w(k-1), B = w(k)^2, P = w(k+1)w(k-1).

These are exactly `coreI_scaled` (parity-free, CommRing) and `normEDS_odd_prod_eq` (CORE-II) targeted in
Lean file. Prints `... True True` iff both hold on every tested pair. Nothing here enters
Lean — the kernel remains the sole judge; this only certifies the induction TARGET is true.
"""

import random
pp = 10007

def build_w(b, c, d, N):
    B4 = pow(b,4,pp)
    pre = [0]*(N+6)
    pre[0]=0; pre[1]=1; pre[2]=1; pre[3]=c%pp; pre[4]=d%pp
    for idx in range(5, N+6):
        n = idx-5
        m = n//2
        if n % 2 == 0:  # Even n
            fac1 = B4 if (m%2==0) else 1
            fac2 = 1 if (m%2==0) else B4
            pre[idx] = (pre[m+4]*pow(pre[m+2],3,pp)*fac1 - pre[m+1]*pow(pre[m+3],3,pp)*fac2) % pp
        else:
            pre[idx] = (pow(pre[m+2],2,pp)*pre[m+3]*pre[m+5] - pre[m+1]*pre[m+3]*pow(pre[m+4],2,pp)) % pp
    def w(n):
        n=int(n)
        if n<0: return (-w(-n))%pp
        return (pre[n]*(b if n%2==0 else 1))%pp
    return w

random.seed(3)
okD=okII=True; tested=0
for trial in range(3000):
    x=random.randrange(pp)
    rhs=(4*x**3+28)%pp
    if rhs!=0 and pow(rhs,(pp-1)//2,pp)!=1: continue
    b=pow(rhs,(pp+1)//4,pp)
    if (b*b-rhs)%pp!=0: continue
    c=(3*x**4+84*x)%pp; d=(2*x**6+280*x**3-784)%pp
    w=build_w(b,c,d,60)
    for k in range(0,12):
        A=(x*w(k)**2 - w(k+1)*w(k-1))%pp
        Bv=(w(k)**2)%pp
        Pv=(w(k+1)*w(k-1))%pp
        D=(w(k-1)**2*w(k+2)-w(k-2)*w(k+1)**2)%pp
        if (D*D)%pp != (4*b*b*(A**3+7*Bv**3))%pp: okD=False; print("D FAIL",x,k)
        if (w(2*k+1)*w(2*k-1))%pp != (3*A**4+4*Pv*A**3+84*A*Bv**3+28*Pv*Bv**3)%pp: okII=False; print("II FAIL",x,k)
        tested+=1
    if tested>800: break
print("tested",tested,"scaled-CORE-I(D^2=4b^2(A^3+7B^3))",okD,"CORE-II",okII)
