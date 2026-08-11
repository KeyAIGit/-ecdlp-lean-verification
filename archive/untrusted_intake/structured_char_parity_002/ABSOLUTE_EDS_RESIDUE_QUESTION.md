# ABSOLUTE-EDS-RESIDUE-QUESTION

Date: 2026-08-11

Status: **isolated untrusted research note**. This file is intentionally kept on
`research/structured-char-parity-002`, outside draft PR #365 and outside
canonical Research Engine state. It authorizes no unknown-target computation,
claims no ECDLP improvement, and must not be merged without independent source
review.

## 1. Exact object

Let `E/F_q` be an elliptic curve, let `G` have odd prime order `n`, and let

```text
Q = [k]G,   0 <= k < n.
```

Write

```text
W_G(t) = psi_t(G),
rho_G(Q) = chi(W_G(k)),
```

where `psi_t` is the `t`-th division polynomial and `chi` is the quadratic
character of `F_q`.

The word **residue** means quadratic residue: `rho_G(Q)=+1` when `W_G(k)` is a
nonzero square and `rho_G(Q)=-1` when it is a nonsquare. It is not an integer
remainder.

An **elliptic divisibility sequence (EDS)** is the indexed sequence
`W_G(t)=psi_t(G)`. It satisfies the elliptic-net/Ward recurrence and can be
evaluated quickly when the index `t` is known. The difficulty here is that the
needed index is the unknown discrete logarithm `k`.

The central question is:

```text
Given public (E,G,Q), can rho_G(Q) be computed exactly below the matched
square-root generic baseline without first recovering k?
```

For the secp256k1 specialization recorded on `research/parity-lift-000`, the
public periodic point function supplies a public factor and turns this residue
bit into canonical scalar parity. Consequently an exact cheap residue oracle
would imply an exact cheap parity oracle and then full scalar recovery by
adaptive bit peeling.

## 2. What would count as a positive answer

A positive result requires all of the following, not merely a correlation or a
toy interpolation:

1. an explicit public algorithm `A(E,G,Q)`;
2. a theorem proving `A(E,G,[k]G)=chi(psi_k(G))` for every canonical `k`;
3. complete treatment of zeros, poles, charts, exceptional points, extension
   fields, and normalization choices;
4. an online cost theorem below the matched square-root baseline, including
   preprocessing, memory, precision, and every adaptive call;
5. no hidden table, unknown-index walk, or preprocessing of square-root size;
6. independent replay and then formalization of the load-bearing identities.

A formula of high algebraic degree is allowed if its actual circuit or recurrence
cost is low. Degree alone is not the cost metric.

## 3. What would count as a negative answer

A universal negative answer for every coordinate-sensitive algorithm would be a
very strong non-generic ECDLP lower bound. The realistic route is therefore
class-by-class:

1. define a precise observable/circuit family `C`;
2. identify a symmetry, balance law, gauge ambiguity, divisor restriction, or
   correlation bound shared by every member of `C`;
3. prove the absolute residue bit violates that invariant;
4. conclude that no member of `C` computes `rho_G` exactly;
5. enlarge `C` only after the theorem is independently reviewed.

Draft PR #365 already performs this for several classes, including sign-erasing
representations and finite products or ratios of fixed-index transported
division-polynomial observables.

## 4. Public reindex-collapse identity

A tempting loophole is:

```text
choose a public invertible m,
R = [m^(-1) mod n]Q,
return chi(psi_m(R)).
```

Naively, because `m` may be even, the denominator in the elliptic-net transport
law has even exponent and appears to disappear under the quadratic character.
This does **not** expose the absolute residue.

Assume the standard perfectly periodic normalization

```text
W_tilde_G(t) = Phi([t]G) = a^(t^2-1) W_G(t),
a = Phi(G).
```

For `R=[t]G`, the rank-one elliptic-net transformation law gives

```text
psi_m(R) = W_G(m*t) / W_G(t)^(m^2).
```

Substituting the periodic normalization gives the exact identity

```text
psi_m(R)
  = a^(1-m^2) * Phi([m]R) / Phi(R)^(m^2).
```

Indeed, the hidden `t^2` exponents cancel:

```text
-(m*t)^2 + 1 + m^2*(t^2-1) = 1-m^2.
```

Taking quadratic characters therefore yields

```text
chi(psi_m(R))
  = chi(a)^(1-m^2)
    * chi(Phi([m]R))
    * chi(Phi(R))^(m^2).
```

Every term on the right is public. In particular, if
`R=[m^(-1) mod n]Q`, then `[m]R=Q`, so the proposed observable collapses to
public normalized-periodic data. It does not isolate `rho_G(Q)`.

This identity does not prove that `chi(psi_m(R))` can never accidentally equal
`rho_G(Q)` for a special fixed family. It closes the specific mechanism claim
that inverse-scalar reindexing removes the hidden denominator and thereby
reveals the absolute residue.

Proposed theorem package:

```text
PUBLIC-REINDEX-COLLAPSE-001
```

with two layers:

- a small kernel-checked exponent identity;
- a source-pinned mathematical statement of the elliptic-net and periodic
  normalization assumptions.

## 5. Current surviving mechanism classes

After the existing fixed-index balance result and the reindex-collapse identity,
a positive mechanism must be genuinely unbalanced. The main surviving classes
are:

1. an unbalanced theta, sigma, or elliptic-net section whose public evaluation
   retains the absolute scaling orientation;
2. a nonlocal statistic that reconstructs the absolute sign from public
   relative EDS data without walking the unknown index;
3. a p-adic or analytic normalization with exact branch selection and a proved
   precision/cost theorem;
4. a multi-point or multi-model relation that breaks quadratic balance without
   smuggling in equivalent hidden input;
5. a structured high-degree circuit that is not reducible to fixed-index
   transport, public scalar reindexing, or a sign-erasing quotient.

## 6. Immediate decision tree

For every proposed observable `F(G,Q)`:

```text
A. Does it identify Q and -Q?
   yes -> reject.

B. Is it a fixed-index division-polynomial product/ratio transported from Q?
   yes -> apply fixed-index quadratic balance.

C. Is it obtained by public scalar precomposition or inverse-scalar reindexing?
   yes -> apply public reindex collapse / Fourier reindexing.

D. Does it use only publicly normalized periodic EDS values or their bounded
   relative ratios?
   yes -> demand an explicit theorem showing where the absolute gauge is fixed.

E. Does it retain an absolute orientation?
   yes -> prove exact correctness, then price circuit, preprocessing, memory,
   precision, and all adaptive calls.
```

## 7. Highest-value next questions

The next useful work is not another broad search for a coordinate. It is one of
these falsifiable statements:

```text
RELATIVE-DATA-GAUGE-002
```

Classify the transformations of an EDS that preserve every publicly computable
bounded relative-residue observation, and determine whether `rho_G(Q)` changes
under any surviving transformation.

```text
AFFINE-INDEX-BALANCE-003
```

Extend fixed-index balance from `m*k` to a precisely defined family of affine
index expressions and nonlocal cycles, retaining canonical-wrap factors rather
than silently reducing indices modulo `n`.

```text
UNBALANCED-SECTION-SEARCH-004
```

Search only for sections with a source-pinned transformation law containing a
non-cancelling absolute exponent, followed immediately by a total evaluation
cost theorem.

A proof of `RELATIVE-DATA-GAUGE-002` for a broad enough class would be a genuine
negative answer for that class. An explicit construction passing all six
positive-result requirements would be a genuine positive answer.
