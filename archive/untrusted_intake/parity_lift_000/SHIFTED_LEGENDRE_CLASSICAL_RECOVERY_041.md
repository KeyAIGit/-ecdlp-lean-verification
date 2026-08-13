# SHIFTED-LEGENDRE-CLASSICAL-RECOVERY-041

Date: 2026-08-12

Status: **an exact scalar-Legendre oracle gives logarithmic information-theoretic query complexity but no established classical sub-square-root recovery algorithm; the Legendre branch is therefore not yet an asymptotic ECDLP route even if its projector were free**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Decision question

Assume an exact unit-cost oracle

```text
O(P)=chi_n(log_G(P))
```

for every nonzero point in the public prime-order subgroup.

For

```text
Q=[k]G,
```

public group operations permit queries on

```text
[t]Q+[a]G=[t*k+a]G,
```

so the oracle returns

```text
chi_n(t*k+a).
```

The question is whether these queries recover `k` classically in complete

```text
O(n^(1/2-epsilon))
```

time, queries, memory, preprocessing, and advice.

## 2. All affine queries reduce to one shifted Legendre oracle

For every nonzero `t`,

```text
t*k+a=t*(k+a/t),
```

and multiplicativity gives

```text
chi_n(t*k+a)=chi_n(t) chi_n(k+a/t).               (L1)
```

The factor `chi_n(t)` and shifted input `a/t` are public. Therefore all public affine curve queries reduce to the standard shifted Legendre sequence

```text
L_k(x)=chi_n(k+x).                                (L2)
```

GLV scaling does not create a richer oracle; it only chooses another public nonzero `t` in `(L1)`.

## 3. Exact autocorrelation

For shifts `s,t in F_n`,

```text
sum_(x in F_n) L_s(x)L_t(x)
 = n-1,  s=t,
 = -1,   s!=t.                                   (L3)
```

Thus the full correlation with the known Legendre sequence has a unique peak at the hidden shift.

A literal classical correlation algorithm uses all `n` oracle values and `O(n log n)` arithmetic through an FFT, or `O(n^2)` without it. This is far above the Pollard square-root scale.

For two distinct shifts, the ternary sequences differ in exactly

```text
(n+3)/2
```

positions when the two zero locations are counted. Hence a random query distinguishes a fixed pair with probability slightly greater than one half.

## 4. Logarithmic query fingerprints do not imply logarithmic time

Choose `q` public query positions and record

```text
(L_k(x_1),...,L_k(x_q)).
```

For any fixed pair of distinct shifts, the probability that all answers agree is less than `2^(-q)`. A union bound shows that

```text
q=2 log_2(n)+O(1)                                 (L4)
```

random queries distinguish all `n` shifts with high probability.

This gives an important separation:

```text
oracle-query information             O(log n),
known generic classical indexing     Theta(n log n) preprocessing/table,
or                                 Theta(n log n) online scan.
```

The table contains one signature for every possible shift. It is inadmissible under the project cost rule because preprocessing and advice are counted.

The frozen replay uses deterministic seeded positions with

```text
ceil(2 log_2 n)+12
```

queries and obtains unique signatures on every retained toy prime. This is bounded evidence for the fingerprint calculation, not a universal deterministic construction.

## 5. Why this does not yet beat Pollard

The Legendre oracle supplies bits efficiently, but the unresolved task is computational inversion of the shifted pseudorandom sequence.

No classical algorithm with proved total cost

```text
O(n^(1/2-epsilon))
```

is established here. The classical complexity of the shifted Legendre problem is a long-standing open algorithmic question, while efficient quantum recovery is known.

Consequently a compact evaluator for `chi_n(k)` would be a strong hidden-bit primitive, but it would not by itself constitute a classical ECDLP break.

This differs sharply from scalar parity or the suitable EDS-residue bit: an exact parity oracle has a literal logarithmic peeling reduction to the full scalar.

## 6. Frozen replay

`shifted_legendre_classical_recovery.py` verifies on the prime orders

```text
397, 433, 1093, 1249, 3469, 4021
```

1. exact autocorrelation `(L3)` for every shift;
2. exact pairwise Hamming distance on deterministic samples;
3. affine-query reduction `(L1)` on deterministic samples;
4. unique deterministic-seeded fingerprints using `ceil(2 log_2 n)+12` positions;
5. the secp256k1 query/table-size certificate.

The toy fingerprint table is constructed only to test the information/time separation. No production-size table is built or proposed.

## 7. secp256k1 cost certificate

For secp256k1:

```text
bit length                                      256,
fingerprint query budget                         524,
number of possible shifts                         n approximately 2^256,
full signature-table symbols                      approximately 524*2^256,
Pollard scale                                     2^128.
```

Thus the oracle answers contain enough information in a few hundred bits, but the known direct classical indexing structure is exponentially larger than Pollard rho.

## 8. Answer

```text
Do all affine queries reduce to shifted Legendre?              yes
Exact autocorrelation peak                                     yes
Information-theoretic identifying queries                      O(log n)
Known table-free classical sub-sqrt inversion                   absent
Known efficient quantum inversion                              yes
Does a free Legendre oracle currently imply classical ECDLP?   no
Does it imply parity or carry?                                  no
```

## 9. Research decision

The Legendre branch remains mathematically valid, but it is now a two-breakthrough route:

```text
compact public chi_n(k) evaluator
plus
classical sub-sqrt shifted-Legendre inversion.
```

The parity/EDS branch requires only the first kind of breakthrough because its oracle-to-ECDLP reduction is already logarithmic.

Therefore the next primary package returns to the direct bit route:

```text
EDS-ABSOLUTE-ORIENTATION-RETURN-042.
```

Its central question is:

> After the no-go results for quadratic-normalization sections, bounded isogenies, local torsion jets, pairing extensions, and standard theta splittings, what is the smallest remaining generator-sensitive nonlocal EDS/sigma object whose exact public evaluation would directly yield scalar parity or `R3`, rather than the weaker scalar Legendre class?

The package must begin with a full branch audit and select one theorem-first object. No new statistical family is admitted without an exact transformation law.

## 10. Formalization boundary

`Ecdlp/Proved/ShiftedLegendreClassicalRecovery.lean` formalizes the affine-query reduction and elementary normalized-oracle identities. It does not formalize finite-field character sums, random fingerprint probability, FFT complexity, classical query lower bounds, quantum algorithms, or secp256k1 ECDLP.
