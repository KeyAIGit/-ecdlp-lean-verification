# UORC-056 all-residue large-order barrier V11

Date: 2026-08-14

Status: **the pure single-division-polynomial quadratic-character route is closed for secp256k1.** Small exact even decimations from V10 remain valid; V11 shows that the re-marked all-residue generator required by such a decimation cannot exist at the secp256k1 order.

Central target remains unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

This is a scoped closure of one representation family, not a solution of UORC-056.

## 1. Input from V10

Let `H=<G>` have odd prime order `n`, let `m` be even with `n` not dividing `m`, and put `P=[m]G`. The division-polynomial chain rule gives the exact equivalence

```text
chi(psi_m([k]G))=(-1)^k for all 1<=k<n
```

if and only if

```text
rho_m(G)=chi(psi_m(G))=-1
```

and

```text
chi(psi_k(P))=+1 for all 1<=k<n.       (V11.1)
```

Thus it suffices to rule out an all-residue nonzero EDS row for a generator `P` of the secp256k1 subgroup.

## 2. A fixed low-degree probe

Assume `(V11.1)`. Set

```text
N=floor((n-1)/3).
```

For every `1<=k<=N`, both `k` and `3k` lie in `1,...,n-1`. The chain rule at the fixed index `3` is

```text
psi_(3k)(P)=psi_3([k]P) * psi_k(P)^9.
```

Taking quadratic characters and using the all-residue hypothesis gives

```text
chi(psi_3([k]P))=+1,
1<=k<=N.                                      (V11.2)
```

The key point is that the function is now the fixed degree-four function `psi_3`; its degree does not grow with `n`.

## 3. Explicit subgroup character-sum bound

Shparlinski--Stange Lemma 5 states that for a subgroup `H` of an elliptic curve over `F_q`, a group character `omega`, and a multiplicative character `eta`,

```text
|sum_(Q in H)^* omega(Q) eta(f(Q))| <= 2 d sqrt(q),
```

when `f` has degree `d` and is not a prohibited nontrivial power.

Take

```text
q=p,
f=psi_3,
eta=chi.
```

The degree of `psi_3` as an elliptic function is

```text
d=(3^2-1)/2=4.
```

Because `p!=3`, multiplication by `3` is separable. The divisor of `psi_3` has simple zeros at the nonzero 3-torsion points, so `psi_3` cannot be a nontrivial power in the algebraic function field. Since the secp256k1 subgroup has prime order `n!=3`, none of those zeros belongs to `H\{O}`.

Therefore every Fourier coefficient of

```text
a_k=chi(psi_3([k]P)),  1<=k<n,
a_0=0,
```

satisfies the explicit bound

```text
|a_hat(r)| <= 8 sqrt(p),
0<=r<n.                                      (V11.3)
```

No asymptotic O-constant is used.

## 4. Completion of the initial block

By Fourier inversion on `Z/nZ`,

```text
S_N=sum_(k=1)^N a_k
    =(1/n) sum_(r=0)^(n-1) a_hat(r) D_N(r),
```

where

```text
D_N(r)=sum_(k=1)^N exp(-2*pi*i*r*k/n).
```

For `r!=0`, put `j=min(r,n-r)`. Then

```text
|D_N(r)| <= 1/sin(pi*j/n) <= n/(2j),
```

using `sin x >= 2x/pi` on `[0,pi/2]`. Hence, with `M=(n-1)/2`,

```text
(1/n) sum_r |D_N(r)|
 <= 1 + H_M
 <= 2 + ln M.                                (V11.4)
```

Combining `(V11.3)` and `(V11.4)` yields

```text
|S_N| <= 8 sqrt(p) (2+ln((n-1)/2)).          (V11.5)
```

But `(V11.2)` says `a_k=1` throughout the first block, so `S_N=N`. Therefore every all-residue generator must satisfy

```text
boxed:
floor((n-1)/3)
 <= 8 sqrt(p) (2+ln((n-1)/2)).               (V11.6)
```

This is a deterministic large-order obstruction derived from a fixed division polynomial.

## 5. Exact secp256k1 certificate

For secp256k1,

```text
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141.
```

Since `n<2^256`,

```text
ln((n-1)/2) < ln n < 256 ln 2 < 256,
```

so `(V11.6)` implies the weaker necessary condition

```text
N <= 2064 sqrt(p),
N=floor((n-1)/3).                              (V11.7)
```

The committed exact integer certificate checks

```text
N^2 > 2064^2 * p,
2064^2 = 4,260,096.
```

Thus `(V11.7)` is false. Numerically the ratio `N/(2064*sqrt(p))` exceeds `2^115`, so the exclusion is nowhere near the boundary.

Consequently **no secp256k1 generator of order `n` has an all-residue nonzero EDS row**.

## 6. Closure of the pure division-polynomial family

Combine V9, V10 and V11:

1. odd `m`: impossible by `Q -> -Q` covariance;
2. even `m` when `chi(-1)=+1`: impossible by the same covariance;
3. secp256k1 has `chi(-1)=-1`, so even `m` is the only surviving case;
4. an exact even `m` would produce an all-residue re-marked generator by V10;
5. V11 proves no such generator can exist at secp256k1 scale.

Therefore

```text
There is no integer m such that
Q=[k]G -> chi(psi_m(Q))
computes (-1)^k on the secp256k1 subgroup.
```

This includes arbitrarily large `m`; no enumeration threshold remains.

## 7. Why small V10 witnesses do not contradict V11

V10 exhibited exact `m=2` parity decimations at orders 5 and 7. Inequality `(V11.6)` is weak at those sizes, so it permits them. The mechanism is therefore genuinely size-dependent:

```text
small exact examples exist,
large all-residue rows are forbidden by square-root cancellation.
```

This is useful evidence that the correct obstruction is analytic/global rather than a local Ward identity.

## 8. What remains open

V11 does not lower-bound arbitrary arithmetic circuits and does not close UORC-056. The principal surviving routes are:

1. direct field-valued evaluation of `Y_G(x(Q))/y(Q)` without expressing the answer as one quadratic character of a division polynomial;
2. compact distinguished global integration of the oriented Miller cocycle;
3. high-degree low-size straight-line programs not reducible to a single `chi(psi_m)`;
4. transposed or modular-composition representations;
5. level-`n` theta or elliptic-unit identities;
6. adaptive branching or other non-character outputs.

The next constructive work should return to these routes rather than enumerate more EDS decimations.

## 9. Source lock

Primary inputs:

- I. E. Shparlinski and K. E. Stange, *Character Sums with Division Polynomials*, Canadian Mathematical Bulletin 55 (2012), Lemmas 2 and 5. Lemma 5 gives the explicit `2 d sqrt(q)` subgroup bound; the proof later records `deg psi_l=(l^2-1)/2` for odd prime `l`.
- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in Number Theory 12:53 (2026), for the divisor and chain-rule interpretation of division polynomials.
- J. H. Silverman, *p-adic properties of division polynomials and elliptic divisibility sequences*, Math. Ann. 332 (2005), for finite-field periodicity and normalization context.

## 10. Claim boundary

V11 closes only the **pure single classical division-polynomial quadratic-character family on secp256k1**. It does not construct the central evaluator, recover an unknown scalar, prove a lower bound for unrestricted circuits, or claim a general ECDLP speedup/no-go theorem.
