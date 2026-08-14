# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C4: circulant norm blindness and two-anchor determinant circularity

Date: 2026-08-13

Status: **single-translation norms, characteristic data, and one-anchor translated determinants are exactly parity-blind. A two-anchor finite-rank determinant can retain the relative scalar, but the matrix determinant lemma reduces it to one Green-kernel coefficient, which is the original parity target. Local Krylov evaluation of that coefficient is already closed by C3. A genuinely two-anchor nonlocal coordinate resultant remains open.**

## 1. Setup

Let `H=<G>` have odd prime order `n`, and let `T=T_G` denote translation by `G` on the function space with basis indexed by `H`.

For a nonzero public point

```text
Q=[k]G,
1 <= k < n,
```

translation by `Q` is

```text
T_Q=T^k.
```

The target is the canonical scalar parity

```text
s_G(Q)=(-1)^k.
```

## 2. Every nonzero translation is one conjugacy class

Because `n` is prime, every nonzero `k` is invertible modulo `n`. Multiplication by `k` permutes the subgroup indices. Let `P_k` be the corresponding permutation matrix. Then

```text
boxed:
P_k^(-1) T P_k = T^k = T_Q.                     (N1)
```

Therefore every nonidentity subgroup translation is similar to the same `n`-cycle.

For every polynomial or rational matrix expression `F` defined at these operators,

```text
F(T_Q)=P_k^(-1)F(T)P_k.                          (N2)
```

Consequently the following data are independent of the nonzero scalar `k`:

```text
det F(T_Q),
trace F(T_Q),
rank F(T_Q),
characteristic polynomial of F(T_Q),
minimal polynomial of F(T_Q),
all similarity-invariant spectral data.          (N3)
```

No function in this class can equal canonical parity on all nonzero points.

## 3. Group-algebra norm consequence

Identify the cyclic group algebra with

```text
R=K[z]/(z^n-1),
```

where multiplication by `z` is represented by `T`.

If a candidate uses `Q` only by substituting

```text
z -> z^k
```

inside one fixed element `f(z)`, then multiplication by `f(z^k)` is similar to multiplication by `f(z)`. Hence

```text
boxed:
Norm_R/K(f(z^k))=Norm_R/K(f(z))                 (N4)
```

for every nonzero `k`.

Equivalently,

```text
Res(z^n-1,f(z^k))
```

is independent of nonzero `k` whenever the resultant is interpreted as the determinant of this multiplication operator.

A monomial shift also carries no scalar information. Since an odd `n`-cycle has determinant `+1`,

```text
Norm(z^a f(z^k))=Norm(f(z)).                     (N5)
```

This closes a single-translation norm or resultant that has no separate marked `G` anchor.

## 4. One-anchor translated perturbations are constant

Let `A` commute with `T`, and let `B` be one fixed operator. Move the whole marked perturbation with `Q`:

```text
A_k=A+T^k B T^(-k).                              (D1)
```

Then

```text
T^(-k) A_k T^k=A+B,                             (D2)
```

so

```text
boxed:
det(A+T^kBT^(-k))=det(A+B).                     (D3)
```

The same holds for every conjugacy invariant. A determinant with only one moving anchor cannot detect the position of that anchor on a homogeneous cycle.

## 5. Two anchors retain only their relative shift

Now allow independent left and right anchors:

```text
D(a,b)=det(A+T^a u v^T T^(-b)),                 (D4)
```

where `A` is invertible and commutes with `T`.

The matrix determinant lemma gives

```text
boxed:
D(a,b)
=det(A) * [1+v^T A^(-1) T^(a-b) u].             (D5)
```

Thus the determinant depends only on the relative shift `a-b`. Simultaneously translating both anchors changes nothing.

This is exactly the structural difference between a blind norm and the C2 determinant. The latter keeps the defect vertex `-G` fixed while the evaluation anchor moves with `Q`.

## 6. Specialization to the parity Green kernel

Take

```text
A=I+T,
u=v=e_0.
```

For odd `n`,

```text
det(I+T)=2,
(I+T)^(-1)=(1/2)sum_(j=0)^(n-1)(-1)^jT^j.       (G1)
```

The actual point defect and query covector can be written as two independent translates of `e_0`. Their relative shift is `k+1 mod n`. Substituting in `(D5)` gives

```text
boxed:
det(I+T+delta_(-G)ev_Q)=2+(-1)^k.               (G2)
```

The determinant is nonconstant because it preserves two anchors. But the only nontrivial scalar in `(D5)` is

```text
v^T(I+T)^(-1)T^(a-b)u,                           (G3)
```

which is precisely the Green-kernel entry whose extraction is the parity problem.

Therefore the generic rank-one determinant lemma does not compress the target. It identifies the exact matrix coefficient that must be evaluated by some additional structure.

## 7. Local Krylov evaluation is already closed

Expanding `(G3)` with `(G1)` produces the translated local moments

```text
v^T T^j u.
```

For point idempotents, each moment is one singleton membership probe. C3 proves that any exact adaptive algorithm using these local probes requires at least

```text
(n-1)/2
```

queries. Bounded-support block probes satisfy

```text
q*b >= (n-1)/2.
```

Hence black-box determinant, Wiedemann, Krylov, or transfer-function procedures do not advance the target when their `Q`-dependent interface reduces to the same local moment sequence.

## 8. What this closes

Closed in the declared models:

```text
Q-only characteristic or spectral invariants of T_Q,
one fixed group-algebra norm after z -> z^k,
monomially shifted versions of the same norm,
one-anchor translated determinant perturbations,
generic rank-one determinant-lemma reduction without a new Green-entry evaluator,
local Krylov extraction through translated point defects.
```

## 9. What remains open

Not closed:

1. a determinant or resultant involving both `T_G` and `T_Q` whose coordinate evaluation is genuinely nonlocal and sub-square-root;
2. a sparse two-translation circulant with an exact branch-extraction theorem and a compact evaluator not requiring `k`;
3. an oriented elliptic product that evaluates the two-anchor Green entry before local expansion;
4. a nonlinear coordinate-algebra state outside bounded-support moment access;
5. a broader circuit lower bound for two-anchor nonlocal observables.

A successful norm or resultant must preserve the relative `G,Q` anchor while avoiding the circular Green coefficient in `(D5)`.

## 10. Answer

```text
Does T_Q alone distinguish nonzero Q?                    no
Reason                                                   all T_Q are similar n-cycles
Does a single norm Res(z^n-1,f(z^k)) distinguish k?      no
Does one translated perturbation distinguish its place? no
Can two independent anchors retain k?                    yes, through relative shift
What does rank-one determinant reduction return?        the target Green-kernel entry
Can local Krylov moments evaluate it below the bound?    no, by C3
Genuinely nonlocal two-anchor resultant                  open
Public parity evaluator                                  absent
Sub-square-root ECDLP                                    absent
```
