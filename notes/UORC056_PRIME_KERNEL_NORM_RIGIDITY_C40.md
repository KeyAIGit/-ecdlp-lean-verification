# UORC-056 C40: prime-kernel norm rigidity

Date: 2026-08-16

Status: exact structural boundary. No parity oracle or sub-square-root ECDLP algorithm is claimed.

## 1. Question left by C39

C39 gives the exact degree-optimal decoder

\[
D_{\rm orb}(Z)=\frac{P_{\rm odd}(Z)-P_{\rm even}(Z)}{P_{\rm odd}(Z)+P_{\rm even}(Z)}
\]

for the compact half-index Miller state. The missing operation is an on-demand evaluation of the ordered half-orbit factors without materializing their `m=(n-1)/2` coefficients.

The first natural candidate is an isogeny norm. C40 determines exactly what such a norm can and cannot do.

## 2. The full rational subgroup is a compact Frobenius fibre

For every frozen curve and for secp256k1, the cofactor is one:

\[
H=E(\mathbb F_p),\qquad |H|=n.
\]

Let `pi` be Frobenius. Then

\[
H=\ker(\pi-1).
\]

For any extension-field point `S`, the fibre through `S` is

\[
(\pi-1)^{-1}((\pi-1)S)=S+H.
\]

Thus a product over the complete rational subgroup has compact geometric support: it is a norm along the separable isogeny `pi-1`.

The exact replay verifies on all five frozen curves:

```text
#E(F_p)=n,
(pi-1)([k]G)=O,
(pi-1)(S+[k]G)=(pi-1)(S)
```

for every subgroup point.

## 3. Why the compact full norm is insufficient

A full norm

\[
N_f(S)=\prod_{T\in H}f(S+T)
\]

is invariant under translation by a point of `H`, because translation only permutes the fibre. It is also invariant under re-marking the generator, including `G -> -G`, because the full index set is unchanged.

The executable replay checks the full product and the full state orbit polynomial under all 443 frozen translations and under generator reversal.

C39 needs an ordered difference

\[
\Delta=P_{\rm odd}-P_{\rm even},
\]

which changes sign when the two marked halves are exchanged. A full-kernel norm retains only symmetric information such as

\[
P_{\rm odd}P_{\rm even}
\quad\text{and}\quad
P_{\rm odd}+P_{\rm even}.
\]

It cannot choose the anti-invariant branch `Delta`.

## 4. The parity halves are not isogeny fibres

For odd prime `n`, define

\[
E_+=\{2,4,\ldots,n-1\},
\qquad
E_-=\{1,3,\ldots,n-2\}.
\]

Each set has size

\[
m=\frac{n-1}{2}.
\]

Neither is a subgroup:

\[
1\in E_-,\quad 1+1=2\notin E_-,
\]

and

\[
n-1\in E_+,\quad (n-1)+(n-1)=n-2\notin E_+.
\]

More generally, a cyclic group of prime order has only subgroup sizes `1` and `n`. Every subgroup coset has one of the same two sizes. Therefore a set of size `(n-1)/2` cannot be the kernel, a kernel coset, or a fibre component of an isogeny whose kernel lies inside `H`.

Consequently there is no nontrivial subgroup-norm tower inside `H`. Every step is either a one-point evaluation or the complete `n`-point norm.

## 5. Interpretation of the C39 factors

The C39 factors are not ordinary isogeny norms. They are incomplete oriented norms over a marked choice of one point from every pair

\[
\{P,-P\}.
\]

The choice is determined by canonical scalar parity. It is exactly the information carried by the oriented root `Y_G`.

This explains why the compact map `pi-1` helps with the unordered orbit but does not reduce the ordered half-orbit evaluation. The obstruction is not the absence of a compact full-kernel isogeny. The obstruction is that parity asks for a non-subgroup section of its fibre.

## 6. Decision

C40 closes:

```text
ordinary full-kernel isogeny norms,
Frobenius-minus-identity full norms,
subgroup-coset norms inside H,
recursive norm towers whose kernels lie inside H.
```

It does not close:

```text
incomplete-product algorithms,
target-dependent transposed resultants,
elliptic-net recurrences not induced by subgroup towers,
nonlinear transfer matrices carrying an oriented section.
```

The next frontier is

```text
INCOMPLETE-ORIENTED-PRODUCT-C41
```

The required algorithm must evaluate one marked half of a prime fibre without converting the problem back into `Theta(n)` coefficients or a square-root-width table.
