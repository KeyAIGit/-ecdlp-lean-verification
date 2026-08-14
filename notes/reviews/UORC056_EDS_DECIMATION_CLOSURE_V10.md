# UORC-056 EDS decimation closure V10

Date: 2026-08-14

Status: **the pure division-polynomial / EDS-decimation character route left open by V9 is closed.**

Central target remains unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

This checkpoint does not construct the target evaluator. It proves that no single quadratic character of a classical division polynomial can be that evaluator, for any index `m`, on an odd prime-order marked subgroup.

## 1. Statement

Let `E/F_q` be an elliptic curve over a finite field of odd characteristic, let

```text
H=<G>,  |H|=n,
```

with `n>=3` an odd prime, and let `chi` be the quadratic character. For every positive integer `m`, define

```text
D_m([k]G)=chi(psi_m([k]G)),  1<=k<n.
```

Then

```text
D_m([k]G) != (-1)^k
```

for at least one `k` in `1,...,n-1`.

Thus there is no exceptional even EDS decimation left to search.

## 2. Odd indices and q=1 mod 4

Classical division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q).
```

Canonical parity on an odd cycle is anti-invariant:

```text
sigma_G(-Q)=-sigma_G(Q).
```

Hence:

1. if `m` is odd, `psi_m` is invariant under `Q -> -Q`, so its quadratic character cannot equal parity;
2. if `m` is even and `chi(-1)=+1`, its quadratic character is again invariant, so it cannot equal parity.

Only the case

```text
m even,
chi(-1)=-1,
```

can pass the negation gate. This is exactly the secp256k1 congruence class.

## 3. Chain-rule reduction of the surviving case

Assume for contradiction that `m` is even, `chi(-1)=-1`, and

```text
chi(psi_m([k]G))=(-1)^k
```

for every `1<=k<n`.

Since `m^2` is even, the division-polynomial chain rule

```text
psi_(mk)(G)=psi_m([k]G) * psi_k(G)^(m^2)
```

implies

```text
rho_(mk)=(-1)^k,
rho_j=chi(psi_j(G)).
```

At `k=1`, therefore,

```text
rho_m=-1.
```

Put

```text
P=[m]G.
```

If `n | m`, then `psi_m(G)=0`, already contradicting `rho_m=-1`. Since `n` is prime, otherwise `P` is again a generator of `H`.

Apply the chain rule in the opposite order:

```text
psi_(mk)(G)=psi_k(P) * psi_m(G)^(k^2).
```

Taking quadratic characters and using

```text
k^2 == k mod 2,
rho_m=-1,
rho_(mk)=(-1)^k,
```

gives

```text
chi(psi_k(P))=+1
```

for every `1<=k<n`.

So an exact even decimation would force the complete nonzero EDS-residue row of a generator `P` to be identically quadratic-residue.

## 4. Ward quasi-periodicity forbids an all-residue row

For a point `P` of order `n>=3`, Shparlinski--Stange quote the classical Ward/Silverman torsion formula

```text
psi_(s*n+k)(P)=a^(k*s) b^(s^2) psi_k(P),
```

for positive integers `s,k`, with

```text
a = psi_(n-2)(P)/(psi_(n-1)(P) psi_2(P)),

b = psi_(n-1)(P)^2 psi_2(P)/psi_(n-2)(P).
```

Under the forced all-residue condition

```text
chi(psi_k(P))=1,  1<=k<n,
```

all factors defining `a` and `b` are nonzero and

```text
chi(a)=chi(b)=1.
```

Therefore Ward quasi-periodicity at `(s,k)=(1,1)` and `(2,1)` gives

```text
chi(psi_(n+1)(P))  = 1,
chi(psi_(2n+1)(P)) = 1.                 (V10.1)
```

Now use the standard EDS/division-polynomial recurrence

```text
psi_(h+i) psi_(h-i) psi_j^2
+ psi_(i+j) psi_(i-j) psi_h^2
+ psi_(j+h) psi_(j-h) psi_i^2 = 0.
```

Substitute

```text
h=n+1,
i=n,
j=1.
```

Because

```text
psi_n(P)=0,
psi_1(P)=1,
```

we get the exact identity

```text
psi_(2n+1)(P)
  = - psi_(n+1)(P)^3 psi_(n-1)(P).     (V10.2)
```

All three nonzero division-polynomial factors on the right of `(V10.2)` have quadratic character `+1` by the all-residue condition and `(V10.1)`. Hence

```text
chi(psi_(2n+1)(P))=chi(-1)=-1,
```

contradicting `(V10.1)`.

Therefore an all-residue EDS row cannot occur when `chi(-1)=-1`, and the surviving even decimation is impossible.

## 5. Consequence for secp256k1

The secp256k1 subgroup order is odd prime and its base field satisfies

```text
p == 3 mod 4,
chi(-1)=-1.
```

V9 reduced every surviving pure division-polynomial candidate to

```text
m even,
k -> rho_(m*k).
```

V10 proves that no such `m` exists. This is independent of the size of `m`; the former lower threshold

```text
m >= 14715411119103453974
```

no longer defines an open search range.

## 6. Exact scope

V10 closes:

- every odd-index `chi(psi_m(Q))` by negation covariance;
- every even-index `chi(psi_m(Q))` over `q=1 mod 4` by negation covariance;
- every even-index `chi(psi_m(Q))` over `q=3 mod 4` by chain-rule reduction plus Ward quasi-periodicity and the EDS recurrence;
- equivalently, the pure even EDS decimation frontier isolated in V9.

It does not close:

1. direct field-valued evaluation of `Y_G(x(Q))/y(Q)`;
2. rational functions not restricted to one division polynomial whose succinct programs use cancellations not represented by this route;
3. theta, elliptic-unit or higher-level CM constructions;
4. transposed/modular-composition representations;
5. adaptive branching or non-character outputs;
6. compact distinguished global integration of the oriented Miller cocycle.

## 7. Source lock

Primary sources used for the algebraic identities:

1. I. E. Shparlinski and K. E. Stange, *Character Sums with Division Polynomials*, Canadian Mathematical Bulletin 55 (2012), 850--857, especially Lemmas 1--3. Lemma 1 records the Ward/Silverman torsion quasi-periodicity and Lemma 2 the multiplication chain rule.
2. K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in Number Theory 12:53 (2026), equations (1.1)--(1.3) and the chain rule.
3. S. Bhakta, *Character sums of division polynomials twisted by multiplicative functions*, Canadian Mathematical Bulletin, FirstView (2026), Lemma 2.3, for an independent modern statement of the chain rule after applying a multiplicative character.

## 8. Claim boundary

The theorem is an exact algebraic no-go for the **pure single-division-polynomial quadratic-character family** on odd prime-order subgroups. It is not a general arithmetic-circuit lower bound, does not solve ECDLP, and does not produce or evaluate an unknown production scalar.
