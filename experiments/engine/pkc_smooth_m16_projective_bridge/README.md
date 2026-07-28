# Recursive projective S17 definition and boundary certificate

This directory is the deterministic producer-side TASK-018 certificate. It
freezes one recursive projective definition of `S17`, including all formal
degrees, coordinate order, binary coefficient order, Sylvester row order, and
normalization rules. It does not expand or evaluate `S17`.

The result is deliberately a `scoped_blocker` with
`zero_retention_success`. The algebraic forward argument is recorded and
bounded `C4=S5` instances are replayed, but neither the generic symbolic
`C16` forward implication nor the universal reverse induction is
computationally or kernel proved. In particular, this producer does not claim
a universally established equivalence between recursive resultant vanishing
and the projective tree.

Assurance is `certificate_replayed`, source independence is
`not_established`, and calibration is `excluded_nonexperimental`. No solver,
experiment, hypothesis, route promotion, rank, yield, or cost claim is
created.

## Field and projective domain

Every statement is restricted to the nonsingular curve

\[
E:y^2=x^3+7
\]

over a field \(k\) with
\(\operatorname{char}(k)\notin\{2,3,7\}\). Its discriminant is
\(-16\cdot27\cdot7^2\), so characteristic seven is explicitly excluded.

Write

\[
Q_i=[X_i:Z_i],\qquad Q_T=[X_T:Z_T],\qquad T=[T_U:T_V].
\]

Every projective coordinate pair must differ from \([0:0]\). Only the union
of invalid coordinate-pair loci may be excluded. Identity, tangent,
two-torsion, duplicate-coordinate, and duplicate-root loci must remain.

The Kummer coordinate is

\[
\kappa(O)=[1:0],\qquad \kappa((x,y))=[x:1].
\]

## Frozen local form

For three projective pairs, use the TASK-017 triquadratic

\[
\begin{aligned}
H={}&X_1^2X_2^2Z_3^2+X_1^2Z_2^2X_3^2+Z_1^2X_2^2X_3^2\\
&-2X_1^2X_2Z_2X_3Z_3
-2X_1Z_1X_2^2X_3Z_3
-2X_1Z_1X_2Z_2X_3^2\\
&-28\left(
X_1Z_1Z_2^2Z_3^2+
Z_1^2X_2Z_2Z_3^2+
Z_1^2Z_2^2X_3Z_3
\right).
\end{aligned}
\]

It has multidegree \((2,2,2)\).

## Fixed recursive definition

The base case is

\[
C_2(Q_1,Q_2;Y)=H(Q_1,Q_2,Y).
\]

For \(3\le r\le16\), freeze

\[
C_r(Q_1,\ldots,Q_r;Y)=
\operatorname{hRes}^{\,2^{r-2},\,2}_{T}
\left(
C_{r-1}(Q_1,\ldots,Q_{r-1};T),
H(T,Q_r,Y)
\right).
\]

The recursive projective predicate is

\[
\operatorname{RecS17}_k(Q_1,\ldots,Q_{16},Q_T)
\iff C_{16}(Q_1,\ldots,Q_{16};Q_T)=0.
\]

The elimination topology is the fixed left fold. No balanced-tree,
permutation, primitive-part, or actual-degree substitution is implicit in
this name.

## Degree schedule

Let \(d_r=2^{r-1}\). Then \(C_r\) has declared projective degree \(d_r\) in
each of its \(r+1\) coordinate pairs.

| Form | Resultant formal degrees | Sylvester size | Degree per pair |
|---|---:|---:|---:|
| `C2` | base `H` | — | 2 |
| `C3` | `(2,2)` | 4 | 4 |
| `C4` | `(4,2)` | 6 | 8 |
| `C5` | `(8,2)` | 10 | 16 |
| `C6` | `(16,2)` | 18 | 32 |
| `C7` | `(32,2)` | 34 | 64 |
| `C8` | `(64,2)` | 66 | 128 |
| `C9` | `(128,2)` | 130 | 256 |
| `C10` | `(256,2)` | 258 | 512 |
| `C11` | `(512,2)` | 514 | 1024 |
| `C12` | `(1024,2)` | 1026 | 2048 |
| `C13` | `(2048,2)` | 2050 | 4096 |
| `C14` | `(4096,2)` | 4098 | 8192 |
| `C15` | `(8192,2)` | 8194 | 16384 |
| `C16` | `(16384,2)` | 16386 | 32768 |

