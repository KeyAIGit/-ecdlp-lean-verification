# THETA-SPLITTING-DUALITY-028

Date: 2026-08-12

Status: **theorem-first scoped decision for standard generator-sensitive theta/sigma splittings**.

No external point, private key, wallet, or production-sized discrete-log instance is accepted. This package constructs no carry, R3, parity, or ECDLP decoder.

## 1. Next object

Let

```text
1 -> M -> T -> H -> 1
```

be a central phase extension over the public prime-order subgroup

```text
H=<G>,   |H|=n.
```

Let `s1,s2 : H -> T` be two multiplicative splittings of the same projection. The exact object controlling the change of theta/sigma normalization is

```text
chi_12(Q)=s1(Q) s2(Q)^(-1).
```

Because the two lifts project to the same point of `H`, their ratio lies in the central phase group `M`. Centrality and multiplicativity imply

```text
chi_12(P+Q)=chi_12(P) chi_12(Q).
```

Thus the ratio of two standard splittings is a character of `H`.

This is the correct object to study after `GENERATOR-ORIENTED-HALF-KERNEL-027`: a generator-sensitive normalization can differ from a generator-blind normalization only through such a dual character, unless the construction leaves the standard homomorphic-splitting category.

## 2. Prime-order dichotomy

Assume `n` is prime. A character of `H` has image order dividing `n`. Therefore exactly two cases exist:

```text
trivial character:      image order 1;
nontrivial character:   image order n and zero kernel.
```

Equivalently, after choosing `G` and a primitive `n`-th root of unity,

```text
chi_a([k]G)=zeta_n^(a*k).
```

If `a=0 mod n`, the character is trivial. If `a!=0 mod n`, multiplication by `a` is a permutation of `Z/nZ`, so `chi_a` is faithful and has full order `n`.

There is no intermediate nontrivial character carrying only a bounded number of states.

## 3. No binary homomorphic quotient

Since `n` is odd, every homomorphism

```text
H -> {+1,-1}
```

is trivial. The image order must divide both `n` and `2`, hence is one.

An elementary generator proof is equally direct. If `x` is the image of `G`, then

```text
x^n=1,
x^2=1.
```

Writing `n=2m+1` gives

```text
1=x^n=(x^2)^m x=x,
```

so `x=1`.

Therefore a standard theta/sigma splitting cannot provide a nontrivial one-bit phase as a homomorphic quotient. It either adds no generator information or introduces a full order-`n` dual character.

## 4. Relation to elliptic-net normalization

Elliptic nets admit multiplication by quadratic scaling forms, and normalization is defined only after choosing a preferred basis. For a non-degenerate net the normalized scaling is then unique. This is compatible with the present result: changing a genuine linearization while preserving the projected points introduces phase data governed by characters, while the ordinary quadratic net scaling remains a separate normalization layer.

This package does not claim that all nonlinear theta expressions are characters. It classifies the ratio of standard multiplicative splittings.

## 5. Consequence for the carry problem

The exact carry cut is already known on the cyclotomic cover. If

```text
z=chi_G(Q)=zeta_n^k,
```

then

```text
B_G(z)=sign Im((1-z)(1-z^lambda)(1-z^(lambda^2)))
      =g_G(Q).
```

`B_G` is deliberately nonlinear and is not a character. The prime-order dichotomy shows why this nonlinearity is unavoidable:

```text
standard splitting -> full order-n phase z;
bit output          -> nonlinear cut B_G(z).
```

The missing algorithmic operation is not the definition of `B_G`; it is a public compressed evaluation of `B_G(chi_G(Q))` without materializing or otherwise computing the full dual character.

## 6. Answer to package 028

```text
Does the ratio of standard splittings form a character?          yes
Can a nontrivial such character have bounded or binary order?    no
Can a homomorphic bit-only theta quotient exist for odd n?       no
Does a nontrivial splitting difference carry full order n?       yes
Is a nonlinear compressed carry evaluator known?                 no
```

Accordingly, the standard splitting route has a scoped no-go:

> A generator-sensitive standard theta/sigma linearization cannot expose only a nontrivial binary phase. In a prime-order subgroup it is either generator-blind or differs by a faithful order-`n` dual character.

This does not rule out a nonhomomorphic circuit that evaluates only the GLV carry cut without reconstructing the full character.

## 7. Next object

The successor is

```text
GLV-TRIPLE-CUT-EVALUATOR-029.
```

Its exact object is the composite

```text
Cut_G(Q)=B_G(chi_G(Q)),

B_G(z)=sign Im((1-z)(1-z^lambda)(1-z^(lambda^2))).
```

The question is no longer whether a theta splitting can be compressed to a smaller character. It cannot in the standard prime-order category. The question becomes:

> Can the nonlinear zero-sum GLV triple cut be evaluated directly from `(E,G,Q)` with total time, memory, preprocessing, advice, and precision `O(n^(1/2-epsilon))`, without evaluating a faithful order-`n` character?

### Obligations for package 029

1. Formalize the exact `C3` invariance and negation anti-invariance of `B_G`.
2. Express `B_G` as a zero-sum triple resolvent and remove every phase factor that cancels publicly.
3. Classify direct theta/net/sigma triple products that evaluate the resolvent without individual dual-character values.
4. Prove either a compact black-box evaluation identity or a scoped obstruction for Frobenius-invariant, bounded-rank, and standard line-function representations.
5. Count all preprocessing and advice. A table, factor, or circuit of size `Omega(sqrt(n))` is not admitted.
6. Promote only an exact decoder with a literal carry-to-ECDLP reduction.

No new broad ML or arbitrary character lookup is admitted without a new exact identity.

## 8. Formalization boundary

`Ecdlp/Proved/ThetaSplittingDuality.lean` formalizes:

```text
ratio of multiplicative phase homomorphisms is a homomorphism;
odd-order binary phase with x^n=x^2=1 is trivial;
nonzero exponent multiplication on ZMod p is injective for prime p.
```

Lean does not formalize central extensions, theta groups, sigma functions, or the identification of every geometric linearization with a multiplicative splitting. Those are the explicit geometric premises of this scoped result.
