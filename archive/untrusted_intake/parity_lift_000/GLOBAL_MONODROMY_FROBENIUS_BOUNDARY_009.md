# GLOBAL-MONODROMY-FROBENIUS-BOUNDARY-009

Date: 2026-08-12

Status: **isolated theorem-first boundary package**.
No external point, key, wallet, or production discrete-log instance is
accepted.  The package makes no unconditional ECDLP-complexity claim.

## 1. Central decision

The first three proposed escapes from `C_quad` separate as follows.

```text
fixed-order scalar monodromy under translation by G:       trivial
finite-field n-th-root monodromy:                          explicit cost > sqrt(n)
canonically trivialized mixed-weight pencil:               reduces to a weight-zero decoder
Frobenius pi-1 leading kernel jet:                          same intrinsic carry as gR3
Frobenius pi+1 nonkernel section:                           even residual EDS weight
public R3 decoder:                                         not obtained
public carry decoder:                                      not obtained
unconditional sub-square-root algorithm:                   not obtained
```

This does not close arbitrary nonalgebraic public predicates, global analytic
continuation with an implicit representation, or unrestricted p-adic
monodromy.  It does remove the most direct finite-field and generalized
Frobenius-section versions of those ideas.

## 2. Fixed-order monodromy cannot encode the odd-cycle cut

Suppose translation by the prime-order generator `G` acts on a scalar phase by

```text
A(Q+G)=zeta*A(Q).
```

Iterating through the full orbit gives

```text
zeta^n=1.
```

If `zeta` is constrained to a fixed root-of-unity group of order `m` with
`gcd(m,n)=1`, then `zeta=1`.  In particular, phases of orders `2`, `3`, `4`, or
`6` cannot provide a nontrivial scalar monodromy around the full secp256k1
subgroup.

An order-three GLV linearization is a different local symmetry, but it remains
binary-trivial: `z^3=1` implies `z=(z^2)^2`, so its quadratic character is one.

Thus a genuine translation phase must have order divisible by `n`.

## 3. Exact finite-field monodromy degree

A nontrivial order-`n` multiplicative phase over a finite field requires

```text
mu_n subset F_(p^d)^*,
```

hence

```text
n divides p^d-1.
```

For the fixed secp256k1 parameters, the exact multiplicative order of `p`
modulo `n` is

```text
d = (n-1)/6
  = 19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

The committed certificate checks

```text
p^d = 1 mod n
```

and

```text
p^(d/q) != 1 mod n
```

for every prime divisor `q` of `d`.

A dense representation of one element of `F_(p^d)` already needs at least

```text
256*d
= 4940462474125491004739028693704017401721069409240529253657820294038108223758336
```

bits.  Moreover,

```text
d / floor(sqrt(n))
= 56713727820156410577229101238628035242.
```

Therefore an explicit finite-field `mu_n` monodromy mechanism is above the
generic square-root scale before its theta arithmetic begins.

Artifacts:

- `experiments/parity_lift_000/global_monodromy_embedding_degree.py`;
- `Ecdlp/Proved/GlobalMonodromyBoundary.lean`.

### Exact boundary

This is a representation-cost statement for explicit finite-field extension
arithmetic.  It is not a universal lower bound on implicit circuits, complex
analytic descriptions, or p-adic algorithms.

## 4. Mixed-weight pencils do not remove the missing object

Let two sections be compared by a public trivialization:

```text
A(Q)=B(Q)*R(Q),
```

where `R` is weight zero on the chosen chart.  Then for every public parameter
`c`,

```text
A(Q)+c*B(Q)=B(Q)*(R(Q)+c).
```

Thus a quadratic character of a mixed-weight pencil factors as

```text
chi(A+cB)=chi(B)*chi(R+c)
```

away from the declared zero and pole locus.

If the reference odd section has C3 orbit sign

```text
g(Q)R3(Q),
```

then the pencil isolates `R3` only when the weight-zero factor contributes
exactly `g`.  In binary additive notation:

```text
(g+r)+f=r  implies  f=g.
```

Consequently a canonically trivialized mixed-weight pencil does not create a
third route.  It is a parametrized search for the same public weight-zero carry
decoder.

The algebraic factorization and binary cancellation implication are formalized
in `Ecdlp/Proved/FrobeniusSectionBoundary.lean`.

The bounded `mixed_weight_pencil_screen.py` remains useful as a search over the
smallest such weight-zero ratios, but any positive candidate must be reported
as a direct carry decoder and calibrated against the identical selected
candidate pool.

## 5. Frobenius generalized division sections

Let `pi` denote p-power Frobenius.  Every rational point satisfies

```text
pi(Q)=Q.
```

Therefore on `E(F_p)`:

```text
(pi-1)(Q)=O,
(pi+1)(Q)=[2]Q.
```

The two endomorphisms have degrees

```text
N_minus = deg(pi-1) = #E(F_p) = n,
N_plus  = deg(pi+1) = p+1+t = 2p+2-n,
```

where `t=p+1-n`.  Both degrees are odd.

### 5.1 The pi-1 kernel jet

In the sigma model for a generalized division function,

```text
Psi_alpha(z) = sigma(alpha*z) / sigma(z)^N
```

up to the fixed normalization attached to `alpha`.  If `G` lies in
`ker(alpha)`, the first nonzero local coefficient at `[k]G` has denominator

```text
sigma(k*z_G)^N.
```

Using

```text
sigma(k*z_G)=W_G(k)*sigma(z_G)^(k^2),
```

its residual EDS exponent is `N`.  For `alpha=pi-1`, `N=n` is odd.  Hence the
leading kernel jet has one odd residual EDS factor and a quadratic
normalization exponent.  By the compatibility theorem already proved in
`GLV-NORMALIZATION-RIGIDITY-008`, its C3 orbit character is again

```text
constant * g(Q) * R3(Q),
```

not `constant*R3(Q)`.

This is the order-dependent Frobenius analogue of the previously screened
order-n torsion jet.  The derivation is conditional on the standard normalized
sigma formula for generalized division functions; the repository Lean file
formalizes only the parity implication, not the sigma geometry.

### 5.2 The pi+1 nonkernel section

For a general endomorphism `alpha` of degree `N`, with `alpha(G)=[m]G`, the
sigma multiplication identity has the form

```text
Psi_alpha([k]G)
 = Psi_alpha(G)^(k^2)
   * W_(alpha G)(k)
   / W_G(k)^N.
