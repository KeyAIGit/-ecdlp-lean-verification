# UORC-056 parity-spectrum divisor barrier

## Status

This is a provisional theorem-level result. The derivation and executable
arithmetic checks have been audited internally, but independent specialist
review and formalization remain pending.

This note gives a theorem-level obstruction to every exact evaluator of the
form

```text
eta(f(Q)),
```

where `eta` is the quadratic character and `f` is a rational function of low
divisor degree on an elliptic curve whose full rational-point group is the
marked odd cyclic group.

It is stronger than another finite grammar screen. It closes all bounded
low-divisor-degree rational-character formulas at once, independently of the
chosen affine, conic, pullback or Miller presentation.

It does **not** yet give a straight-line-program lower bound. A rational
function of enormous degree can sometimes have a short representation through
pullbacks, addition chains, division polynomials or Miller recurrences. Such a
representation still requires a separate all-in construction and evaluation
cost argument.

## Setting

Let `E/F_q` be an elliptic curve over an odd finite field and assume

```text
E(F_q) = <G>,     #E(F_q) = n,
```

with `n >= 3` odd. Let `eta:F_q^* -> {+1,-1}` be the quadratic character and
let `f` be a nonzero rational function on `E` such that `f(P)` is finite and
nonzero for every `P in E(F_q) - {O}`.

Define the geometric odd-divisor support

```text
B(f) = {P in E(Fbar_q) : ord_P(f) is odd},
b(f) = #B(f).
```

Assume that `f` realizes canonical parity:

```text
eta(f([k]G)) = (-1)^k,     1 <= k < n.
```

## Theorem

Under the setting above,

```text
(b(f) + 1) * sqrt(q) >= cot(pi/(2n)).
```

Consequently,

```text
b(f) >= cot(pi/(2n))/sqrt(q) - 1.
```

If `deg(f)` denotes the degree of the rational map `f:E -> P^1`, then

```text
deg(f) >= ceil(b(f)/2).
```

Therefore, whenever `n` is asymptotic to `q`,

```text
b(f) = Omega(sqrt(n)),
deg(f) = Omega(sqrt(n)).
```

For secp256k1, where the cofactor is one and the full rational-point group has
prime order `n`, the certified elementary estimate in the machine artifact
gives

```text
b(f) >= 216543324404233567658511113820216134562,

deg(f) >= 108271662202116783829255556910108067281.
```

The sharp real-valued bound has logarithmic size

```text
log2(cot(pi/(2n))/sqrt(p)) = 127.348503870528...
```

for odd support, before the factor two conversion to rational-map degree.

## Step 1: exact Fourier peak of parity

For a frequency `r`, let

```text
rho_r([k]G) = exp(2*pi*i*r*k/n).
```

Use the two frequencies

```text
r_- = (n-1)/2,
r_+ = (n+1)/2.
```

At `r_-`,

```text
(-1)^k rho_r([k]G) = exp(-pi*i*k/n).
```

Hence

```text
sum_{k=1}^{n-1} (-1)^k rho_r([k]G)
  = sum_{k=1}^{n-1} exp(-pi*i*k/n)
  = -i*cot(pi/(2n)).
```

At `r_+` the sum is its complex conjugate. Thus both peak frequencies have
exact nonzero-point magnitude

```text
cot(pi/(2n)) = (2/pi)n + O(1/n).
```

This large coefficient is the spectral signature of the single discontinuity
created by trying to place alternating parity on an odd cycle.

## Step 2: convert group characters into unramified local systems

The Lang isogeny

```text
Frob_q - 1 : E -> E
```

has kernel `E(F_q)`. The function-sheaf dictionary for connected commutative
algebraic groups associates to each `rho_r` a rank-one lisse character sheaf
`M_r` on `E` whose Frobenius trace on `E(F_q)` is `rho_r`.

The two geometric local systems `M_{r_-}` and `M_{r_+}` are distinct because
their quotient is the nontrivial Lang local system `M_{-1}`.

## Step 3: attach the Kummer sheaf of f

The quadratic Kummer sheaf attached to `f` is rank one, pure of weight zero and
lisse away from the points where `ord_P(f)` is odd. Since the characteristic is
odd, its local ramification is tame.

Let

```text
U = E - (B(f) union {O}).
```

