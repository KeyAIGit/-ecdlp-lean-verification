# SESQUILINEAR-CM-PAIRING-011

Date: 2026-08-12

Status: **natural sesquilinear Weil/Tate route closed on the secp256k1
rational prime-order line**.

No external point, key, wallet, or production discrete-log instance is accepted.
The package changes no canonical Research Engine state and makes no universal
pairing lower-bound or unconditional ECDLP-complexity claim.

## 1. Motivation

Ordinary Weil self-pairing is alternating, so

```text
e_n(Q,[lambda]Q)=1.
```

Sesquilinear CM pairings are a legitimate stronger candidate because they are
conjugate-linear in one variable rather than merely bilinear. In principle,

```text
T_hat_alpha([gamma]P,[delta]Q)
  = T_hat_alpha(P,Q)^(conjugate(gamma)*delta),
```

so a self-value could contain a quadratic exponent such as `k^2`, whose parity
matches the parity of `k`.

This package checks whether that possibility survives the actual pairing
domains and finite-field codomains for secp256k1.

Primary source:

- Katherine E. Stange, *Sesquilinear pairings on elliptic curves*,
  arXiv:2405.14167v5, especially Theorems 5.4-5.6, Proposition 5.7, and
  Algorithm 5.8.

## 2. Pairing domains

For a CM element `alpha`, the pulled-back pairings have domains

```text
W_hat_alpha : E[conjugate(alpha)] x E[alpha] -> target,
T_hat_alpha : E[conjugate(alpha)] x E/[alpha]E -> target.
```

This asymmetry is decisive.

## 3. Order-dependent annihilator

Let `omega` be the order-three CM automorphism and let `lambda` be its scalar
action on the secp256k1 subgroup

```text
H=<G>, |H|=n.
```

Consider

```text
alpha=lambda-omega.
```

On `H`,

```text
[alpha]Q=[lambda]Q-[omega]Q=O.
```

Thus

```text
H subset E[alpha].
```

However,

```text
conjugate(alpha)=lambda-omega^2
```

acts on `H` by

```text
c=lambda-lambda^2=2*lambda+1 mod n.
```

The fixed secp256k1 replay gives

```text
c=75436160726311993805852442966950040901855315110965173977233241085775995960037,
```

with inverse

```text
c^(-1)=52049339249440132347096509016808591601273271149061544929325695065753442342879
        mod n.
```

Therefore

```text
H intersect E[conjugate(alpha)]={O}.
```

### Consequence for W_hat_alpha

`Q` may be used in the second input, because `Q in E[alpha]`, but no nonzero
point of the known rational line can be used in the first input. The pairing
needs a point in the conjugate kernel, which is precisely an independent
extension-field direction.

Swapping `alpha` and `conjugate(alpha)` does not help. Then the rational line is
available only in the first input, not the second.

### Consequence for T_hat_alpha

For `alpha=lambda-omega`, the same conjugate-kernel first input is missing.

For `alpha=conjugate(lambda-omega)`, the rational line is admissible in the
first input, but the quotient in the second input is

```text
E/[conjugate(alpha)]E.
```

Since `[conjugate(alpha)]` acts on `H` by the unit `c`, every `Q in H` has the
public preimage

```text
[c^(-1)]Q.
```

Hence the class of every rational-line `Q` in this quotient is zero, and the
pairing value is trivial.

This closes the most natural order-dependent CM-annihilator construction.

## 4. Size of the annihilator

The Eisenstein norm is

```text
N(lambda-omega)=lambda^2+lambda+1.
```

It is divisible by `n`, but is not a small-degree isogeny:

```text
N(lambda-omega)/n
 =12286276166636580012140862095472453253950970278553425451194017527274075467639,
```

which is a 253-bit cofactor. The full norm is 509 bits.

Thus even an explicit generalized-isogeny realization is not a bounded-degree
escape.

## 5. Central choice alpha=n

The remaining natural choice is the central integer `alpha=n`.