```

When `alpha=pi+1`, one has `m=2`.  Expressing the numerator sequence back over
`G` introduces one residual EDS source, while the denominator contributes `N`
sources.  The total residual gauge weight is therefore

```text
N+1.
```

Since `N_plus` is odd, `N_plus+1` is even.  This section can provide relative
or weight-zero information, but it cannot be the required odd `R3` anchor.

The integer parity fact

```text
N odd  implies  N+1 even
```

is kernel-checked in `FrobeniusSectionBoundary.lean`.

## 6. A genuinely new public candidate outside algebraic characters

The previous rational-character screens did not cover integer comparisons of
canonical field representatives.  On a j=0 GLV orbit define

```text
delta_x(Q)
 = (rep(x(Q)) + rep(beta*x(Q)) + rep(beta^2*x(Q))) / p
 in {1,2}.
```

This is public, cheap, and GLV invariant.  It is the exact field-coordinate
analogue of the hidden scalar carry

```text
gamma(k)
 = (k + rep(lambda*k) + rep(lambda^2*k)) / n.
```

Because `delta_x` is Kummer invariant, it is multiplied by either the canonical
half-interval orientation of `y` or `chi(y)` to obtain an anti-Kummer candidate
with the same symmetry as `g`.

The dedicated frozen screen also tests the permutation orientation of the
three canonical x representatives and their products:

- `experiments/parity_lift_000/cm_coordinate_carry_screen.py`;
- workflow `.github/workflows/cm-coordinate-carry.yml`.

A positive result is admitted only if it is an exact cross-order identity or
repeatedly exceeds a matched 95-percent null envelope as the order grows.
Finite selected-candidate maxima are not treated as leakage.

## 7. What remains live

The remaining central question is now precisely a weight-zero question:

```text
Find a public efficiently evaluable F(Q) with

F(phi Q)=F(Q),
F(-Q)=-F(Q),
F(Q)=g(Q),
```

or find a public predicate whose full-group correlation with `g` is at least
inverse-polylogarithmic.

The latter is enough for an unconditional sub-square-root route.  Indeed, if
`h` is public and

```text
E_u h([u]G)g(u) = delta,
```

then Fourier duality and the proven bound `||g_hat||_1=O(log n)` imply

```text
max_j |h_hat(j)| >= |delta| / ||g_hat||_1.
```

An inverse-polylogarithmic `delta` therefore forces an inverse-polylogarithmic
heavy Fourier coefficient.  Chosen-multiplier evaluation gives

```text
h_Q(t)=h([t]Q)=h_G(t*k),
```

which multiplicatively decimates the known spectrum.  The local-SFT recovery
pipeline from `GLV-CARRY-FOURIER-REDUCTION-007` can then recover `k` from a
polynomial-size candidate list.

This observation strengthens the acceptance rule for future screens:
accuracy must not merely exceed one half at a fixed toy order.  Its advantage
must remain at least inverse-polylogarithmic under matched cross-order scaling.

## 8. Current exact answer

```text
public R3 decoder obtained:                              no
public exact carry decoder obtained:                    no
public inverse-polylog correlated carry predicate:      not yet
unconditional sub-square-root algorithm obtained:       no
finite-field global monodromy escape:                    closed in explicit model
mixed-weight pencil as an independent mechanism:        reduced to carry decoder
Frobenius pi-1 leading-jet escape:                       same gR3 multiplier
Frobenius pi+1 odd-anchor escape:                        even residual weight
nonalgebraic CM coordinate carry:                        active bounded test
```

The next constructive work should concentrate on public weight-zero predicates,
particularly the new coordinate-carry family and order-dependent rational
circuits whose Fourier spectrum can be proved heavy without first knowing the
scalar.