For either peak frequency define

```text
L_r = K_f tensor M_r
```

on `U`. Because the two `M_r` are geometrically distinct, at least one of the
two sheaves `L_{r_-}`, `L_{r_+}` is geometrically nontrivial.

Choose such an `r`.

## Step 4: cohomological square-root bound

The curve `U` has genus one and at most `b(f)+1` geometric punctures. The sheaf
`L_r` has rank one and only tame ramification. The
Grothendieck-Ogg-Shafarevich formula therefore gives

```text
dim H_c^1(U_bar, L_r) <= b(f)+1,
```

because geometric nontriviality kills `H_c^0` and `H_c^2`.

The Grothendieck trace formula expresses the complete trace sum as the
Frobenius trace on `H_c^1`. Deligne's weight bound gives absolute value at most
`sqrt(q)` for each eigenvalue. Therefore

```text
abs(sum_{P in E(F_q)-{O}} eta(f(P))*rho_r(P))
  <= (b(f)+1)*sqrt(q).
```

The left side is exactly the parity Fourier peak from Step 1. This proves

```text
(b(f)+1)*sqrt(q) >= cot(pi/(2n)).
```

## Step 5: degree consequence

Write `b_+` for odd-order zeros and `b_-` for odd-order poles. If `d=deg(f)`,
then

```text
d >= b_+,
d >= b_-,
b(f)=b_+ + b_-.
```

Thus `d >= ceil(b(f)/2)`.

## Integer-certified elementary lower bound

The generated artifact does not rely on floating point for its certified
integer result. Put `x=pi/(2n)`. The elementary inequalities

```text
sin(x) <= x,
cos(x) >= 1-x^2/2,
pi < 22/7
```

give

```text
cot(pi/(2n))
  >= 2n/pi - pi/(4n)
  > (98*n^2-121)/(154*n).
```

Combining this rational lower bound with the theorem permits exact integer
arithmetic using `isqrt`.

## What this closes

This theorem excludes exact parity from every family whose resulting rational
function has odd-divisor support `o(n/sqrt(q))`. In the cofactor-one regime
`n asymptotic to q`, this includes every uniformly bounded-degree or
`o(sqrt(n))`-degree rational-character mechanism.

In particular, the negative V1-V5 screens are now instances of a general
spectral obstruction rather than isolated failures of selected coefficient
sets.

## What remains open

1. Succinct high-degree circuits. Pullbacks `[m]^*f`, division polynomials,
   EDS factors and Miller chains may have degree far larger than their syntax.
2. Representation cost. The theorem lower-bounds geometric degree, not the
   number of field or group operations needed to represent that degree.
3. Proper subgroups. The statement above is written for `E(F_q)=<G>`. The
   frozen corpus and secp256k1 satisfy this. Extending the clean conductor bound
   to an arbitrary proper marked subgroup requires an additional subgroup
   restriction argument.
4. Sums or branching circuits. The theorem directly handles one quadratic
   character of one rational function. Products of character atoms collapse to
   this form, but adaptive branching or non-character outputs require separate
   treatment.

## Standard inputs

The proof uses established results rather than a new unproved estimate:

- the Lang-isogeny function-sheaf dictionary for characters of a connected
  commutative algebraic group over a finite field;
- Kummer sheaves and multiplicative character sums on curves;
- the Grothendieck trace formula;
- the Grothendieck-Ogg-Shafarevich formula;
- Deligne's weight theorem in *La conjecture de Weil II*.

Relevant references include Cunningham-Roe on commutative character sheaves,
Perret on multiplicative character sums and Kummer coverings, SGA 5 for the
trace and Euler-characteristic formalism, and Deligne's Weil II.

## References

- P. Deligne, *La conjecture de Weil II*, Publications Mathematiques de
  l'IHES 52 (1980), 137-252.
- C. Cunningham and D. Roe, *From the function-sheaf dictionary to
  quasicharacters of p-adic tori*, Journal of the Institute of Mathematics of
  Jussieu 17 (2018), 1-37.
- M. Perret, *Multiplicative character sums and Kummer coverings*, Acta
  Arithmetica 59 (1991), 279-290.
- Standards for Efficient Cryptography Group, *SEC 2: Recommended Elliptic
  Curve Domain Parameters*, Version 2.0 (2010).
