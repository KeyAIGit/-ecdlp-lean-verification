# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C29: autonomous algebraic-state rigidity

Date: 2026-08-15

Status: **C29 classifies exact autonomous states for canonical scalar parity. On an odd prime cycle, every deterministic autonomous state with a state-only exact decoder must have `n` distinct semantic values. Therefore the four-state objects `(g_G,J_G)` and `W_G=g_G+2J_G` are valid static classifiers but cannot be closed under one deterministic update for `Q -> Q+G`. A recurrence fitted only on the finite marked orbit is not evidence of compression: any `n` prescribed successor values admit a degree-below-`n` Lagrange interpolant, and the frozen cycle interpolants use `n-1` or `n` nonzero coefficients. For a global algebraic semiconjugacy `S(P+G)=R(S(P))`, the normalized image has genus zero or one. The genus-zero case would require an order-`n` element of `PGL_2(F_p)` and is excluded for secp256k1 by the exact certificate `gcd(n,p(p^2-1))=1`. In the genus-one case, after translating the origin, `S` is an isogeny and the update is translation by `S(G)`, so `S(Q)=[k]S(G)`: the same hidden scalar is recoded on an isogenous marked subgroup. No parity evaluator or sub-square-root ECDLP algorithm is constructed. The surviving mechanism must be nonautonomous or target-dependent.**

Only public prime orders, public finite-field constants, deterministic finite-state controls, and public secp256k1 constants are used. No external unknown-scalar point, wallet, private key, production target, scalar-indexed table, oriented-root table, or target-dependent advice is accepted.

Deterministic result artifact:

```text
experiments/parity_lift_000/uorc056_autonomous_state_rigidity_result.json
```

## 1. Central target

Let

```text
E/F_p be the public elliptic curve,
H=<G>,
|H|=n,
Q=[k]G,
1<=k<n.
```

The unchanged target is

```text
sigma_G(Q)=Y_G(x(Q))/y(Q)=(-1)^k.
```