### Sesquilinear Weil pairing

Both inputs may now be chosen from `H`, but Theorem 5.4 expresses
`W_hat_n` as a product of ordinary Weil pairings of CM scalar multiples of the
inputs. For `P,Q in H`, all such points lie on one cyclic line. Every classical
factor is therefore an alternating pairing of dependent points and equals one.
Consequently

```text
W_hat_n(P,Q)=1 for P,Q in H.
```

The sesquilinear packaging does not remove the dependent-line degeneracy.

### Sesquilinear Tate pairing over F_p

Theorem 5.6 expresses `T_hat_n` as a product of ordinary `n`-Tate pairing
values. But

```text
gcd(n,p-1)=1.
```

Therefore the map

```text
x -> x^n
```

is an automorphism of `F_p^*`, and

```text
F_p^*/(F_p^*)^n
```

is trivial. Every classical Tate factor, and hence `T_hat_n`, is trivial over
the base field.

### Extension field

The source non-degeneracy theorem assumes a field containing the relevant
roots of unity and the full torsion. At minimum, containing `mu_n` requires

```text
d=ord_n(p)=(n-1)/6,
```

where

```text
log2(d)=253.41503749927884.
```

This is the same exact embedding-degree barrier certified in
`GLOBAL-MONODROMY-SECTION-009`. An explicit field element already needs a basis
with `d` base-field coefficients, far above the square-root operation scale.

Miller-style evaluation being polynomial in the coefficients of `alpha` does
not remove the cost of representing the field in which the nontrivial value
lives.

Furthermore, the resulting torsion target has odd order. Squaring is an
automorphism on an odd-order group, so it has no nontrivial binary character.
A quadratic-residue test of a root-of-unity value cannot reveal parity.

## 6. Exact decision

```text
W_hat_(lambda-omega) using only H:          blocked by missing conjugate kernel
T_hat_(lambda-omega) using only H:          blocked by missing conjugate kernel
T_hat_conjugate(lambda-omega) on H:         quotient class of Q is zero
W_hat_n on H x H:                           identically one
T_hat_n over F_p:                           base-field quotient is trivial
T_hat_n over a nondegenerate extension:     requires degree (n-1)/6
binary character of the odd-order target:   trivial
public carry decoder:                       absent
public R3 decoder:                          absent
unconditional sub-sqrt algorithm:           absent
```

This is a scoped no-go for the natural sesquilinear CM pairing constructions.
It is not a theorem against all possible biextension, pairing-like, or
non-algebraic observables.

## 7. Formal and replay artifacts

- `Ecdlp/Proved/SesquilinearCmPairingBoundary.lean`;
- `experiments/parity_lift_000/sesquilinear_cm_pairing_boundary.py`;
- `experiments/parity_lift_000/sesquilinear_cm_pairing_results.json`.

Lean kernel-checks the fixed eigenvalue relation, conjugate action formula,
explicit inverse, surjectivity on the rational scalar line, divisibility of the
annihilator norm, and triviality of its conjugate kernel intersection with the
line.

Lean does not formalize Stange's pairing construction or the identifications of
its domains and codomains. Those are source-level inputs stated explicitly
above.

## 8. Constructive successor

The dual-character route is now reduced further. The surviving mechanism must
avoid all of:

1. an ordinary or sesquilinear pairing requiring an independent torsion line;
2. a target whose nontrivial realization requires `mu_n` explicitly;
3. an odd-order target with no binary quotient;
4. a quotient in which the public rational line is already in the image;
5. a bounded homogeneous algebraic section covered by `C_quad`.

The next theorem-first package is

```text
DUAL-CHARACTER-LINEAR-SUPPORT-012.
```

It studies the exact additive Fourier spectrum of the carry. The goal is to
prove that every nonzero additive frequency occurs, so an exact linear
combination of public dual characters requires full support rather than a
sparse compressed representation. This does not rule out nonlinear circuits,
but it closes the most direct compressed-character model.
