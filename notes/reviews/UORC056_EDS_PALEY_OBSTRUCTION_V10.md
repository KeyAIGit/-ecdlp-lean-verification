# UORC-056 V10: Paley obstruction for pure EDS decimation

## Status

The mathematical reduction and the executable finite-field certificates are
complete. Independent peer review and formal-assistant transcription remain
pending.

V10 closes the last pure single-factor division-polynomial route left open by
V9. It does **not** close products or ratios of several division-polynomial
factors, arbitrary EDS straight-line programs, or direct field-valued
construction of the oriented root.

## 1. Target class

Let

```text
E/F_q,
H=<G>,
|H|=n,
q and n odd primes,
chi : F_q -> {0,+1,-1} the quadratic character.
```

V9 reduced the only covariance-compatible secp256k1 case to

```text
delta * chi(psi_m([k]G)) = (-1)^k,
1 <= k < n,
m even,
delta in {+1,-1},
q = 3 mod 4.
```

Here `delta` is one public global output phase. Per-point phases and omitted
zeros are forbidden.

## 2. Theorem

### Theorem V10-EDS-PALEY

Assume the target above is defined and exact on every nonzero point of `H`.
Put

```text
t=(n-1)/2.
```

Then necessarily

```text
t^2 <= 3q+1.
```

Consequently, if

```text
((n-1)/2)^2 > 3q+1,
```

there is no even index `m`, of any size, and no global phase `delta` for which
`delta*chi(psi_m(Q))` computes canonical parity on `H`.

This is an all-index theorem. It does not enumerate `m` and does not use the V8
lower threshold on `m`.

## 3. Proof

### Step 1: the candidate would make all division-polynomial values square

Write

```text
R=[m]G.
```

The evaluator is everywhere nonzero, so `n` does not divide `m`; because `n` is
prime, `R` again has order `n`.

The division-polynomial composition identity is

```text
psi_(ab)(P)=psi_a([b]P) * psi_b(P)^(a^2).
```

Since `m` is even, `m^2` is even. Therefore

```text
chi(psi_(mk)(G))
 = chi(psi_m([k]G))
 = delta*(-1)^k.
```

The same composition identity in the opposite order gives

```text
psi_(mk)(G)=psi_k(R) * psi_m(G)^(k^2).
```

At `k=1`, exactness gives

```text
chi(psi_m(G))=-delta.
```

Hence

```text
chi(psi_k(R))
 = delta*(-1)^k * (-delta)^(k^2)
 = 1       for k odd,
 = delta   for k even.
```

If `delta=+1`, take `R'=R`. If `delta=-1`, take `R'=-R`. The negation law

```text
psi_k(-R)=(-1)^(k+1) psi_k(R)
```

toggles precisely the even-index characters because `chi(-1)=-1`. Thus in
both phase cases

```text
chi(psi_k(R'))=+1
for every 1 <= k < n.
```

### Step 2: the half orbit becomes a transitive Paley subtournament

For `1 <= i < j <= t`, the standard division-polynomial difference identity is

```text
x([j]R')-x([i]R')
 = - psi_(i+j)(R') psi_(j-i)(R')
     / (psi_i(R')^2 psi_j(R')^2).
```

All indices on the right lie in `1,...,n-1`, because `i+j<=2t=n-1`.
Every division-polynomial value on the right is a nonzero square. Therefore

```text
chi(x([j]R')-x([i]R'))=chi(-1)=-1,
chi(x([i]R')-x([j]R'))=+1.
```

The values

```text
x(R'), x([2]R'), ..., x([t]R')
```

are distinct: equality would imply `iR'=+/-jR'`, while neither `i-j` nor
`i+j` is divisible by `n` in this range.

Thus these `t` field elements form a transitive subtournament in the Paley
tournament: in their natural order every forward difference is a quadratic
residue.

### Step 3: spectral bound

Index the full quadratic-character matrix by `F_q`:

```text
M_(u,v)=chi(u-v),
chi(0)=0.
```

