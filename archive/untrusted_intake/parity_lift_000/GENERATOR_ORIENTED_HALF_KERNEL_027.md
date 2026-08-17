# GENERATOR-ORIENTED-HALF-KERNEL-027

Date: 2026-08-12

Status: **theorem-first generator-covariance and generator-blindness decision**.

No external point, key, wallet, or production-sized discrete-log instance is
accepted. This package constructs no carry, R3, parity, or ECDLP decoder.

## 1. Question

Let `H=<G>` be the public prime-order subgroup and let

```text
Q=[k]G.
```

The generator-relative GLV carry is

```text
g_G(Q)=(-1)^gamma,
```

where the three canonical representatives of

```text
Q, phi(Q), phi^2(Q)
```

sum to `gamma*n`, with `gamma in {1,2}`.

The exact half-kernel specification is

```text
H_G(Y)=product_(carry-positive C3 orbits) (Y-y_orbit),
H_G(y(Q))=0 iff g_G(Q)=+1.
```

The package asks whether the degree-`n` CM isogeny with kernel `H`, its
conjugate, Frobenius, and ordinary theta/net normalization can select `H_G`
rather than another half factor.

## 2. Exact generator-change covariance

Replace the generator by

```text
G'=[u]G,     u in (Z/nZ)^*.
```

If `Q=[k]G`, then relative to `G'` its canonical scalar is

```text
k'=[u^(-1)k]_n.
```

Therefore the carry satisfies the exact covariance law

```text
g_[uG](Q)=g_G([u^(-1)]Q).                         (C1)
```

Let

```text
S_G={Q in H\{O}: g_G(Q)=+1}.
```

Then

```text
S_[uG]=[u]S_G.                                    (C2)
```

Consequently the oriented root factor transforms as

```text
H_[uG](Y)
  = product_(P in S_G/C3) (Y-y([u]P)).            (C3)
```

This is not an ordinary fixed substitution in `Y`; multiplication by `u`
permutes the subgroup before the y-coordinate is taken.

For the concrete GLV units,

```text
H_[lambda^j G](Y)=H_G(Y),
```

because the order-three automorphism preserves the horizontal C3 orbit and its
common y-coordinate.

For the negative coset,

```text
H_[-lambda^j G](Y)=(-1)^d H_G(-Y),
d=(n-1)/6.                                        (C4)
```

Thus `G` and `-G` require complementary oriented factors.

## 3. Generator-blindness theorem

The subgroup and every kernel-only object are unchanged by

```text
G -> -G:
<G>=<-G>.
```

In particular, a CM endomorphism or isogeny selected only by its kernel, its
kernel polynomial, its quotient curve, its conjugate, and Frobenius is the same
for `G` and `-G`.

But the desired labels are opposite:

```text
g_[-G](Q)=g_G(-Q)=-g_G(Q)
```

for every nonzero `Q`, and equation (C4) swaps the two root halves.

Therefore:

> A deterministic construction that depends only on the subgroup kernel or on
> the corresponding un-oriented CM isogeny cannot be a correct
> generator-relative half-kernel selector for both `G` and `-G`.

This is an exact logical obstruction, not a heuristic complexity claim.

The new Lean file
`Ecdlp/Proved/GeneratorOrientationBlindness.lean` formalizes the abstract
statement that a generator-blind decoder cannot equal two complementary
generator-relative targets.

## 4. Exhaustive toy covariance

The frozen verifier examines all nonzero generator multipliers on fifteen
prime-order `j=0` toy subgroups.

It verifies:

```text
g_[uG](Q)=g_G([u^(-1)]Q)
```

for every nonzero scalar pair `(u,Q)`.

It also records the orientation signature across all C6 orbit pairs. On every
frozen case:

```text
number of distinct oriented signatures = (n-1)/3,
stabilizer of H_G                      = <lambda>,
complementary-signature coset          = -<lambda>.
```

Thus modulo the order-three GLV relabeling there is a separate oriented factor
for every generator class. Modulo global negation there are `(n-1)/6`
unoriented pairs.

The toy result is evidence for the full stabilizer statement. The `G` versus
`-G` generator-blindness contradiction does not depend on the toy screen.

## 5. What extra datum is missing

A theta or sigma construction that acts on the kernel needs a
generator-sensitive **linearization** or **splitting** to orient it.

Abstractly, if two multiplicative splittings of the same central phase
extension exist, their pointwise ratio is a character of the cyclic subgroup.
Conversely a splitting can be twisted by any subgroup character. Thus the
space of possible phase normalizations is a torsor under the dual group

```text
Hom(H, mu_n).
```

After choosing `G`, a nontrivial member has the form

```text
[k]G -> zeta_n^(a*k).
```

This is exactly the dual-character object isolated by
`GLOBAL-MONODROMY-SECTION-009`.

Therefore adding a genuine generator-sensitive theta linearization does not
magically bypass the previous bottleneck. It supplies, or must compactly
evaluate, the same missing dual phase.

For secp256k1:

```text
gcd(n,p-1)=1,
ord_n(p)=(n-1)/6.
```

Hence no nontrivial `H -> F_p^*` character exists, and a standard explicit
`mu_n` realization requires the already-recorded enormous extension degree.
This does not rule out a compressed bit-only realization, but it rules out an
ordinary base-field character or generator-blind CM normalization.

## 6. Answer to package 027

The answer is split.

```text
Can alpha/kernel alone select H_G?                     no
Can an un-oriented compact CM factorization do so?     no
Can an added generator-sensitive theta splitting?      only if it supplies
                                                       the missing dual phase
Is a sub-sqrt compressed splitting known?              no
```

Accordingly, stages 1-3 of the previous package formulation are not an
independent route. Without an explicit generator-sensitive splitting they are
generator-blind. With such a splitting they reduce to the dual-character
compression problem already isolated.

Package 027 therefore closes at Stage 0 as a scoped no-go for **kernel-only CM
half-factor selection**.

## 7. Next package

```text
THETA-SPLITTING-DUALITY-028
```

Central question:

> Does there exist a public generator-sensitive theta/sigma linearization whose
> evaluation supplies only the bit needed for `g_G(Q)` or hard-branch `R3(Q)`,
> with total time, memory, preprocessing, advice, and precision
> `O(n^(1/2-epsilon))`, without materializing a nontrivial order-`n` dual
> character?

The theorem-first obligations are:

1. formalize the ratio-of-splittings character law;
2. prove that every standard theta linearization over `<G>` differs by an
   order-`n` dual character;
3. classify which nonlinear function of that phase is sufficient for GLV carry;
4. audit whether bit-only evaluation can avoid representing `mu_n` or an
   equivalent `n`-state object;
5. obtain either a costed compressed construction or a scoped lower bound for
   the specified representation.

No new broad ML, lookup, bounded rational-function, or kernel-polynomial screen
is admitted without a new exact identity.
