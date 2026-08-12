# GLV-CARRY-FOURIER-REDUCTION-007

Date: 2026-08-11

Status: **isolated, non-executable source-conditional reduction package**.
No external point, key, wallet, or production discrete-log instance is
accepted. This package constructs no carry oracle and no EDS-residue decoder.
It changes no canonical Research Engine state and makes no unconditional
secp256k1 break claim.

## 1. Why this package exists

`NONLOCAL-ODD-ANCHOR-004` isolated

```text
R3(Q)=rho_G(Q)rho_G(phi Q)rho_G(phi^2 Q),
```

a Kummer- and GLV-invariant aggregate containing three nonpublic EDS-residue
factors. `GLV-CARRY-SEPARATION-005` then showed that the public point-function
orbit norm satisfies

```text
C3(Q)=g(Q)R3(Q),
```

where

```text
g(Q)=(-1)^gamma(Q),
gamma(Q) in {1,2}
```

is the canonical GLV lift carry.

Thus an exact public `R3` decoder immediately gives an exact carry decoder:

```text
g(Q)=C3(Q)R3(Q).
```

The remaining question is whether the carry is merely another weak bit, or
whether arbitrary chosen-multiplier access to it recovers the entire scalar.

This package gives a positive answer in the local sparse-Fourier oracle model.

## 2. Exact carry predicate

Let `n` be an odd prime, let `lambda` have order three modulo `n`, and choose
canonical representatives in `{1,...,n-1}`. For a nonzero scalar `u`, put

```text
r(u) = lambda*u mod n.
```

The third GLV representative is `lambda^2*u mod n`, and

```text
u+r(u)+(lambda^2*u mod n)=gamma(u)*n,
gamma(u) in {1,2}.
```

Because

```text
lambda^2+lambda+1=0 mod n,
```

the carry has the exact triangular form

```text
gamma(u)=1  iff  u+r(u)<n,
gamma(u)=2  iff  u+r(u)>n.
```

Define the sign

```text
g(u)=+1  if gamma(u)=2,
g(u)=-1  if gamma(u)=1,
g(0)=0.
```

It obeys

```text
g(lambda*u)=g(u),
g(-u)=-g(u).
```

The frozen verifier checks the triangle identity, GLV invariance, and negation
complement on all `14,298` nonzero scalars of the fifteen toy groups.

## 3. Exact Fourier formula

Use the normalized additive Fourier transform

```text
fhat(j)=(1/n) sum_(u mod n) f(u) exp(-2*pi*i*j*u/n).
```

Let

```text
c(u)=(g(u)+1)/2.
```

For `1<=u<n`, the carry can be written as a difference of two discrete
sawtooths:

```text
c(u)
 = floor((lambda+1)u/n)-floor(lambda*u/n).
```

For every invertible `a mod n` and every nonzero Fourier frequency, reindexing
by `a*u mod n` gives

```text
sum_(u=1)^(n-1) floor(a*u/n) z^u
 = -a/(1-z) + 1/(1-z^(a^(-1))),
```

where `z^n=1` and `z!=1`.

Substitution yields the exact carry spectrum

```text
n*ghat(j)
 = i*(
     cot(pi*[j]_n/n)
   + cot(pi*[lambda*j]_n/n)
   + cot(pi*[lambda^2*j]_n/n)
   ).                                                (F)
```

In particular, since the two nontrivial roots sum to `n-1`,

```text
|ghat(1)|
 = (1/n)*(
     cot(pi/n)
   + cot(pi*lambda/n)
   + cot(pi*lambda^2/n)
   )
 > cot(pi/n)/n.
```

For the fixed secp256k1 constants the normalized magnitude is

```text
0.31830988618379067153776752674502872406891929148091289749...
```

which differs from `1/pi` only beyond the displayed precision.

The coefficient is therefore a constant fraction of the signal energy, not a
small `O(sqrt(n))` fluctuation.

## 4. Logarithmic Fourier L1 bound

Equation (F) gives

```text
||ghat||_1
 <= (3/n) sum_(j=1)^(n-1) |cot(pi*j/n)|.
```

Using symmetry and

```text
cot(pi*j/n) <= n/(2j),
1 <= j <= (n-1)/2,
```

one obtains

```text
||ghat||_1 <= 3 H_((n-1)/2) = O(log n).              (L1)
```

For fixed public secp256k1 parameters the resulting elementary upper bound is
approximately

```text
531.989240123062760286002109186.
```

The toy spectra are much smaller in practice. The largest measured normalized
Fourier L1 value through order `4021` is approximately `13.4826`.

The logarithmic bound is the condition needed to keep the cited local
sparse-Fourier runtime polynomial in the bit length.

## 5. Hidden multiplicative decimation

Suppose the unknown public point is

```text
Q=[k]G,
```

and an exact carry oracle can be queried on arbitrary public scalar multiples:

```text
O_Q(t)=g([t]Q)=g(t*k mod n).
```

Define

```text
F_k(t)=O_Q(t).
```

A change of variables `u=t*k` in the Fourier sum gives the exact identity

```text
Fhat_k(j)=ghat(j*k^(-1)).                              (D)
```

