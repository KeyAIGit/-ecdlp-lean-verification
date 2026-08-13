# P-ADIC-GLOBAL-BRANCH-054

Date: 2026-08-13

Status: **standard p-adic sigma and formal-group methods are local to the kernel of reduction. Nonzero prime-to-p subgroup points do not enter that neighborhood under any known scalar not divisible by the subgroup order; the first universal multiplier that enters is the order itself and annihilates the point. Canonical lifting transports the subgroup but does not select the marked branch, while Hensel lifting preserves rather than creates an initial square-root choice.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Target

The exact marked root remains

```text
Y_G(X)^2 = X^3+7 mod K_H(X),
Y_G(x([k]G))/y([k]G)=(-1)^k.                     (P1)
```

After packages 047-053, the next possible source of global orientation is a p-adic sigma function, formal logarithm, canonical lift, or Coleman continuation.

## 2. Domain of the p-adic sigma function

The Mazur-Tate p-adic sigma function is naturally defined on the formal group, equivalently the kernel of reduction

```text
E_1(K)=ker(E(K)->E(k)).                           (P2)
```

Its power series is normalized at the identity and converges for a formal parameter of positive valuation.

A nonzero point of the public prime-order subgroup has nonzero reduction. Therefore it is not in `E_1`.

## 3. Known scalar multiplication cannot move the target locally

Let `Q=[k]G` with `1<=k<n` and `n` prime. For a known integer `m`,

```text
[m]Q reduces to O
iff mk=0 mod n
iff m=0 mod n.                                   (P3)
```

Thus no known multiplier smaller than or coprime to `n` moves an arbitrary nonzero target into the formal group.

The first universal multiplier is `m=n`, but

```text
[n]Q=O.                                          (P4)
```

At that point all information about `k` has been erased.

## 4. Formal logarithm on prime-to-p torsion

Whenever a p-adic logarithm is defined and respects multiplication,

```text
log([n]P)=n log(P).                               (P5)
```

For prime-to-p torsion, `[n]P=O` and `n` is a p-adic unit, hence

```text
log(P)=0.                                        (P6)
```

The formal logarithm cannot distinguish the different points of the finite prime-to-p torsion subgroup.

## 5. Canonical lift does not orient the subgroup

secp256k1 is ordinary, so its reduction admits a canonical lift. Prime-to-p torsion points lift through the finite etale torsion scheme.

This transports the public subgroup and the Frobenius/CM action to characteristic zero. It does not distinguish the marked generator from its inverse or choose the correlated signs in `Y_G`.

The compact endomorphism description

```text
H=ker(Frob-1)                                    (P7)
```

is subgroup data. Packages 027 and 046 show that subgroup-only data cannot choose between the roots attached to `G` and `-G`.

## 6. Hensel and Newton lifting preserve an initial branch

Suppose a square root in the Kummer algebra is lifted p-adically by Newton iteration. The iteration requires a starting root modulo `p`.

For every component, the two possible seeds are

```text
+y(P), -y(P).                                    (P8)
```

Hensel lifting uniquely continues the selected seed; it does not decide which seed belongs to `Y_G`.

Therefore p-adic precision can refine an orientation, but cannot create the missing generator-relative orientation from the unoriented equation

```text
Y^2=X^3+7 mod K_H.                               (P9)
```

## 7. Base-field p-adic characters

For the frozen curves and secp256k1,

```text
gcd(n,p-1)=1.                                    (P10)
```

Hence the base field contains no nontrivial `n`-th roots of unity. A multiplicative p-adic character of the order-`n` subgroup into the base field is trivial.

Adjoining the full dual character again requires the extension degree

```text
ord_n(p)=(n-1)/6                                 (P11)
```

for secp256k1, the same explicit obstruction isolated in the theta/pairing packages.

## 8. Coleman and third-kind integrals

A global Coleman integral of the invariant differential reduces to the p-adic logarithm and vanishes on prime-to-p torsion.

Differentials of the third kind can retain torsion information through multiplicative periods and pairings. But then the value is a Tate/Weil-pairing or dual-character object. Packages 032-038 show that the required dual phase is either defined in a huge extension or disappears under canonical symmetric descent.

Thus a Coleman construction is useful only if it exhibits a new generator-sensitive branch constant not equivalent to:

```text
formal logarithm,
standard pairing,
full dual character,
initial Hensel seed,
explicit signed row factor.
```

No such constant is presently identified.

## 9. Frozen exact replay

`p_adic_global_branch.py` checks the six frozen public pairs `(p,n)`:

```text
(151,19), (43,31), (79,67),
(1087,271), (2851,397), (1663,433).
```

It verifies:

1. `gcd(n,p)=gcd(n,p-1)=1`;
2. every nonzero scalar remains outside the reduction kernel under all declared known multipliers not divisible by `n`;
3. multiplication by `n` sends every scalar to zero;
4. no nontrivial base-field order-`n` character exists;
5. the number of independent componentwise square-root choices is `2^((n-1)/2)`.

The secp256k1 certificate checks ordinarity, the same coprimality conditions, the half-Frobenius congruence, and the formal-neighborhood obstruction. No unknown target is evaluated.

## 10. Answer

```text
Can formal sigma evaluate arbitrary nonzero subgroup points?     no
Can a known scalar move them into the formal group?              only multiples of n
What does the first universal such multiplier do?                annihilates the point
Does the formal logarithm distinguish prime-to-p torsion?        no; it vanishes
Does the canonical lift choose Y_G?                              no
Does Hensel lifting choose the initial branch?                   no
Does base-field p-adic character theory expose k?               no
Public parity / absolute EDS-residue decoder                     absent
Unconditional classical sub-sqrt ECDLP                          absent
```

## 11. Closed and open classes

Closed within this package:

```text
formal-group sigma evaluation without a global entry mechanism,
formal logarithm on prime-to-p torsion,
known-scalar movement into the kernel of reduction,
canonical lift as subgroup-only orientation,
Hensel/Newton lifting without an independently supplied branch seed,
base-field p-adic characters.
```

Still open:

1. a genuinely new Coleman third-kind cocycle not reducible to a pairing;
2. a global overconvergent function with a generator-sensitive branch constant;
3. an arithmetic circuit evaluating `Y_G(x(Q))` without formal localization;
4. a general circuit lower bound for the marked square-root problem.

## 12. Strategic successor

The next narrow package is

```text
COLEMAN-THIRD-KIND-COCYCLE-055.
```

It must decide whether a third-kind integral between public torsion points yields anything beyond a Tate-pairing/dual-character value. The package will derive the transformation law, identify every period and branch constant, and reject any construction whose nontriviality is supplied by an uncharged dual point or path choice.

If package 055 also collapses, the natural algebraic, theta, pairing, and p-adic analytic routes will all have scoped closures. The remaining central object will be an unrestricted uniform branch-evaluation circuit for `Y_G`, together with an explicit cost model or a new structural identity.