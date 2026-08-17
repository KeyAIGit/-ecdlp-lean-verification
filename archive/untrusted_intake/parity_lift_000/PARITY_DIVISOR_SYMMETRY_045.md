# PARITY-DIVISOR-SYMMETRY-045

Date: 2026-08-12

Status: **the canonical scalar-parity divisor has trivial multiplier stabilizer; GLV/C6 quotients cannot reduce its oriented root count**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Canonical parity sets

Let `n` be an odd prime and use canonical representatives

```text
1,2,...,n-1.
```

Define

```text
E={2,4,...,n-1},
O={1,3,...,n-2}.
```

Both sets have `(n-1)/2` elements, and negation swaps them:

```text
-E=O.                                             (P1)
```

This is the scalar orientation hidden by the Kummer quotient.

## 2. Exact multiplier stabilizer

Put

```text
M=(n-1)/2.
```

The sum of the even representatives is

```text
S_E=2*(1+...+M)=M(M+1)=(n^2-1)/4.                (P2)
```

Modulo `n`,

```text
S_E=-1/4 != 0.                                   (P3)
```

Suppose a nonzero scalar multiplier `u` preserves the parity set:

```text
uE=E.
```

Taking sums modulo `n` gives

```text
u S_E=S_E.
```

Since `S_E` is nonzero,

```text
u=1.                                             (P4)
```

If instead

```text
uE=O,
```

then the sum of all nonzero residues is zero, so `S_O=-S_E`. Hence

```text
u S_E=-S_E,
u=-1.                                            (P5)
```

Therefore

```text
Stab(E)={1},
Swap(E,O)={-1}.                                  (P6)
```

This is an exact theorem for every odd prime.

## 3. Consequence for secp256k1 GLV

The secp256k1 GLV scalar `lambda` has order three and is neither `1` nor `-1`. By `(P6)`:

```text
lambda E != E,
lambda E != O.
```

Thus GLV does not preserve parity and does not globally flip it. It mixes the two classes through the canonical wrap/carry.

No quotient by the order-three CM unit action can therefore define scalar parity as a function on the quotient.

## 4. Exact balance on every C6 orbit

A nonzero C6 orbit is

```text
{plus_or_minus k,
 plus_or_minus lambda*k,
 plus_or_minus lambda^2*k}.
```

For odd `n`, the canonical representatives of `a` and `-a=n-a` have opposite parity. The orbit consists of three such opposite pairs. Therefore every free C6 orbit contains exactly

```text
3 even representatives,
3 odd representatives.                           (P7)
```

Consequences:

1. every C6-invariant scalar function is constant on a set containing both parity values;
2. a C6 trace, norm, or orbit polynomial is parity-blind;
3. GLV orbit compression cannot reduce the number of oriented parity roots;
4. the GLV carry is precisely the extra orientation data needed to choose one member of each opposite pair.

## 5. Parity divisor degree

Let a rational function `f` on the curve equal `+1` on one parity class and `-1` on the other. Then `f^2-1` vanishes on all `n-1` nonzero subgroup points, so

```text
deg(f) >= (n-1)/2.                               (P8)
```

Unlike the scalar-Legendre divisor, the parity divisor admits no C6 quotient reduction by a factor of six. Its exact multiplier stabilizer is trivial.

This does not rule out a short high-degree arithmetic circuit.

## 6. Frozen replay

`parity_divisor_symmetry.py` verifies on frozen odd primes with an order-three scalar:

1. the exact sums `(P2)`-`(P3)`;
2. exhaustive preservation stabilizer `{1}`;
3. exhaustive swapping set `{-1}`;
4. every nonzero C6 orbit has three even and three odd representatives;
5. GLV neither preserves nor swaps parity;
6. the secp256k1 arithmetic certificate.

## 7. Answer

```text
Parity-preserving scalar multipliers             {1}
Parity-swapping scalar multipliers                {-1}
Does GLV preserve parity?                         no
Does GLV globally flip parity?                    no
Parity distribution in each C6 orbit              3 versus 3
Can C6 quotient encode parity?                    no
Can GLV reduce parity-divisor degree?              no
Public parity / EDS-residue decoder               absent
Unconditional classical sub-sqrt ECDLP            absent
```

## 8. Next object

The next theorem-first object is

```text
ORIENTED-PARITY-DIVISOR-CIRCUIT-046.
```

The exact question is:

> Can the high-degree parity divisor, which has no nontrivial scalar or GLV symmetry, nevertheless be evaluated by an `n`-dependent short arithmetic circuit, determinant, resultant, theta product, or p-adic analytic formula in complete `O(n^(1/2-epsilon))` cost?

Any accepted candidate must give:

1. an explicit generator-sensitive divisor or section;
2. a straight-line or recurrence representation;
3. an exact evaluation and branch-extraction theorem;
4. total preprocessing, advice, memory, coefficient-height, and precision costs;
5. proof that it does not reconstruct the full scalar or materialize `(n-1)/2` oriented roots.

## 9. Formalization boundary

`Ecdlp/Proved/ParityDivisorSymmetry.lean` formalizes the nonzero-sum stabilizer and swap identities. It does not formalize canonical parity subsets of finite fields, exhaustive C6 orbit balance, elliptic-curve divisor degrees, arithmetic circuits, or ECDLP.