The complete cost gate remains

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
=O(n^(1/2-epsilon)).
```

C27 excludes several broad linear/operator state models. C28 proves that an ordinary rational parity observable has pole degree at least `(n-1)/2`, while explicitly leaving high-degree low-size circuits open. C29 asks whether that surviving circuit can be realized as one fixed autonomous state transition.

## 2. Three notions that must not be conflated

### 2.1 Static sufficient state

A static state is any value `S_G(Q)` from which parity can be decoded. Without a representation restriction this notion is tautological because one may take

```text
S_G(Q)=(-1)^k.
```

### 2.2 Autonomous state

An autonomous state has one fixed transition law

```text
s_(k+1)=R(s_k),
s_k=S_G([k]G),
```

and one decoder

```text
D(s_k)=(-1)^k.
```

The next state is determined by the current state alone. C29 classifies this model.

### 2.3 Nonautonomous or target-dependent compiler

A nonautonomous compiler may use a sequence of public maps depending on the curve, generator, query coordinates, recursion level, addition chain, or other public data:

```text
state_(i+1)=R_i(E,G,Q,state_i).
```

This is not covered by the autonomous theorem. It is the surviving target after C29.

## 3. Canonical parity has full cyclic period

Define the canonical cyclic word

```text
sigma(k)=(-1)^k,
0<=k<n,
```

with indices reduced into the canonical range `0,...,n-1`.

For every nonzero shift `d mod n`, the shifted word differs from the original.

If `d` is odd, take `k=0`:

```text
sigma(d)=-1 != +1=sigma(0).
```

If `d` is even and nonzero, take `k=n-d`. Since `n` is odd and `d` is even, `n-d` is odd, while

```text
k+d=0 mod n.
```

Hence

```text
sigma(k)=-1 != +1=sigma(k+d).
```

Therefore

```text
boxed:
minimal cyclic period of sigma is n.              (C29.1)
```

This is the wrap defect in its most elementary form. The linear alternating word has period two before reduction modulo `n`, but the canonical odd cycle itself has full period `n`.

## 4. Autonomous state injectivity theorem

Let

```text
s_k in State,
s_(k+1)=R(s_k),
D(s_k)=sigma(k).
```

Suppose two states repeat:

```text
s_i=s_j,
i!=j mod n.
```

Determinism gives, for every `t>=0`,

```text
s_(i+t)=s_(j+t).
```

The decoder therefore gives

```text
sigma(i+t)=sigma(j+t)
```

for every `t`. Thus `sigma` is invariant under the nonzero shift `j-i`, contradicting `(C29.1)`.

Consequently

```text
boxed:
s_0,s_1,...,s_(n-1) are pairwise distinct.        (C29.2)
```

Every exact autonomous state with a state-only decoder carries a faithful `n`-phase orbit.

This statement is semantic. It does not say that storing the state requires `n` field elements. One field element can take `n` distinct values when an appropriate order-`n` action exists. The theorem says that the state cannot genuinely collapse the cycle to two, four, or any smaller number of semantic states.

## 5. Consequence for `g_G`, `J_G`, and `W_G`

The static factorization is exact:

```text
g_G(Q) in {+1,-1},
J_G(x(Q)) in {+1,-1},
g_G(Q)J_G(x(Q))=(-1)^k.
```

The four-state encoding

```text
W_G(Q)=g_G(Q)+2J_G(x(Q))
in {-3,-1,1,3}
```

also decodes parity by

```text
(-1)^k=(W_G(Q)^2-5)/4.
```

However `(C29.2)` gives:

```text
boxed:
there is no deterministic state-only map R on four values such that
W_G(P+G)=R(W_G(P)) on the complete odd cycle.       (C29.3)
```

The same applies to the pair `(g_G,J_G)`. These objects remain useful static classifications and possible decoder outputs, but they are not closed autonomous translation states.

The simplest visible conflict is the even state at the wrap. On ordinary edges an even scalar is followed by an odd scalar. On the final edge `n-1 -> 0`, an even scalar is followed by an even scalar. One identical two-state label would need two different successors.

## 6. Decoder access to `Q`

The original broad state formulation allowed

```text
D(E,G,Q,S_G(Q))=(-1)^k.
```

In that model, collisions of `S_G(Q)` alone are not an obstruction because the decoder may distinguish the points through `Q`.

But then the complete state is

```text
S_complete(Q)=(Q,S_G(Q)).
```

Its first coordinate is the original public subgroup point. The builder-decoder composition is again the original parity evaluator. Therefore a claim of compression must identify what the auxiliary coordinate contributes beyond the already available `Q` and must charge the algorithm that constructs it.

C29 uses the state-only decoder theorem only for genuine summaries. The global algebraic theorem below treats the complete state image and shows that an autonomous global realization has genus one and retains the same scalar.

## 7. Finite-orbit interpolation trap

A frozen finite recurrence can always be manufactured.

Let `x_0,...,x_(n-1)` be `n` distinct field elements and prescribe arbitrary successors

```text
R(x_i)=x_(i+1 mod n).
```

Lagrange interpolation produces a polynomial `R` of degree below `n` satisfying all `n` equations.

Thus

```text
boxed:
passing every edge of one frozen n-point orbit does not establish a
compact recurrence.                                 (C29.4)
```

The compiler, coefficient generation, representation size, and uniform transfer across curves must be charged independently.

The executable replay uses states `0,...,n-1` in an auxiliary prime field and fits the cyclic successor map for

```text
n=5,7,11,13,17,19,31.
```

Every cycle is reproduced exactly. The interpolants have degree `n-1`, and the frozen coefficient vectors contain `n-1` or `n` nonzero coefficients. These examples expose the table-fitting mechanism; they are not a universal theorem that every specially structured cycle polynomial must be dense.

## 8. Global algebraic semiconjugacy model

Now impose a genuine global identity. Let

```text
S:E -> V
```

be a nonconstant rational/algebraic state map, and let `R` be one fixed rational self-map of the state space satisfying

```text
boxed:
S(P+G)=R(S(P))                                    (C29.5)
```

as a function identity on `E`, not merely at the `n` marked points.

Let `X` be the normalization of the projective closure of `S(E)`. Since `E` is normal, the map lifts to

```text
S_tilde:E -> X.
```

The update descends to a rational self-map

```text
R_X:X -> X.
```

Since translation by `G` has order `n`, iteration gives

```text
R_X^n o S_tilde
=S_tilde o tau_G^n
=S_tilde.
```

The map `S_tilde` is surjective, so

```text
R_X^n=id_X.                                       (C29.6)
```

Therefore `R_X` is a finite-order automorphism. A fixed global autonomous update cannot exploit repeated degree growth on its actual image: its iterate returns exactly to the identity.

## 9. The normalized image has genus at most one

Factor the finite morphism `E -> X` into its purely inseparable and separable parts. A Frobenius twist of an elliptic curve still has genus one. Applying Riemann-Hurwitz to the separable part shows that a nonconstant image curve cannot have genus greater than one.

Hence

```text
boxed:
g(X) in {0,1}.                                    (C29.7)
```

This reduces every finite-dimensional global autonomous algebraic state, regardless of the number of ambient coordinates, to two curve cases.

## 10. Genus-zero state

Because `S_tilde(O)` is an `F_p`-rational point, a genus-zero `X` is isomorphic to `P^1` over `F_p`.

A finite-order automorphism of `P^1` is a Möbius transformation:

```text
R_X in PGL_2(F_p).
```

The autonomous state must be nontrivial on the marked cycle. Since `n` is prime and `R_X^n=id`, its order must be exactly `n`. Therefore

```text
n divides |PGL_2(F_p)|=p(p^2-1).                 (C29.8)
```

For secp256k1, exact integer arithmetic gives

```text
gcd(n,p(p^2-1))=1.
```

Thus

```text
boxed:
no nonconstant global one-coordinate autonomous rational state over F_p
exists for secp256k1.                              (C29.9)
```

The frozen diagnostic gives the same group-order obstruction for

```text
(p,n)=(43,31),(67,79),(79,67),(163,139).
```

The toy pair `(127,127)` is deliberately not covered because `n=p` divides the `p` factor of `|PGL_2(F_p)|`. Retaining this exception prevents the scoped secp256k1 result from being misreported as a universal statement for all characteristic/order pairs.

## 11. Genus-one state

Suppose `g(X)=1`. Use the rational point

```text
x_0=S_tilde(O)
```

as the origin of `X`. Define

```text
phi(P)=S_tilde(P)-x_0.
```

A morphism of elliptic curves sending identity to identity is a group homomorphism. Since `phi` is nonconstant, it is an isogeny.

Translate the update into the new coordinates. From `(C29.5)`,

```text
phi(P+G)=phi(P)+phi(G).
```

Surjectivity gives the exact update law on all of `X`:

```text
boxed:
R_X(x)=x+phi(G).                                  (C29.10)
```

For the public query:

```text
boxed:
phi(Q)=phi([k]G)=[k]phi(G).                       (C29.11)
```

Thus the canonical scalar has not been shortened, quotiented, or replaced by a bounded-state phase. It is the same `k` on an isogenous marked subgroup.

This is a classification and reduction, not a theorem that isogenous coordinates can never help. A claimed advantage must provide a separate public evaluator on `(X,phi(G),phi(Q))` and a full cost ledger. The autonomous state construction itself has not removed the hidden scalar.

If `phi(G)=O`, the state is constant on `H` and cannot support an exact state-only parity decoder. Therefore any exact autonomous genus-one state retains an order-`n` marked point.

## 12. Consequence for the CM residue state `(A(T),B(T))`

The proposed auxiliary state is

```text
S_AB(Q)=(A(x(Q)^3),B(x(Q)^3)).
```

It is Kummer-even:

```text
S_AB(Q)=S_AB(-Q).
```

Therefore it cannot support a state-only parity decoder, since parity changes sign under `Q -> -Q`.

A decoder using the public coordinates `x(Q),y(Q)` is valid, and the known direct formula does exactly that. But then the complete state contains `Q`. If one additionally demands a fixed global autonomous update for the complete algebraic state, the normalized image falls under the genus-one classification above. The update recodes translation and preserves the same scalar.

Consequently the useful remaining question is not

```text
Does one fixed map update (A,B) for every translation step?
```

It is

```text
Can a target-dependent short composition evaluate A(T),B(T) at one public T
without walking the orbit or materializing their dense coefficients?
```

## 13. Relation to C28 high-degree growth

C28 correctly leaves high-degree low-size circuits open. C29 now separates two subcases.

### Fixed autonomous update

Closed globally by `(C29.6)-(C29.11)`. On the normalized image, the update is a finite-order automorphism. In genus zero it is impossible for secp256k1; in genus one it is translation on an isogenous curve.

### Nonautonomous composition

Still open. A sequence

```text
R_0,R_1,...,R_m
```

may generate enormous algebraic degree in `O(log n)` or several hundred gates without being one finite-order state update. Such a compiler must be target-dependent, addition-chain dependent, modular-composition based, or otherwise nonautonomous.

This is the precise surviving high-degree low-size class.

## 14. Executable replay

The C29 Python package verifies:

```text
7 odd prime cycle orders,
all nonzero cyclic shifts on those orders,
full cyclic parity period,
two-state wrap conflicts,
faithful n-state cycle controls,
7 exact finite-cycle Lagrange interpolants,
5 frozen PGL2 diagnostics,
exact secp256k1 PGL2 coprimality,
6 unit-test groups,
0 failures.
```

The secp256k1 record includes the exact 256-bit semantic orbit size and explicitly states that this is not a memory lower bound.

## 15. Formalization

The Lean file

```text
Ecdlp/Proved/Uorc056AutonomousStateRigidity.lean
```

kernel-checks:

```text
iteration of a semiconjugacy,
equal-state persistence under autonomous updates,
decoder contradiction from future target separation,
injectivity from future target separation,
finite state-cardinality transfer,
the two-state wrap contradiction,
additive recoding phi([k]P)=[k]phi(P),
exact secp256k1 PGL2 order coprimality,
exact frozen arithmetic diagnostics.
```

Lean does not formalize:

```text
normalization of the algebraic image,
Riemann-Hurwitz,
the genus-zero identification with P1,
the classification of genus-one morphisms as translated isogenies,
the transfer from the global geometric theorem to every proposed state variety.
```

Those geometric inputs are stated explicitly and are not labeled kernel-checked.

## 16. Closed classes

C29 closes:

```text
autonomous exact states with fewer than n semantic values and a state-only decoder,
two-state and four-state autonomous parity summaries,
a finite toy recurrence presented without a charged uniform compiler,
global genus-zero autonomous rational states for secp256k1,
global finite-dimensional autonomous algebraic states as a new compression mechanism:
  genus zero is excluded,
  genus one is isogeny recoding.
