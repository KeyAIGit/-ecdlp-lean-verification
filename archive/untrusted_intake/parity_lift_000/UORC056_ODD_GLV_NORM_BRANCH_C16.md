# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C16: odd GLV norm as a global branch selector

Date: 2026-08-13

Status: **C15 leaves one global `mu_2` ambiguity `Z -> -Z`. The natural cubic GLV norm is odd under this ambiguity and therefore is a valid branch selector. Its invariant divisor does not collapse, however: outside at most four exceptional nonzero GLV orbits, every coefficient is a sum of three signs and cannot vanish. On secp256k1 the descended function in `F_p(y)` has at least `(n-1)/3-4` nonzero quotient-support points and pole degree at least `(n-1)/6-2`. The standard odd-norm route moves orientation into a new linear-degree invariant but does not provide a sub-square-root evaluator. A short addition-enabled circuit for that invariant remains open.**

Only frozen prime orders, one frozen `j=0` scalar control, and public secp256k1 constants are used. No unknown-scalar external point, wallet, private key, or production target is accepted.

## 1. Why an odd observable is required

C15 gives a compact local law

```text
Z(P)Z(P+G)=R(P),
```

but all local products are unchanged by `Z -> -Z`. Every even-degree norm has the same defect.

On secp256k1, let

```text
phi(x,y)=(beta*x,y),
phi([k]G)=[lambda*k]G,
lambda^2+lambda+1=0 mod n.
```

Define

```text
N_phi Z(P)=Z(P)Z(phi(P))Z(phi^2(P)).              (C16.1)
```

Then

```text
boxed:
N_phi(-Z)=-N_phi(Z).                             (C16.2)
```

Thus a compact evaluator for the cubic norm would genuinely select the missing global branch.

## 2. Invariance and descent

The three factors are cyclically permuted by `phi`, so

```text
N_phi Z(phi(P))=N_phi Z(P).                      (C16.3)
```

For `E:y^2=x^3+7` and `phi(x,y)=(beta*x,y)`, the fixed field is

```text
F_p(E)^<phi>=F_p(y).
```

Hence

```text
boxed:
N_phi Z(P)=R_G(y(P))                             (C16.4)
```

for a rational function `R_G` on the genus-zero quotient.

## 3. Endpoint divisor is parity plus a finite correction

Let `z_k=ord_(P_k)Z`. C15 gives

```text
z=p-r,
p_k=(-1)^k,
r=delta_m+q,
q=delta_a+delta_(n-1)-delta_(a-1)-delta_0.       (C16.5)
```

The correction `r` meets at most four nonzero indices: `m,a-1,a,n-1`.

## 4. Odd-orbit noncancellation theorem

For a nonzero GLV orbit

```text
O_k={k,lambda*k,lambda^2*k},
```

the cubic-norm divisor coefficient is

```text
c(O_k)=sum_(j in O_k) z_j.                       (C16.6)
```

If `O_k` avoids the correction support, then

```text
c(O_k)=sum_(j in O_k)(-1)^j.
```

This is a sum of three elements of `{+1,-1}` and therefore belongs to

```text
{-3,-1,+1,+3}.
```

It can never vanish. At most four nonzero GLV orbits meet the correction support. Since there are `(n-1)/3` nonzero order-three orbits,

```text
boxed:
nonzero quotient support >= (n-1)/3-4.           (C16.7)
```

## 5. Descended pole-degree lower bound

The quotient divisor is principal, so its positive and negative degrees are equal. Every nonzero quotient-support coefficient has absolute value at least one. Therefore twice the pole degree is at least the number of nonzero quotient points.

For secp256k1,

```text
boxed:
deg_poles(R_G) >= (n-1)/6-2.                    (C16.8)
```

Exact values are

```text
nonzero GLV orbits =
38597363079105398474523661669562635950945854759691634794201721047172720498112

nonzero quotient support lower bound =
38597363079105398474523661669562635950945854759691634794201721047172720498108

pole degree lower bound =
19298681539552699237261830834781317975472927379845817397100860523586360249054
```

The pole-degree bound has 254 bits. As in C9, this is not an unrestricted arithmetic-circuit lower bound.

## 6. Consequence

The cubic norm solves the correct logical problem, because it changes sign under the global branch flip. But the standard symmetry route now requires one of the following:

```text
1. materialize a linear-degree R_G(Y),
2. evaluate an equivalent almost-full quotient divisor,
3. find a genuine short addition-enabled circuit for R_G.
```

The first two fail the complete cost gate. The third remains open.

## 7. Replay

Index-space replay checks both roots of `lambda^2+lambda+1=0 mod n` for the frozen orders

```text
19,31,67,271,397,433.
```

It verifies that all nonexceptional orbit sums are odd and nonzero and that all support and pole-degree lower bounds hold.

A scalar control uses

```text
E/F_43: y^2=x^3+7,
G=(38,21), |G|=31,
beta=6, lambda=5.
```

On 12 deterministic `F_(43^2)` probes it verifies

```text
N_phi Z(phi(P))=N_phi Z(P),
N_phi(-Z)=-N_phi(Z).
```

Full replay SHA-256:

```text
63cd039f4bf562db53f41a574787a67070aec397fd56debc639f6295844dc080
```

## 8. Answer

```text
Natural odd branch observable                      cubic GLV norm
Does it distinguish Z from -Z?                     yes
Does it descend?                                   yes, to F_p(y)
Nonzero quotient support lower bound               (n-1)/3-4
Descended pole degree lower bound                  (n-1)/6-2
Does the standard odd norm give a compact evaluator? no
Does degree prove arbitrary circuit hardness?       no
Short addition-enabled invariant circuit            open
Strictly sub-square-root evaluator                  absent
Parity oracle below square root                     absent
Sub-square-root ECDLP                               absent
```

## 9. Successor

The next package is

```text
HIGH-DEGREE-INVARIANT-ADDITION-CIRCUIT-067.
```

It must compute `R_G(y(Q))` without constructing `R_G` densely, evaluating three independent endpoint gauges, or receiving the branch as advice. The primary routes are cubic Kummer norm decomposition by `x`-exponent classes modulo three, high-index division/net recurrences for those components, transposed evaluation on the `y`-line, explicit addition-enabled circuits, and scoped lower bounds for bounded-width invariant recurrences.
