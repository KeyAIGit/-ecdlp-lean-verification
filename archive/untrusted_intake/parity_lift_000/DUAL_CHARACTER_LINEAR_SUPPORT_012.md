# DUAL-CHARACTER-LINEAR-SUPPORT-012

Date: 2026-08-12

Status: **exact no-go for sparse linear additive-character representations of
the GLV carry**.

No external point, key, wallet, or production discrete-log instance is accepted.
This is not a lower bound for arbitrary nonlinear algorithms.

## 1. Fourier formula

Let `g(k)=(-1)^gamma(k)` be the GLV carry sign and let the normalized additive
Fourier transform be

```text
g_hat(j)=(1/n)*sum_k g(k)*exp(-2*pi*i*j*k/n).
```

For every nonzero frequency `j`, define canonical residues

```text
a=[j]_n,
b=[lambda*j]_n,
c=[lambda^2*j]_n.
```

Because

```text
1+lambda+lambda^2=0 mod n,
```

and `j` is nonzero, all three residues lie in `{1,...,n-1}` and

```text
a+b+c=gamma_j*n,
gamma_j in {1,2}.
```

The exact carry transform is

```text
g_hat(j)
 = (i/n)*(cot(pi*a/n)+cot(pi*b/n)+cot(pi*c/n)).
```

## 2. No coefficient vanishes

First suppose `a+b+c=n` and put

```text
A=pi*a/n,
B=pi*b/n,
C=pi*c/n.
```

Then `A+B+C=pi`. Set

```text
x=cot(A), y=cot(B), z=cot(C).
```

The cotangent addition identity gives

```text
x*y+y*z+z*x=1.
```

Therefore

```text
(x+y+z)^2>=3,
```

because

```text
(x-y)^2+(y-z)^2+(z-x)^2>=0.
```

Moreover the cotangent sum is positive for three positive angles summing to
`pi`. Hence

```text
cot(A)+cot(B)+cot(C)>=sqrt(3).
```

If `a+b+c=2n`, replace each angle by its complement `pi-A`, `pi-B`, `pi-C`.
The complementary angles sum to `pi`, while each cotangent changes sign. Thus

```text
cot(A)+cot(B)+cot(C)<=-sqrt(3).
```

Consequently, for every `j!=0`,

```text
|g_hat(j)|>=sqrt(3)/n>0.
```

The zero-frequency coefficient vanishes because `g(-k)=-g(k)`. Therefore the
Fourier support is exactly

```text
support(g_hat)=Z/nZ minus {0},
|support(g_hat)|=n-1.
```

## 3. Consequence

Additive characters form a basis of all complex functions on `Z/nZ`, so their
Fourier coefficients are unique. Any exact representation

```text
g(k)=sum_(j in S) c_j*exp(2*pi*i*j*k/n)
```

must contain every nonzero frequency:

```text
|S|>=n-1.
```

For secp256k1 this is essentially `2^256` terms. Thus the direct proposal

```text
compute carry as a sparse linear combination of a small number of dual
characters
```

is impossible.

This does not contradict the six heavy frequencies used in
`GLV-CARRY-FOURIER-REDUCTION-007`. Those six suffice to recover a hidden
multiplicative decimation when an exact carry oracle already exists. They do
not reconstruct the carry function exactly.

## 4. Validation

The frozen replay evaluated all nonzero frequencies on fifteen toy groups:

```text
frequencies checked:          14,298
full-support failures:        0
sign failures:                0
sqrt(3) bound failures:       0
largest order:                4,021
```

The smallest observed unnormalized cotangent magnitude was

```text
1.73329526630219289558578409499,
```

already close to `sqrt(3)` from above.

Artifacts:

- `Ecdlp/Proved/DualCharacterLinearSupport.lean`;
- `experiments/parity_lift_000/dual_character_linear_support.py`;
- `experiments/parity_lift_000/dual_character_linear_support_results.json`.

Lean kernel-checks the algebraic implication

```text
xy+yz+zx=1 -> (x+y+z)^2>=3 -> x+y+z!=0.
```

It does not formalize the cotangent Fourier formula or Fourier uniqueness.

## 5. Exact boundary

```text
exact sparse linear dual-character carry formula:    impossible
full linear support required:                         n-1
nonlinear compressed dual character:                  open
public carry decoder:                                 absent
public R3 decoder:                                    absent
unconditional sub-sqrt algorithm:                     absent
```

## 6. Surviving bottleneck

The remaining constructive possibility must be genuinely nonlinear. It must
evaluate enough information about the hidden primitive character

```text
zeta_n^k
```

without explicitly materializing `mu_n`, an `n`-dimensional theta space, or all
`n-1` Fourier modes.

The next package should test low-complexity nonlinear character circuits rather
than additional linear combinations. A candidate is admissible only if it
comes with a public evaluation map from `(G,Q)`, exact branch semantics, and a
full sub-square-root cost model.
