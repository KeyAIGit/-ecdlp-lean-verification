# UORC-056 division-polynomial frontier V9

## Status

This checkpoint resolves the first problem left by V8 and sharply narrows the
second.

1. A lower bound on odd divisor support does **not** imply a comparable lower
   bound on straight-line evaluation cost. Division polynomials give an
   explicit elliptic-curve counterexample.
2. Classical terminal Miller functions are closed for every index, not only
   for the bounded small-Miller grammar.
3. Pure division-polynomial characters are closed uniformly across the mixed
   `q mod 4` transfer corpus.
4. The remaining secp256k1-specific case is an even-index division-polynomial
   character, equivalently a decimation of the EDS residue sequence.

The algebraic identities and executable checks are complete. Literature source
locking, independent specialist review and formalization remain pending.

## 1. Input from V8

For an exact regularized quadratic-character evaluator on an odd cyclic
subgroup `H=<G>` of order `n`, V8 gives

```text
cot(pi/(2n)) <= s(f)*sqrt(q)+s(f)+1,
```

where

```text
s(f)=#{P in E(Fbar_q): ord_P(f) is odd}.
```

For the public secp256k1 parameters, the certified consequence is

```text
s(f) >= 216543324404233567658511113820216134562.
```

The open question was whether such support already forces comparable circuit
cost.

## 2. Classical Miller functions are fully closed

For a point `P` and positive index `m`, the terminal Miller function satisfies

```text
div(f_(m,P)) = m[P]-[mP]-(m-1)[O].
```

Reducing divisor multiplicities modulo two gives:

```text
m odd:  [P]+[mP],
m even: [mP]+[O].
```

Coincident points can cancel, so in every case

```text
s(f_(m,P)) <= 2.
```

This bound is independent of `m`. The line factors in a Miller loop can be
numerous, but their odd divisor slots telescope to at most two in the terminal
function.

Therefore a single exact evaluator

```text
chi(f_(m,P)(Q))
```

cannot equal canonical parity once the V8 support lower bound exceeds two.
This closes every classical terminal Miller function for every index.

A product of `t` independent terminal Miller functions has odd support at most
`2t`. Consequently, on secp256k1 it needs at least

```text
108271662202116783829255556910108067281
```

terminal factors before it can even meet the V8 support requirement. This is a
representation lower bound for an explicit list of terminal Miller functions,
though not yet for a recursively specified family with shared structure.

## 3. Division polynomials separate support from cost

Assume the characteristic does not divide `m`. The classical division
polynomial has divisor

```text
div(psi_m)
 = sum_{T in E[m] minus {O}} [T] - (m^2-1)[O].
```

All nonzero `m`-torsion zeros are simple. Hence

```text
s(psi_m) = m^2-1,  m odd,
s(psi_m) = m^2,    m even.
```

This grows quadratically with the index.

At a non-2-torsion evaluation point, however, the standard recurrences are

```text
psi_(2r+1)
 = psi_(r+2) psi_r^3 - psi_(r-1) psi_(r+1)^3,

psi_(2r)
 = (psi_r/psi_2)
   (psi_(r+2) psi_(r-1)^2 - psi_(r-2) psi_(r+1)^2).
```

A memoized binary dependency DAG contains only a constant-width window at each
halving level. Therefore `psi_m(Q)` has an `O(log m)` field-arithmetic
straight-line program, with one reusable inversion of `psi_2(Q)`.

For secp256k1, the smallest even index whose odd support reaches the V8 bound is

```text
m_min = 14715411119103453974.
```

It has bit length 64 and

```text
s(psi_m_min)=m_min^2
            >= 216543324404233567658511113820216134562.
```

The exact dependency replay contains only

```text
483 total division-polynomial indices,
479 nonbase recurrence nodes,
<= 2906 field multiplications,
<= 495 additions or subtractions,
1 field inversion.
```

Thus a natural elliptic-curve family reaches square-root-scale odd support with
only a few thousand field operations. Any unrestricted theorem of the form

```text
large odd support => large straight-line evaluation cost
```

is false.

This is not a parity evaluator. It is a counterexample to the proposed proof
strategy.

## 4. Negation covariance of division-polynomial characters

Division polynomials satisfy

