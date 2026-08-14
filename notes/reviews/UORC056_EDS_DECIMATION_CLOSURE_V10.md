# UORC-056 EDS decimation audit V10

Date: 2026-08-14

Status: **the attempted all-index EDS-decimation closure is retracted. The valid chain-rule reduction survives, but its proposed Ward obstruction is false. Explicit q=3 mod 4 counterexamples show that a generator can have an all-residue nonzero EDS row. The secp256k1 even-decimation frontier therefore remains open.**

Central target remains unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

## 1. What remains proved from V9

Classical division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q).
```

Hence:

1. odd `m` cannot give parity because the quadratic-character output is invariant under `Q -> -Q`;
2. even `m` over `q=1 mod 4` cannot give parity because `chi(-1)=+1` again makes the output invariant;
3. only even `m` over `q=3 mod 4` survives this covariance gate. secp256k1 is in this class.

## 2. Valid chain-rule reduction

Assume `m` is even, `chi(-1)=-1`, and

```text
chi(psi_m([k]G))=(-1)^k
```

for every `1<=k<n`. The chain rule gives

```text
psi_(mk)(G)=psi_m([k]G) * psi_k(G)^(m^2),
```

so, with `rho_j=chi(psi_j(G))`, `rho_(mk)=(-1)^k` and in particular `rho_m=-1`.

Put `P=[m]G`. If `n | m`, then `psi_m(G)=0`, impossible. Otherwise `P` is a generator because `n` is prime. Using the chain rule in the opposite order,

```text
psi_(mk)(G)=psi_k(P) * psi_m(G)^(k^2),
```

and `k^2 == k mod 2` gives

```text
chi(psi_k(P))=+1,  1<=k<n.             (V10.1)
```

Thus any exact even decimation would imply the existence of a generator whose complete nonzero EDS-residue row is all quadratic residues. This reduction is correct and remains useful.

## 3. Correction of the Ward normalization

The first V10 attempt used a misread normalization for the torsion quasi-period constants. The primary source is Silverman, Theorem 8. For a point `P` of order `n>=3`, there exist units `a,b` such that

```text
F_(s*n+k)(P)=a^(s*k) b^(s^2) F_k(P).
```

With Silverman's normalized division functions,

```text
a = F_(n+2)(P)/(F_2(P) F_(n+1)(P)),
b = F_2(P) F_(n+1)(P)^2/F_(n+2)(P).
```

The same `n+1,n+2` normalization is what the classical short-Weierstrass division-polynomial recurrence satisfies up to the fixed normalization gauge. The earlier `n-1,n-2` reading cannot be used to infer `chi(a)=chi(b)=+1` from `(V10.1)`.

Under an all-residue row, the recurrence is instead compatible with

```text
chi(a)=+1,
chi(b)=-1
```

when `chi(-1)=-1`. There is no contradiction.

## 4. Exact counterexamples to the proposed obstruction

The corrected replay exhibits genuine generators on the same curve shape

```text
y^2=x^3+7
```

over fields with `q=3 mod 4` whose entire nonzero division-polynomial row consists of quadratic residues.

Two frozen counterexamples are:

```text
F_59: P=(31,11), ord(P)=5,
chi(psi_k(P))=+1 for k=1,2,3,4;

F_83: P=(74,5), ord(P)=7,
chi(psi_k(P))=+1 for k=1,...,6.
```

For both examples the corrected Ward constants satisfy

```text
chi(a)=+1,
chi(b)=-1,
```

and the Ward quasi-period formula and EDS recurrence hold exactly. Therefore the all-residue condition by itself is not an obstruction to an even decimation.

## 5. Consequence for secp256k1

The secp256k1-specific open case remains

```text
m even,
chi(psi_m([k]G))=rho_(m*k),
q=3 mod 4.
```

V10 does not find an exceptional `m`, but it proves that the proposed shortcut

```text
exact decimation -> all-residue re-marked row -> impossible
```

stops at the second implication: all-residue rows are possible.

The bounded V9 screens remain valid evidence only. They do not settle arbitrary `m`.

## 6. Revised next questions

The useful next statements are now more precise:

1. classify the pair of Ward sign invariants `(chi(a_P),chi(b_P))` as the generator `P` varies through `<G>`;
2. determine the exact action of re-marking `P=[m]G` on these invariants;
3. combine `(V10.1)` with the *generator-change law*, not merely with the existence of an all-residue row;
4. test whether an all-residue generator `P` can specifically arise from an even `m` satisfying `rho_m=-1` relative to the original marked generator `G`;
5. if this route remains inconclusive, return to the non-character central routes: direct field-valued `Y_G`, compact global integration of the oriented Miller cocycle, theta/elliptic-unit and transposed representations.

## 7. Source lock

The correction is anchored to the primary normalization in:

- J. H. Silverman, *p-adic properties of division polynomials and elliptic divisibility sequences*, Math. Ann. 332 (2005), Theorem 8, especially the explicit formulas obtained from `F_(n+1)` and `F_(n+2)`;
- K. E. Stange, *Division polynomials for arbitrary isogenies*, Research in Number Theory 12:53 (2026), for the classical recurrence and chain rule;
- S. Bhakta, *Character sums of division polynomials twisted by multiplicative functions*, Canadian Mathematical Bulletin (2026), Lemma 2.3, for the multiplicative-character chain rule.

## 8. Claim boundary

V10 is now an **error-correcting checkpoint**, not a no-go theorem. It preserves the valid chain-rule reduction and supplies exact counterexamples to an invalid obstruction. No public parity evaluator, sub-square-root ECDLP algorithm, or arbitrary-index EDS-decimation classification is claimed.
