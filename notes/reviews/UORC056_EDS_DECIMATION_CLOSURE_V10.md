# UORC-056 EDS decimation audit V10

Date: 2026-08-14

Status: **the attempted universal EDS-decimation no-go is retracted. More strongly, exact even EDS decimations genuinely exist on small odd prime-order curves. The secp256k1 case remains open and must be attacked by a large-order or secp-specific argument.**

Central target remains unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

## 1. Surviving division-polynomial family

The classical covariance

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q)
```

still closes odd `m` and even `m` when `chi(-1)=+1`. The only family relevant to secp256k1 is

```text
m even,
chi(-1)=-1,
D_m([k]G)=chi(psi_m([k]G)).
```

For even `m`, the chain rule gives

```text
D_m([k]G)=rho_(m*k),
rho_j=chi(psi_j(G)).
```

## 2. Exact re-marking equivalence

Suppose `n` is odd prime, `n` does not divide even `m`, and put `P=[m]G`. The chain rule in the two orders gives

```text
psi_(mk)(G)=psi_m([k]G) psi_k(G)^(m^2)
           =psi_k(P) psi_m(G)^(k^2).
```

Therefore

```text
D_m([k]G)=(-1)^k for every 1<=k<n
```

if and only if

```text
rho_m(G)=-1
```

and

```text
chi(psi_k(P))=+1 for every 1<=k<n.       (V10.1)
```

So the problem is exactly a generator-reorientation problem: find an even lift `m` whose image generator has an all-residue EDS row while the transition term `rho_m(G)` is a nonresidue.

## 3. Ward normalization correction

The first V10 attempt used a wrong reading of the torsion quasi-period constants. The primary normalization is Silverman, Theorem 8:

```text
F_(s*n+k)(P)=a^(s*k) b^(s^2) F_k(P),
```

with

```text
a=F_(n+2)(P)/(F_2(P)F_(n+1)(P)),
b=F_2(P)F_(n+1)(P)^2/F_(n+2)(P).
```

Thus `(V10.1)` does not imply both Ward constants are residues. In the exact examples below it gives

```text
chi(a)=+1,
chi(b)=-1,
```

which is fully compatible with the EDS recurrence when `chi(-1)=-1`.

## 4. Exact parity-decimation witnesses

The corrected executable replay finds and freezes two exact mechanisms on the same secp-shaped curve family `y^2=x^3+7`.

### Order 5

```text
F_59,
G=(22,25),
n=5,
m=2,
P=[2]G=(31,11).
```

Exactly,

```text
chi(psi_2([k]G))=(-1)^k, k=1,2,3,4.
```

Moreover

```text
chi(psi_2(G))=-1
```

and the re-marked generator `P` satisfies

```text
chi(psi_k(P))=+1, k=1,2,3,4.
```

### Order 7

```text
F_83,
G=(70,36),
n=7,
m=2,
P=[2]G=(74,5).
```

Again

```text
chi(psi_2([k]G))=(-1)^k, k=1,...,6,
```

while `rho_2(G)=-1` and every nonzero EDS-residue sign of `P` is `+1`.

Both examples have `q=3 mod 4`. The corrected Ward formula and the specialized EDS recurrence are checked exactly.

## 5. Meaning for secp256k1

This changes the scientific status of the family. Even division-polynomial decimation is not merely a surviving formal possibility: it is a **real exact parity mechanism on small curves**.

V9's five larger frozen discovery curves contain no exact even class modulo `2n`, so the property is not generic. But a universal algebraic no-go cannot be true.

For secp256k1 the problem becomes:

```text
Does there exist an even m mod 2n such that
rho_m(G)=-1
and [m]G has an all-residue nonzero EDS row?
```

Since the character sequence has period dividing `2n`, this is a finite but astronomically large structural question, not an unbounded-index question.

## 6. Next high-leverage route

The next attack should combine the exact equivalence with large-order information:

1. derive the generator-change law for Ward sign invariants and for the all-residue property;
2. use published character-sum bounds for `sum chi(psi_k(P))` to test whether an all-residue row can exist when `ord(P)` is comparable to the field size;
3. make the constants explicit enough for the fixed secp256k1 field if possible;
4. exploit CM/GLV only if it gives a stronger secp-specific exclusion or constructive selector.

If this does not close the EDS-decimation family, the other central routes remain direct field-valued `Y_G`, compact distinguished integration of the oriented Miller cocycle, theta/elliptic-unit formulas and transposed representations.

## 7. Source lock

- J. H. Silverman, *p-adic properties of division polynomials and elliptic divisibility sequences*, Math. Ann. 332 (2005), Theorem 8.
- I. E. Shparlinski and K. E. Stange, *Character Sums with Division Polynomials*, Canadian Mathematical Bulletin 55 (2012), for EDS-character periodicity and character-sum bounds.
- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in Number Theory 12:53 (2026), recurrence and chain rule.
- S. Bhakta, *Character sums of division polynomials twisted by multiplicative functions*, Canadian Mathematical Bulletin (2026), Lemma 2.3.

## 8. Claim boundary

V10 now proves an exact re-marking equivalence and exact small-curve parity-decimation witnesses. It does **not** assert that secp256k1 admits such an `m`, nor that one can locate it below square-root cost.