The elementary character correlation identity gives

```text
M M^T = q I - J.
```

Therefore

```text
||M||_2=sqrt(q).
```

The principal submatrix on the `t` ordered half-orbit coordinates is

```text
T_(i,j)= 0  if i=j,
          1  if i<j,
         -1  if i>j.
```

A principal compression cannot have larger operator norm, so

```text
||T||_2 <= sqrt(q).
```

For the all-ones vector,

```text
(T 1)_i=t+1-2i,
||T 1||_2^2=t(t^2-1)/3.
```

Hence

```text
||T||_2^2 >= (t^2-1)/3.
```

Combining the two bounds yields

```text
(t^2-1)/3 <= q,
t^2 <= 3q+1.
```

This proves the theorem.

## 4. secp256k1 certificate

For secp256k1,

```text
q=p
 = 115792089237316195423570985008687907853269984665640564039457584007908834671663,

n
 = 115792089237316195423570985008687907852837564279074904382605163141518161494337.
```

The exact integer gate is equivalently

```text
(n-1)^2 > 12p+4.
```

It passes by an enormous margin:

```text
bit_length(((n-1)/2)^2) = 510,
bit_length(3p+1)         = 258.
```

Therefore no pure evaluator

```text
delta * chi(psi_m(Q))
```

can compute canonical parity on the secp256k1 prime-order subgroup for any
index `m`. Odd `m` and the `q=1 mod 4` even case were already closed by
negation covariance; V10 closes the remaining even `m`, `q=3 mod 4` case.

## 5. Executable corpus result

The V10 replay independently checks:

- the composition identity on all 18 frozen curves;
- the `x([a]G)-x([b]G)` identity on every pair in the half orbit for every
  `q=3 mod 4` curve;
- the finite-field character correlation `sum_z chi(z)chi(z+1)=-1`;
- the exact integer Paley margin;
- both global output phases.

Corpus decision:

```text
18 total curves,
7 q=1 mod 4 curves closed by covariance,
11 q=3 mod 4 curves closed by the Paley inequality,
0 unresolved curves.
```

The smallest positive Paley margin in the corpus is already `95`, on
`p=43,n=31`; all other margins are larger.

## 6. What is closed

V10 closes, for arbitrary index size:

```text
delta * chi(psi_m(Q))
```

with one division-polynomial factor and one global phase on secp256k1 and on
the complete 18-curve transfer corpus.

This removes the V9 item

```text
Can an even EDS decimation k -> rho_(mk) equal (-1)^k?
```

for the pure single-factor realization coming from `psi_m`.

## 7. What remains open

The next rational-character frontier is no longer a single EDS decimation. It
must use genuinely richer structure, for example

```text
chi(prod_i psi_(m_i)(Q) / prod_j psi_(r_j)(Q)),
```

with exact divisor cancellation, or an arithmetic circuit whose character
cannot be collapsed to one division-polynomial factor plus a global phase.
Direct field-valued `Y_G` evaluation, theta/elliptic-unit constructions and
non-character branching also remain separate.

Any continuation should first determine whether a bounded product of `s`
division-polynomial factors forces a low-rank or multi-tournament analogue of
the V10 obstruction. Blindly increasing the index bound is now obsolete.

## References

- J. H. Silverman, *The Arithmetic of Elliptic Curves*, division-polynomial
  recurrences, multiplication formulas and coordinate identities.
- M. Ward, *Memoir on Elliptic Divisibility Sequences*, EDS recurrences.
- I. Shparlinski and K. Stange, *Character Sums with Division Polynomials*,
  Canadian Mathematical Bulletin 55 (2012), 850-857.
- `UORC056_DIVISION_POLYNOMIAL_FRONTIER_V9.md`, source-locked predecessor and
  executable composition replay.

## Claim boundary

This is a scoped algebraic impossibility theorem. It is not a parity evaluator,
not an ECDLP algorithm and not a lower bound for unrestricted arithmetic
circuits. No external target point, wallet, real key or unknown production
scalar is used.