```text
psi_m(-Q)=(-1)^(m+1) psi_m(Q).
```

Canonical parity on an odd cycle is anti-invariant:

```text
sigma_G(-Q)=-sigma_G(Q).
```

Therefore:

### Odd index

For odd `m`, `psi_m` is `x`-only and invariant under `Q -> -Q`. Its quadratic
character is invariant over every odd field, so it cannot equal parity.

### Even index, q=1 mod 4

For even `m`, `psi_m` changes sign. If `chi(-1)=+1`, its quadratic character is
still invariant. It cannot equal parity.

### Even index, q=3 mod 4

If `chi(-1)=-1`, the character becomes anti-invariant and passes this symmetry
gate. secp256k1 lies in this class.

The 18-curve transfer corpus contains primes in both congruence classes.
Therefore no pure formula `chi(psi_m(Q))` can transfer unchanged across the
whole corpus for any parity of `m`.

## 5. EDS normal form of the surviving case

The division-polynomial composition identity is

```text
psi_(mk)(G)=psi_m([k]G) * psi_k(G)^(m^2).
```

Define the EDS residue sign

```text
rho_j=chi(psi_j(G)).
```

Then

```text
m odd:
chi(psi_m([k]G))=rho_(mk) rho_k,

m even:
chi(psi_m([k]G))=rho_(mk).
```

The only secp256k1-specific pure division-polynomial case surviving covariance
and V8 is therefore

```text
m even,
m >= 14715411119103453974,
k -> rho_(mk).
```

It is not an independent Miller mechanism. It is a decimation of the same EDS
residue sequence already isolated as the hidden orientation factor.

## 6. Executable bounded screen

The V9 replay evaluates exact division-polynomial recurrences on every nonzero
point of the five frozen discovery curves. It tests all 2,048 even indices
through `m=4096` with one allowed global output phase.

Results:

```text
438 nonzero points,
1,897 indices defined everywhere,
0 exact parity candidates,
best index m=884,
best match 272/438.
```

On each discovery curve separately, no exact even-index candidate appears
through `8n`.

This finite negative is supporting evidence only. The asymptotic conclusion is
the structural reduction above, not extrapolation from `m<=4096`.

## 7. What V9 closes

- every single classical terminal Miller function, for arbitrary index;
- every product of fewer than half the V8 support lower bound independent
  terminal Miller functions;
- every odd-index pure division-polynomial character;
- every even-index pure division-polynomial character over `q=1 mod 4`;
- unchanged pure division-polynomial transfer across a corpus containing both
  `q=1 mod 4` and `q=3 mod 4`;
- the proposed unrestricted odd-support-to-SLP-cost theorem.

## 8. What remains open

The main surviving rational-character route is now much narrower:

```text
secp256k1,
m even and at least 14715411119103453974,
chi(psi_m([k]G))=rho_(mk).
```

The next theorem should target the EDS decimation itself, not geometric degree.
The useful questions are:

1. Determine the exact quadratic-character quasi-periodicity of `rho_j` for a
   point of prime order `n`.
2. Classify whether any even decimation `k -> rho_(mk)` can equal the sawtooth
   parity sequence on all `1<=k<n`.
3. Express the obstruction through Ward symmetry, an elliptic-net cocycle or a
   metaplectic character of multiplication by `m`.
4. Keep the full all-in cost gate if a constructive exceptional `m` appears.

Direct field-valued evaluation of `Y_G`, theta or elliptic-unit formulas, and
non-character branching circuits remain outside this checkpoint.

## References

- J. H. Silverman, *The Arithmetic of Elliptic Curves*, division-polynomial
  recurrences and multiplication formulas.
- V. Miller, *Short Programs for Functions on Curves*, Miller functions and
  their divisors.
- M. Ward, *Memoir on Elliptic Divisibility Sequences*, nonlinear EDS
  recurrences.
- I. Shparlinski and K. Stange, *Character Sums with Division Polynomials*,
  Canadian Mathematical Bulletin 55 (2012), 850-857.
- J. H. Silverman, *p-adic properties of division polynomials and elliptic
  divisibility sequences*, 2004.

## Claim boundary

V9 proves a mechanism separation and a set of no-go statements. It does not
produce an evaluator, recover any scalar or prove a general lower bound for all
arithmetic circuits.
