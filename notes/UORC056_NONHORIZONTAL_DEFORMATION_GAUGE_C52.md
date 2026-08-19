# UORC-056 C52: nonhorizontal deformation gauge boundary

Date: 2026-08-19

Status: exact first-order deformation trichotomy, public finite-etale torsion-lift compiler, full-scalar leakage theorem for fixed-fibre vertical tangents, genuine `a`-moduli tangent state, exact finite replay and scoped decoder boundary. No cheap parity decoder, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. Target

Let

\[
E:y^2=x^3+7,
\qquad H=\langle G\rangle,
\qquad |H|=n,
\qquad Q=[k]G.
\]

The target remains

\[
\sigma_G(Q)=(-1)^k.
\]

C51 showed that horizontal point differentiation of normalized sigma/Fay sections cancels the naked quasiperiod. C52 therefore varies the curve and the torsion section itself.

The first gate is strict:

```text
the deformation must be constructible from public E,G,Q;
it may not receive k through dot Q, a path label, tangent advice, or a signed branch table.
```

## 2. Three deformation classes

The first-order problem separates into three mathematically distinct classes.

### 2.1 Finite-etale torsion transport

When the characteristic does not divide `n`, the finite group scheme `E[n]` is etale. An `n`-torsion point therefore has a unique first-order lift along a curve deformation.

If `G_t` is the unique lift of `G`, then `[k]G_t` is an `n`-torsion lift of `Q=[k]G`. By uniqueness it equals the independently constructed lift `Q_t`:

\[
\boxed{Q_t=[k]G_t.}
\]

This construction is public and does not need `k`, because both lifts can be computed locally from their public coordinates. Nevertheless it is horizontal with respect to the discrete torsion label. It transports the same hidden `k`; it does not expose its canonical parity.

### 2.2 Fixed-fibre vertical motion

Keep the curve fixed and give `G` a nonzero tangent vector. Let

\[
\omega=\frac{dx}{2y}
\]

be the invariant differential. The differential of scalar multiplication satisfies

\[
[k]^*\omega=k\omega.
\]

Therefore any tangent pair preserving `Q_t=[k]G_t` obeys

\[
\boxed{
\omega_Q(\dot Q)=k\,\omega_G(\dot G).
}
\]

If `omega_G(dot G)` is nonzero, then

\[
\boxed{
k=\frac{\omega_Q(\dot Q)}{\omega_G(\dot G)}}.
\]

For secp256k1, `0<k<n<p`, so this field element is the full canonical integer scalar, not only a residue ambiguity.

Thus a nonzero public fixed-fibre tangent pair would solve the entire DLP. It cannot be treated as a cheap auxiliary input.

### 2.3 Coordinate and connection gauge

A Weierstrass scaling

\[
x\mapsto u^2x,
\qquad y\mapsto u^3y,
\qquad a\mapsto u^4a,
\qquad b\mapsto u^6b
\]

has infinitesimal form

\[
\dot x=2\alpha x,
\qquad \dot y=3\alpha y,
\qquad \dot a=4\alpha a,
\qquad \dot b=6\alpha b.
\]

It changes coordinates but not the torsion label. More generally, changing a connection adds chosen gauge data. A coefficient proportional to `k` created by an arbitrary connection is not an intrinsic public observable unless the connection itself is canonically and publicly specified.

## 3. Public torsion-lift compiler

For the universal short Weierstrass family

\[
E_{a,b}:y^2=x^3+ax+b
\]

and a nonzero `n`-torsion point `P=(x,y)`, differentiate

\[
\psi_n(x;a,b)=0.
\]

Separability gives `partial_x psi_n != 0`, hence

\[
\boxed{
\dot x
=-\frac{
\dot a\,\partial_a\psi_n+
\dot b\,\partial_b\psi_n
}{\partial_x\psi_n}.
}
\]

Differentiating the curve equation gives

\[
\boxed{
\dot y
=\frac{(3x^2+a)\dot x+
\dot a\,x+
\dot b}{2y}.
}
\]

The values and first partial derivatives of `psi_n` are evaluated by automatic differentiation through the ordinary division-polynomial recurrence. At fixed jet order the index cost is `O(log n)` field operations.

The compiler is therefore public and compact. Its output remains the horizontal finite-etale lift described above.

## 4. The two moduli directions at j=0

At `a=0,b=7`, the `b`-direction is exactly scaling:

\[
\boxed{
\dot x_b=\frac{x}{3b},
\qquad
\dot y_b=\frac{y}{2b}.
}
\]

It is gauge and cannot create the missing parity branch.

The `a`-direction is genuinely transverse to the `j=0` locus. Under the GLV endomorphism

\[
\phi(x,y)=(\beta x,y),
\qquad \beta^3=1,
\]

