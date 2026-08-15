# UORC-056 — IDEMPOTENT-FACTORIZATION-V16

Status: exact algebraic reduction; no public parity evaluator and no sub-root algorithm claimed.

## 1. Starting point

V15 isolates two generator-sensitive sign objects on the marked subgroup:

- sector involution `J_G(X)` with `J_G^2 = 1 mod K_H` and `J_G(X)J_G(beta X)J_G(beta^2 X)=1`;
- carry involution `L_G(T)` with `L_G^2 = 1 mod kappa_H`, where `K_H(X)=kappa_H(X^3)` on the GLV-stable half-kernel.

The central parity evaluator factors as

`(-1)^k = chi(y(Q)) L_G(x(Q)^3) J_G(x(Q))`.

This package identifies the exact algebraic content of computing either involution.

## 2. Involutions are equivalent to binary kernel factorizations

Let `F` be a field of odd characteristic, let `K in F[X]` be squarefree, and let

`R = F[X]/(K)`.

For any `J in R` satisfying `J^2=1`, define

`e_+ = (1+J)/2`, `e_- = (1-J)/2`.

Then exactly in `R`:

- `e_+^2=e_+`, `e_-^2=e_-`;
- `e_+e_-=0`;
- `e_++e_-=1`;
- `J=e_+-e_-`.

Because `K` is squarefree, `R` is a product of residue fields over the irreducible factors of `K`. Hence `J` selects a sign independently on every geometric root orbit. Equivalently there is a coprime factorization

`K = K_+ K_-`

such that on roots of `K_+`, `J=+1`, and on roots of `K_-`, `J=-1`.

Conversely, any coprime factorization `K=K_+K_-` determines a unique involution by CRT:

`J = +1 mod K_+`,
`J = -1 mod K_-`.

Thus exact evaluation of a generator-sensitive involution is not merely a polynomial interpolation problem. It is an oriented factor-membership problem for a generator-dependent partition of the public kernel roots.

## 3. Sector factorization

Apply the theorem to `J_G` in

`R_H = F_p[X]/(K_H)`.

Define

`K_H = K_{J,+} K_{J,-}`

where roots are partitioned by `kappa_0=+1` versus `kappa_0=-1`.

Then evaluating `J_G(x(Q))` is exactly deciding which oriented factor contains `x(Q)`.

The GLV constraint

`J_G(X) J_G(beta X) J_G(beta^2 X)=1`

imposes a non-arbitrary orbit law on this factorization: every size-three GLV orbit of roots has an even number of minus signs. Therefore the allowed local sector patterns are precisely

`(+++)`, `(+--)`, `(-+-)`, `(--+)`.

This recovers the V15 Klein-four state space directly at the factorization level.

Important consequence: a future compact sector evaluator must compress this oriented binary factorization, not just approximate the dense representative of `J_G`.

## 4. Carry factorization

Likewise write

`kappa_H(T) = K_{L,+}(T) K_{L,-}(T)`

according to `L_G(T)=+1` or `-1`.

The carry bit at `Q` is

`c(Q)=chi(y(Q)) L_G(x(Q)^3)`.

Thus the hidden part of carry is exactly factor membership in a generator-sensitive partition of the smaller GLV quotient kernel.

This makes the factor-three degree reduction from V15 conceptually exact: GLV has removed the orbit label, but not the oriented partition.

## 5. Explicit CRT representative

If `K=K_+K_-` with `gcd(K_+,K_-)=1`, choose Bezout coefficients

`a K_+ + b K_- = 1`.

Then one representative is

`J = b K_- - a K_+ mod K`.

Indeed it is `+1 mod K_+` and `-1 mod K_-`.

Therefore any proposal that stores both factors densely already costs Theta(deg K) field elements. Beating the root barrier requires a compressed description of the factors or a membership algorithm that never materializes them.

This is a representation observation, not an unrestricted circuit lower bound.

## 6. Revised compression target

The correct V16 target is no longer simply

`find a short polynomial for J_G or L_G`.

It is:

> Given public `(E,G,Q)` and charged preprocessing/advice, decide membership of `x(Q)` (or `x(Q)^3`) in the generator-oriented factor of the corresponding kernel polynomial in total cost `o(sqrt(n))`.

Equivalent candidate representations to test:

1. compact arithmetic circuits for factor-membership;
2. recursive/product-tree descriptions of the oriented factors;
3. norm/trace towers compatible with GLV orbits;
4. elliptic-unit or theta descriptions whose divisors equal the oriented partition;
5. low-state recurrences that update factor membership under doubling/addition;
6. transposed modular evaluation without dense factor construction.

## 7. Immediate no-go screen

Any proposed representation should be rejected if it only supplies:

- the unordered public kernel `K_H` or `kappa_H`;
- GLV-invariant multiplicative division-polynomial characters (closed by V13);
- a dense list of oriented roots/factor coefficients hidden in advice;
- per-curve fitted labels whose storage is linear in the kernel degree;
- a sequential walk whose state is constant-size but whose number of steps is Theta(k) or Theta(n).

All preprocessing, representation construction, memory, advice, branching and online evaluation remain charged.

## 8. New structural question

The strongest next theorem would show that the oriented factors `K_{J,+},K_{J,-}` or `K_{L,+},K_{L,-}` have no uniformly constructible representation of sub-root total complexity inside a clearly specified model.

The strongest positive result would instead exhibit a recursive identity of the form

`State(2m) = F(State(m), public data at [m]G)`

or an addition-chain analogue, where the state determines oriented factor membership and has `polylog(n)` size.

That is now the highest-value search: not another finite formula grammar, but a recursion for the oriented idempotent/factor partition.

## 9. Scope discipline

This reduction does NOT prove:

- that `J_G` or `L_G` requires linear representation in every circuit model;
- that no sub-root parity evaluator exists;
- that generic-group lower bounds automatically apply to these algebraic representations.

It DOES prove the exact equivalence between the V15 involutions and generator-oriented CRT partitions of their squarefree kernel algebras. This gives a sharper semantic target for both constructive and lower-bound work.