Thus `C16` has multidegree 32768 in each of the seventeen external
coordinate pairs \(Q_1,\ldots,Q_{16},Q_T\).

- The sum of the seventeen affine multidegree capacities is 557056.
- With a fixed target, the sixteen-leaf subtotal is 524288.

These are capacity sums, not the actual total degree, solving degree, degree
of regularity, matrix size, memory, rank, yield, or work estimate.

## Coefficient and Sylvester conventions

For a fixed-degree binary form

\[
F(U,V)=\sum_{i=0}^{m}f_iU^{m-i}V^i,
\]

store coefficients as \([f_0,\ldots,f_m]\), in descending \(U\)-degree.
Dehomogenization uses \(F(t,1)\), but the declared degree \(m\) and every
leading zero coefficient are retained.

For formal degrees \((m,n)\), the \((m+n)\)-square Sylvester matrix has:

1. \(n\) shifted rows of \([f_0,\ldots,f_m]\);
2. \(m\) shifted rows of \([g_0,\ldots,g_n]\).

The homogeneous resultant is the ordinary determinant of this literal
matrix. No content division, primitive-part extraction, monic normalization,
or actual-degree reduction is allowed.

The literal determinant has coefficient unit \(1\) only when the argument
order, binary coefficient order, formal degrees, Sylvester row order, and
determinant convention are exactly those frozen here. Projective coordinate
rescaling is different: rescaling a valid coordinate representative
multiplies \(C_r\) by the corresponding nonzero field scalar raised to its
declared degree \(d_r\). For `C16`, each of the seventeen representative
scalars occurs to exponent 32768. No variable-dependent factor may be
discarded.

This convention retains infinity: \([1:0]\) is a common root exactly when
both retained formal leading coefficients vanish.

## Predicate boundaries

The artifact keeps four predicates separate.

| Predicate | External coordinates | Internal coordinates | Status |
|---|---|---|---|
| `RecS17_k` | \(\mathbf P^1(k)^{17}\) | none | frozen determinant DAG |
| `GeoCat_kbar` | \(\mathbf P^1(k)^{17}\) | \(\mathbf P^1(\bar k)^{14}\) | TASK-017 homogeneous tree |
| `RatCat_Fp` | \(\mathbf P^1(\mathbf F_p)^{17}\) | \(\mathbf P^1(\mathbf F_p)^{14}\) | base-field tree |
| `Recover_Fp` | exact leaf lifts and full target point | supplied valid tree and backpointers | exact point recovery |

The recorded algebraic forward target is

\[
\operatorname{GeoCat}_{\bar k}\Longrightarrow\operatorname{RecS17}_k.
\]

The argument is common-projective-root vanishing at each fixed resultant
step. This producer directly replays it only for bounded `C4=S5` fixtures; it
does not computationally or kernel prove generic symbolic `C16`
specialization. Its exact status is
`algebraic_argument_recorded_bounded_replay`.

The intended reverse would repeatedly recover a common projective root from
the fixed resultant, from `C16` down to `C2`. It remains `unproved_target`.
The missing bridge in both generic directions is specialization
compatibility of the symbolic fixed-degree resultant, including
specialization of the output at \([1:0]\). Consequently the universal
equivalence

\[
\operatorname{RecS17}_k\iff\operatorname{GeoCat}_{\bar k}
\]

is not claimed by this certificate.

The recorded algebraic argument likewise predicts that `RatCat_Fp` implies
recursive-resultant vanishing. The producer checks that implication for every
bounded `C4=S5` tuple over F5, F11, and F13, not for generic `C16`. Valid
`Recover_Fp` input implies `RatCat_Fp` on its supplied tree by definition.
The reverse implications are not established universally. TASK-017 records
signed-point semantics only on its stated lift and supplied-tree domains.