its tangent transforms as

\[
\boxed{
\dot x_a(\phi P)=\beta^2\dot x_a(P),
\qquad
\dot y_a(\phi P)=\beta\dot y_a(P).
}
\]

Define the GLV-invariant quotient variables

\[
T=x^3,
\qquad R=x\dot x_a,
\qquad S=\frac{x^2\dot y_a}{y}.
\]

The differentiated curve equation gives the exact relation

\[
\boxed{
2(T+7)S=T(3R+1).
}
\]

This is a real new field-valued state with a logarithmic-cost builder. It is not, however, an independent two-coordinate state: `S` is rationally determined by `T` and `R`.

## 5. Decoder screens

The replay tests 22 public deformation features, including

```text
dot x_a, dot y_a, dot x_b, dot y_b,
invariant-differential values,
anchor-normalized ratios,
2 by 2 tangent determinants,
anchor/query wedges,
position determinants,
R=x dot x_a,
S=x^2 dot y_a/y.
```

For each feature, every affine quadratic-character decoder

\[
\chi(f(Q)+c),
\qquad c\in\mathbb F_p,
\]

is checked exactly.

Every projective curve direction

\[
(\dot a:\dot b)\in\mathbf P^1(\mathbb F_p)
\]

is also checked for the outputs

\[
\dot x,
\quad \dot y,
\quad \omega(\dot P),
\quad x\dot y-y\dot x.
\]

No direct character decoder survives on any declared curve.

A uniform structural grammar across all 12 curves contains 3,872 declared atoms. Only 89 are nonzero on every row. Their arbitrary-product span has rank 83 and does not contain parity.

A complete projective affine screen on the smallest curve tests 13,251 pair-state atoms and finds no exact single atom. Arbitrary products on one small curve can interpolate parity and are explicitly classified as finite overfit rather than a uniform identity.

## 6. Exact replay

The deterministic replay covers

```text
12 prime-to-characteristic curves
4 frozen curves
8 held-out curves
4,392 nonzero torsion rows
13,176 horizontal transport checks
8,784 Weierstrass scaling checks
4,392 full-scalar vertical-tangent recoveries
4,392 negation covariance checks
4,392 GLV covariance checks
3,872 uniform structural character atoms
89 valid everywhere-nonzero atoms
GF(2) span rank 83
13,251 complete p=43 pair-affine atoms
0 exact single survivors
0 arithmetic errors
```

The CM quotient polynomials are near the full interpolation ceiling in the declared corpus. The maximum degree deficit is 8 and the maximum number of zero coefficients is 1. This is finite evidence only, not a circuit lower bound.

## 7. secp256k1 certificate

The production certificate uses the standard public constants

```text
p, n, G, beta, lambda.
```

It verifies

```text
14 public scalar samples
42 horizontal transport checks
28 scaling checks
14 vertical full-scalar recoveries
14 GLV covariance checks
```

The public `a`-deformation state is evaluable by a first-jet recurrence in `O(log n)` index cost. No decoder from that state to parity is found.

## 8. Decision

```text
Public finite-etale torsion-lift compiler              found
Functorial deformation preserves Q_t=[k]G_t            yes
New canonical torsion label exposed                    no
Fixed-fibre nonzero tangent pair                       reveals full k
Weierstrass scaling breaks gauge                       no
Genuine a-moduli tangent state                         found
Simple and declared structural character decoder       absent
Public endpoint-charged nonhorizontal deformation      absent
Cheap parity decoder                                   absent
Parity oracle                                          absent
Sub-square-root ECDLP                                  absent
```

## 9. What remains open

C52 does not prove a lower bound against arbitrary nonlinear functions of the moduli tangent state. It also does not close every possible Gauss-Manin, p-adic, theta, or connection construction.

The next package is

```text
CONNECTION-DEFECT-AND-MODULI-TANGENT-DECODER-C53
```

with two precise tasks:

1. classify the connection defect
   \[
   \Delta_k^\nabla(G)=\nabla([k]G)-d[k]_G\nabla(G)
   \]
   and distinguish intrinsic information from chosen gauge;
2. attack nonlinear decoders of the genuine `a`-deformation quotient state without inserting `k` into tangent advice.

Any positive mechanism must include the full preprocessing, advice, branch, precision, memory, representation and online cost.

## 10. Claim boundary

C52 does not claim:

1. an unrestricted deformation or connection lower bound;
2. nonexistence of every nonlinear tangent-state decoder;
3. a parity oracle;
4. a sub-square-root ECDLP algorithm.

It gives an exact deformation trichotomy, a literal public first-order compiler, exact toy and secp256k1 replay, held-out screens, a Lean-checked algebraic core and a narrowly defined successor.
