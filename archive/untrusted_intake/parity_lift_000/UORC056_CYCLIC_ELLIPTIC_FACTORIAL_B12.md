# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — CYCLIC ELLIPTIC FACTORIAL B12

Date: 2026-08-14

Status: **open candidate specification, not an algorithm. The alternating Miller potential is, under complex sigma uniformization and up to a point-independent normalization, a ratio of two finite elliptic shifted factorials with step `2G`. Existing elliptic shifted-factorial and root-of-unity cyclic-dilogarithm identities do not presently supply a finite-field, generator-oriented, sub-square-root evaluator for this object.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Exact target inherited from B8

Let `n=2M+1`, let `z` and `g` represent `P` and `G` on a complex uniformization, and let `sigma` be the Weierstrass sigma function.

A standard line quotient with divisor

```text
(R)+(G)-(R+G)-(O)
```

has, up to a nonzero normalization independent of `z`, the sigma expression

```text
g_(R,G)(z)
 =sigma(z-r)sigma(z-g)
  /[sigma(z-r-g)sigma(z)].                       (B12.1)
```

Multiplying `(B12.1)` over `r=(2j-1)g`, `1<=j<=M`, gives

```text
boxed:
H_G(z)
 =C_G [sigma(z-g)/sigma(z)]^M
    * product_(j=0)^(M-1) sigma(z-(2j+1)g)
      / product_(j=1)^M sigma(z-2jg).             (B12.2)
```

Thus `H_G` is an alternating finite elliptic shifted factorial with step `2g`.

Equation `(B12.2)` is a characteristic-zero uniformization of the exact algebraic Miller product from B8. The finite-field object is defined algebraically by B8 and does not depend on choosing a complex embedding.

## 2. Difference equation

The shifted factorial satisfies the exact first-order relation already derived algebraically in B8:

```text
H_G(P+2G)=c_2(P)H_G(P),                          (B12.3)
```

where `c_2` has a four-point generalized-Miller divisor and can be evaluated from logarithmic-length scalar data.

The full product over all `n` translates is controlled by ordinary multiplication/kernel formulas. The half-factor in `(B12.2)` is not a subgroup product and has trivial translation stabilizer by B10.

## 3. Relation to known special-function classes

The literature contains:

1. elliptic shifted factorials and determinant transformations involving them, for example H. Rosengren, *An elliptic determinant transformation*, arXiv:math/0505248;
2. cyclic quantum dilogarithms at roots of unity and their mutation identities, for example I. C.-H. Ip and M. Yamazaki, *Quantum Dilogarithm Identities at Root of Unity*, arXiv:1412.5777;
3. root-of-unity limits of elliptic gamma functions producing finite discrete-spin structures, for example A. P. Kels and M. Yamazaki, arXiv:1709.07148.

These references establish that finite root-of-unity products and elliptic shifted factorials form a real special-function class. They do not, as far as the present audit identified, provide the required algorithm below.

In particular, the cyclic-dilogarithm framework uses root-of-unity central characters and cyclic variables that amount to choosing roots or full finite-dimensional cyclic states. Such data cannot be imported here without charging its representation and branch cost.

This is a literature-audit conclusion, not a theorem of nonexistence.

## 4. Exact success gate

A positive B12 result must provide all of the following:

```text
Input:       public finite-field E,G,Q=[k]G only.
Output:      H_G(Q), its zero/pole orientation, or directly (-1)^k.
Correctness: exact algebraic identity over the target finite field.
Orientation: output changes correctly under G -> -G.
State:       no table of M signs, no dual point, no full zeta_n^k phase.
Cost:        preprocessing+advice+representation+memory+online
             =O(n^(1/2-epsilon)).
```

A new name for the length-`M` product, a complex analytic formula without finite-field descent, or a root-of-unity representation of dimension `n` is not a successful evaluator.

## 5. Current evidence

Packages B4-B11 show:

```text
explicit product                         length M,
ordinary Miller monomial replacement    linear number of atoms,
subgroup multiplication formula         full kernel only,
explicit resultant/index trees          square-root state,
linear/transposed character state       support n,
local two-step edge                      compact,
global endpoint value                   unresolved.
```

Therefore B12 is the last clearly identified B-specific nonlinear route. Its unresolved question is whether the special-function notation hides a genuinely shorter finite-field circuit or merely repackages the same dense cyclic product.

## 6. Coordination with track A

Track A studies endpoint segment composition abstractly. B12 supplies the most structured special-function candidate for that endpoint primitive. A positive identity discovered in either track should be checked against `(B12.2)` and the all-in cost gate above.