```

The phrase `as a new compression mechanism` is important. The genus-one case may still be used as an input transformation to another independently justified algorithm.

## 17. Open classes

C29 does not close:

```text
nonautonomous target-dependent composition chains,
branching circuits,
modular composition,
transposed one-point evaluation,
nonlocal joint A/B recurrences whose maps depend on the recursion level,
elliptic-unit or Miller jump identities,
theta or p-adic constructions with a public branch-sensitive seed,
unrestricted arithmetic circuits,
a decoder that performs the hard parity computation directly from Q.
```

## 18. Decision

```text
canonical parity full cyclic period                         yes
autonomous state-only exact decoder requires n states       yes
(g_G,J_G) or W_G closed four-state transition               no
finite-orbit recurrence without compiler evidence           rejected
global genus-zero autonomous state on secp256k1             excluded
global genus-one autonomous state                           isogeny recoding
fixed autonomous high-degree escape                         closed as new compression
nonautonomous target-dependent high-degree compiler         open
public branch-sensitive seed                                absent
exact parity evaluator                                      absent
complete sub-square-root cost gate                          not passed
parity oracle                                               absent
sub-square-root ECDLP                                       absent
```

## 19. Successor

The successor is

```text
TARGET-DEPENDENT-ORIENTED-COMPILER-079.
```

It must attack a nonautonomous public-Q compiler, beginning with the one-point CM residue target

```text
(A(x(Q)^3),B(x(Q)^3)).
```

A positive package must provide a literal sequence of public maps or a uniform compiler generating them, prove exact parity decoding on every marked point, and charge every coefficient, branch seed, field extension, memory cell, and online operation.

A negative package must name one exact nonautonomous grammar and prove a composition-width, branch-information, query, or coefficient-generation lower bound. C29 does not authorize a general circuit lower-bound claim.

Final flags:

```text
canonical_parity_full_cyclic_period=true
autonomous_state_requires_n_semantic_values=true
four_state_autonomous_summary_blocked=true
finite_orbit_interpolation_warning_verified=true
global_genus_zero_state_excluded_for_secp256k1=true
global_genus_one_state_classified_as_isogeny_recoding=true
fixed_autonomous_high_degree_escape_found=false
nonautonomous_oriented_composition_found=false
public_branch_sensitive_seed_found=false
joint_A_B_recurrence_found=false
modular_composition_state_found=false
high_degree_low_size_state_blocked=false
exact_parity_extraction_found=false
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```