## Exact fixtures

### Fixed degree retains infinity over F5

For the tuple \((0,0,3,3)\), the two binary quadratics are

\[
H(0,0,[U:V])=2UV,\qquad
H(3,3,[U:V])=V(4U+3V).
\]

Their fixed \((2,2)\) resultant is zero because they share \([1:0]\).
Incorrectly reducing both affine polynomials to actual degree one gives
resultant \(1\pmod5\). This detects deletion of the valid identity/infinity
stratum.

### Combined nonlift and F25 witness

For the five external coordinates \((0,0,3,0,3)\), the top `C4=S5`
elimination uses

\[
C_3(0,0,3;T)=
T^4+2T^3+3T+1
\]

and

\[
H(T,0,3)=4T^2+2T+1.
\]

The exact quotient is \(4T^2+T+1\), and the quadratic discriminant is
\(3\pmod5\). It has no root in \(\mathbf F_5\), but in

\[
\mathbf F_{25}=\mathbf F_5[\alpha]/(\alpha^2+3\alpha+4)
\]

the common roots are \(\alpha\) and \(\alpha^5=2-\alpha\). The explicit tree
witness uses \(W_2=0\) and \(W_3=\alpha\).

At the same time \(x=0\) has curve right-hand side \(2\), a nonsquare in
\(\mathbf F_5\). The exact disposition is therefore `EXTERNAL_NONLIFT`.
This is a combined nonlift/extension witness, not a pure internal-extension
counterexample with all external coordinates liftable.

### Exhaustive bounded S5 boundary

The producer enumerates every ordered tuple in
\(\mathbf P^1(\mathbf F_p)^5\), evaluates the literal fixed \((4,2)\)
Sylvester determinant, and independently enumerates all two-internal-node
`RatCat_Fp` witnesses.

| Field | All tuples | Resultant zero | Zero tuples with no Fp tree | Zero tuples with at least one Fp tree | Base-liftable zeros | Base-lift Rec/Rat mismatches |
|---|---:|---:|---:|---:|---:|---:|
| F5 | 7776 | 1648 | 576 | 1072 | 432 | 0 |
| F11 | 248832 | 23328 | 7976 | 15352 | 6442 | 0 |
| F13 | 537824 | 87507 | 6360 | 81147 | 766 | 0 |

The rows establish only a bounded `C4=S5` boundary. A recursive zero without
an \(\mathbf F_p\)-tree is not labelled extension-only unless an explicit
extension-field witness is constructed. The universal `C16` reverse remains
open.

## Strata policy

- Retain identity and infinity.
- Retain tangents and repeated inputs.
- Retain rational two-torsion.
- Retain duplicate coordinates and duplicate roots.
- Retain extension roots for geometric predicates when explicitly witnessed.
- Reject external nonlifts from `Recover_Fp`.
- Exclude only the invalid pair \([0:0]\).

No radicality, scheme equality, or multiplicity-preservation statement is
made.

## Reproduce

From the repository root:

```bash
python3 experiments/engine/pkc_smooth_m16_projective_bridge/generate.py
python3 experiments/engine/pkc_smooth_m16_projective_bridge/generate.py --check
python3 experiments/engine/pkc_smooth_m16_projective_bridge/validate.py
python3 experiments/engine/pkc_smooth_m16_projective_bridge/test_validate.py
(cd experiments/engine/pkc_smooth_m16_projective_bridge && \
  sha256sum -c artifact.sha256)
python3 -m py_compile \
  experiments/engine/pkc_smooth_m16_projective_bridge/generate.py \
  experiments/engine/pkc_smooth_m16_projective_bridge/validate.py \
  experiments/engine/pkc_smooth_m16_projective_bridge/test_validate.py
```

The producer is self-contained and deterministic. The validator is
independent of the producer and shared helpers; its fault suite rehashes
semantic mutations and separately checks a stale sidecar. The certificate
binds TASK-017 at
SHA-256
`578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf`,
TASK-016 at
`963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19`,
and the primary claim extract at
`f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f`.
