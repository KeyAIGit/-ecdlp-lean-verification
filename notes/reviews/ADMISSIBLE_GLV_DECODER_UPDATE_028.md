# Admissible GLV Decoder Update after THETA-SPLITTING-DUALITY-028

Date: 2026-08-12

Status: **successor refinement to the synchronized decoder contract**.

## 1. What package 028 closes

For a standard multiplicative theta/sigma splitting over the prime-order group
`H=<G>`, the ratio of two splittings is a character of `H`.

Since `n=|H|` is odd prime, such a character is either:

```text
trivial, or
faithful of full order n.
```

There is no nontrivial binary or bounded-order homomorphic quotient.  Hence a
standard generator-sensitive splitting cannot itself expose only the GLV carry
bit.  It either remains generator-blind or introduces the full order-`n` dual
phase.

This closes one open mechanism class from the original admissible-decoder map:

```text
standard multiplicative bit-only theta/sigma splitting.
```

It does not close a nonlinear circuit that consumes the full phase only
implicitly.

## 2. Exact nonlinear representation

After choosing the faithful generator-oriented character

```text
chi_G([k]G)=zeta_n^k,
```

the carry has the exact cyclotomic representation

```text
Cut_G(Q)=B_G(chi_G(Q)),
B_G(z)=sign Im((1-z)(1-z^lambda)(1-z^(lambda^2))).
```

For `Q=[k]G`, this equals

```text
g_G(Q).
```

Thus two exact but currently inadmissible representations are now explicit:

```text
algebraic half-kernel:
  H_G(Y)=product_(carry-positive C3 orbits)(Y-y(P));

cyclotomic triple cut:
  B_G(chi_G(Q)).
```

The first materializes `(n-1)/6` roots or comparable state.  The second
materializes or evaluates a faithful order-`n` phase.  Neither is presently a
sub-square-root decoder.

## 3. Refined single open object

The synchronized successor is

```text
GLV-TRIPLE-CUT-EVALUATOR.
```

> Can `B_G(chi_G(Q))` be evaluated exactly from public `(E,G,phi,Q)` with total
> time, memory, preprocessing, advice and precision
> `O(n^(1/2-epsilon))`, without evaluating or storing a faithful order-`n`
> character and without materializing the equivalent generator-oriented
> half-kernel partition?

This is equivalent to the half-kernel membership question and to exact public
evaluation of `R3_G(Q)` through the public bridge

```text
C3_G(Q)=g_G(Q)R3_G(Q).
```

## 4. Admitted constructive mechanisms after 028

Only mechanisms that genuinely bypass both explicit large representations
remain admitted:

1. a direct zero-sum GLV triple resolvent in bounded-rank theta/net/sigma data;
2. a high-degree but uniformly generated low-circuit base-field identity;
3. a canonical p-adic or analytic exact evaluator whose branch and precision
   are public and costed;
4. a nonlocal order-dependent EDS section outside the closed homogeneous
   category and surviving the public-factor quotient gate.

A new splitting, phase lookup, broad ML screen, or kernel polynomial is not a
new route unless it supplies an exact identity for the nonlinear cut and meets
the complete `D_adm` cost contract.

## 5. Updated existence answer

```text
Does an exact public mathematical representation exist?       yes
Does a standard binary theta splitting provide it?            no
Does a full order-n phase plus nonlinear cut provide it?       yes
Is that representation currently admissible below sqrt(n)?    no
Is a different admissible evaluator ruled out universally?     no
```

The research problem is now a representation-compression problem for one exact
nonlinear cut, not a search for another hidden bit.