Hence multiplication of the hidden scalar does not destroy the carry spectrum.
It permutes its frequencies:

```text
heavy(F_k)=k*heavy(g).
```

This is the decisive distinction from a generic one-bit leakage. The hidden
scalar appears as a multiplicative displacement of a known constant-heavy
additive Fourier spectrum.

## 6. Sparse-Fourier recovery

Adi Akavia's local SFT theorem gives a deterministic algorithm for finding
significant Fourier coefficients over any finite abelian group, including
`Z/nZ`, with runtime polynomial in

```text
log n, 1/tau, and ||fhat||_1,
```

and with point-oracle access to `f`. The theorem is also stated to be robust to
random noise. This package uses only its exact-oracle consequence.

Choose a fixed threshold, for example

```text
tau=0.25.
```

Run the local SFT algorithm twice:

1. on the known efficiently computable carry function `g`;
2. on the oracle function `F_k(t)=g(t*k)`.

Let the returned heavy-frequency lists be `H_g` and `H_F`. By (D), for every
true pair

```text
r in H_g,
j=k*r in H_F,
```

one has

```text
k=j*r^(-1) mod n.
```

Therefore enumerate the cross-ratio list

```text
K={j*r^(-1): j in H_F, r in H_g}
```

and test each candidate by checking

```text
[candidate]G = Q.
```

Parseval bounds the size of a constant-threshold heavy list by a constant.
Thus the final verification list is constant-sized.

On every frozen toy group, the `0.25`-heavy spectrum is exactly

```text
{+/-1, +/-lambda, +/-lambda^2}.
```

The cross-ratio list has at most six distinct candidates. Exhaustive replay
recovers every one of the `14,298` nonzero hidden toy scalars.

## 7. Reduction from the odd EDS anchor

For any chosen multiplier `t`, the public point is

```text
Q_t=[t]Q.
```

An exact `R3` decoder evaluated on `Q_t` gives `R3(Q_t)`, while the point-function
orbit norm `C3(Q_t)` is publicly computable. Therefore

```text
g(Q_t)=C3(Q_t)R3(Q_t).
```

Combining this with the sparse-Fourier recovery gives

```text
exact R3 oracle
  -> exact GLV carry oracle
  -> full discrete logarithm.
```

If one `R3` evaluation costs `T(n)`, the total reduction cost is

```text
poly(log n) * (T(n) + ordinary group/field arithmetic),
```

subject to the literal complexity guarantees and normalization conventions of
the cited local SFT theorem.

Thus the odd aggregate is not merely correlated with ECDLP. In this oracle
model it is ECDLP-complete under a polynomial-time Turing reduction.

## 8. What has and has not been solved

### Solved in this package

```text
carry is a known triangular predicate:                 yes
carry has a constant-heavy Fourier coefficient:        yes
normalized Fourier L1 is O(log n):                     yes
hidden scalar multiplicatively shifts the spectrum:    yes
heavy lists recover k up to a constant candidate set:  yes
R3 oracle gives carry oracle:                          yes
```

### Not solved

```text
public carry decoder from Q:                           absent
public R3 decoder from x(Q):                           absent
absolute section with a new GLV multiplier:            absent
unconditional sub-square-root secp256k1 algorithm:     absent
```

The result validates `R3` and the carry as exact bottlenecks. It does not
construct the missing section.

## 9. New research target

The next package should no longer ask whether the odd aggregate is useful. Its
usefulness is established by the reduction above.

The remaining constructive target is:

```text
THETA-GLV-CARRY-SECTION-008
```

> Construct a public theta, sigma, or line-bundle section whose C3 orbit norm
> separates `R3` from the canonical GLV carry, or prove normalization rigidity
> for the complete efficiently evaluable algebraic section category.

A positive section immediately enters the Fourier recovery pipeline. A
rigidity theorem would close the present algebraic category and force the
search into genuinely global analytic or p-adic monodromy.

## 10. Frozen artifacts

- `experiments/parity_lift_000/glv_carry_hidden_number_screen.py`
- `experiments/parity_lift_000/glv_carry_hidden_number_results.json`
- `experiments/parity_lift_000/glv_carry_fourier_recovery_screen.py`
- `experiments/parity_lift_000/glv_carry_fourier_recovery_results.json`

## Primary anchors

- Adi Akavia, *Finding Significant Fourier Transform Coefficients
  Deterministically and Locally*, ECCC TR08-102, for local SFT over arbitrary
  finite abelian groups and its stated complexity in `log|G|`, `1/tau`, and
  Fourier `L1` norm.
- Kristin Lauter and Katherine E. Stange, *The Elliptic Curve Discrete
  Logarithm Problem and Equivalent Hard Problems for Elliptic Divisibility
  Sequences*, for the EDS-residue and perfectly periodic point-function bridge.

## Claim boundary

The Fourier algebra, L1 estimate, decimation identity, and finite candidate
verification are explicit. Promotion to a canonical theorem requires a
claim-level audit of the external SFT theorem's normalization, oracle model,
and output guarantees. No actual `R3` or carry oracle is supplied.
