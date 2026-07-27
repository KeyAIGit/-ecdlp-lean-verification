# M16 projective exceptional fibers and recovery domain

This directory is the deterministic TASK-017 certificate. It closes the
set-theoretic bridge between the homogeneous projective left-fold tree and
signed-point semantics, classifies every named exceptional stratum, and
executes exact base-field recovery on bounded fixtures.

The terminal result is a scoped blocker. The projective-tree bridge is exact,
but a bridge to a direct `S17` predicate cannot yet be stated precisely:
there is no frozen recursive projective definition of `S17` in the repository
and no reverse theorem above `S4`. This certificate does not define or
materialize that polynomial.

Every local and projective statement below is restricted to the nonsingular
curve \(E:y^2=x^3+7\) over a field \(k\) with
\(\operatorname{char}(k)\notin\{2,3,7\}\). Equivalently, the discriminant
\(-16\cdot27\cdot7^2\) is nonzero in \(k\). In particular,
characteristic seven is excluded even though it is greater than three.

The terminal assurance is `certificate_replayed`. Source independence is
`not_established`, and calibration is `excluded_nonexperimental`. The cost
quantity remains `partial`, the solving cost remains `unpriced`, and the
narrowed barrier and owning cell both remain open.

## Five separate predicates

The certificate keeps the following predicates distinct.

| Predicate | External coordinates | Internal coordinates | Extra condition |
|---|---|---|---|
| `GeoCat_kbar` | \(\mathbf P^1(k)\) | \(\mathbf P^1(\overline{k})\) | homogeneous tree equations |
| `RatCat_Fp` | \(\mathbf P^1(\mathbf F_p)\) | \(\mathbf P^1(\mathbf F_p)\) | homogeneous tree equations |
| `AffCat_Fp` | finite external chart as needed | \(W_i=[u_i:1]\) | \(V_2\cdots V_{15}\ne0\) |
| `Recover_Fp` | exact leaf lifts and full target point \(R\) | supplied projective coordinates | exact point DP and backpointers |
| `DirectS17` | not frozen | not frozen | unresolved |

Write \(Q_i=[X_i:Z_i]\), \(Q_T=[X_T:Z_T]\), and
\(W_i=[U_i:V_i]\). The frozen caterpillar is

\[
\begin{aligned}
H(Q_1,Q_2,W_2)&=0,\\
H(W_{i-1},Q_i,W_i)&=0 &&(3\le i\le15),\\
H(W_{15},Q_{16},Q_T)&=0.
\end{aligned}
\]

It has fourteen internal projective coordinates and fifteen triquadratic
vertices. Every projective pair must differ from \([0:0]\). Only components
supported on an invalid coordinate pair may be removed. Coordinate-equality
loci must remain because they contain tangent and duplicate-root strata.

## Homogeneous local equation

For \(E:y^2=x^3+7\), the multidegree \((2,2,2)\) form is

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

Use the Kummer coordinate

\[
\kappa(O)=[1:0],\qquad \kappa((x,y))=[x:1].
\]

Over an algebraic closure of a field satisfying the nonsingularity and
characteristic restrictions above, the exact local lemma is

\[
H(\kappa(P),\kappa(Q),W)=0
\iff
W=\kappa(P+Q)\ \text{or}\ W=\kappa(P-Q).
\]

The complete case split is finite.

| Inputs | Exact output form | Projective roots |
|---|---|---|
| finite, distinct | \((x_P-x_Q)^2(U-x(P+Q)V)(U-x(P-Q)V)\) | two roots, with discriminant \(16f(x_P)f(x_Q)\) |
| finite, repeated, \(f(x)\ne0\) | \(V(-4f(x)U+(x^4-56x)V)\) | \(O\) and \(\kappa(2P)\), both simple |
| repeated rational two-torsion | \(cV^2\), \(c\ne0\) | \(O\), multiplicity two |
| one identity input | \((XV-ZU)^2\) | the other coordinate, multiplicity two |

Here \(f(x)=x^3+7\). Induction over the fifteen vertices proves the exact
set-theoretic projective-tree to signed-point bridge. Algebraic multiplicity
does not create another point state or another relation. No radicality or
scheme-level equality is claimed.

## Lift and Frobenius partition

For a finite coordinate \(x\), let
\(\chi=\chi_p(f(x))\).

| Condition | Lifts | Frobenius type | Base recovery |
|---|---|---|---|
| \(\chi=+1\) | \(P,-P\in E(\mathbf F_p)\) | plus | retain both |
| \(\chi=-1\) | \(P,-P\in E(\mathbf F_{p^2})\) | minus, \(\pi(P)=-P\) | reject as external nonlift |
| \(\chi=0\) | \(T=(x,0)=-T\) | plus two-torsion | retain once |
| \(O=[1:0]\) | \(O\) | plus | retain identity |
| \([0:0]\) | none | undefined | reject |

For a prefix \(A=B+T\), with

\[
B\in E_+=\ker(\pi-1),\qquad T\in E_-=\ker(\pi+1),
\]

its Kummer coordinate is rational exactly when

\[
\kappa(A)\in\mathbf P^1(\mathbf F_p)
\iff \pi(A)=\pm A
\iff 2T=O\ \text{or}\ 2B=O.
\]

On secp256k1 the absence of rational two-torsion reduces this to
\(T=O\) or \(B=O\). This is the precise ordering invariant. An ordering is
affine-admissible only when every required prefix also differs from \(O\).

## Exhaustive local replays

The producer checks every ordered pair of valid projective coordinates and
every projective output coordinate over two fields.

- \(\mathbf F_7\) is deliberately excluded because
  \(y^2=x^3+7\) is singular in characteristic seven.
- Over \(\mathbf F_{13}\), the curve has no rational two-torsion. All
  \(14^2=196\) ordered input pairs are classified. The fixture includes
  base/base, minus/minus, mixed extension-only, repeated tangent, and identity
  cases.
- Over \(\mathbf F_{11}\), \(x=5\) is rational two-torsion. All
  \(12^2=144\) ordered input pairs are classified. The fixture checks
  repeated two-torsion, distinct two-torsion, ordinary split,
  extension-only, and identity cases with exact multiplicity.

The artifact stores the complete type counts, named examples, and digests of
the exhaustive records.

## Supplied-coordinate recovery replay

The control curve is

\[
E/\mathbf F_{564523}:y^2=x^3+7,
\qquad \#E(\mathbf F_p)=564469=163\cdot3463.
\]

The fixed point \(P=[163](2,100588)\) has order \(3463\). The coordinate
multiset has fourteen copies of \(x(P)\) and two copies of \(x(50P)\), with
target \(R=14P\).

For each supplied projective fiber, recovery fixes the first leaf sign,
tries both exact lifts of every later leaf, retains a state only when its
Kummer coordinate equals the supplied \(W_i\), and keeps all backpointers.
The final state must be \(R\) or \(-R\).

The complete replay gives:

| Quantity | Exact value |
|---|---:|
| unique coordinate orders | 120 |
| normalized sign preimages | 240 |
| projective supplied-coordinate fibers | 239 |
| affine fibers | 238 |
| identity fibers | 1 |
| masks in the identity fiber | `0`, `32766` |
| retained backpointer edges | 3599 |

The two masks in the identity fiber share the same projective coordinates:
the first two \(50P\) leaves cancel, and all later prefixes differ only by
point sign. After duplicate aggregation, every preimage gives the one row

\[
14P-R=O.
\]

The producer checks all 240 raw oriented sums, all 240 target-normalized sums,
and the duplicate-compressed row as exact curve identities.

## secp256k1 GLV lift-sign replay

Let \(P_0\) be the even-\(y\) lift of \(x=1\). The producer constructs and
checks the full signed orbit

\[
\{\pm P_0,\ \pm\phi(P_0),\ \pm\phi^2(P_0)\},
\qquad \phi(x,y)=(\beta x,y).
\]

The fixed M16 row uses fourteen \(x=1\) leaves, seven lifted as \(P_0\) and
seven with negative sign, followed by \(x=\beta\) and \(x=\beta^2\), both
with negative signs. Since

\[
P_0+\phi(P_0)+\phi^2(P_0)=O,
\]

the leaf sum is \(P_0\), which is the fixed target. Membership is exact:
\(1^D=\beta^D=(\beta^2)^D=1\) because \(3\mid D\).

The compressed representative is \(-P_0\). Each canonical even-\(y\) orbit
point is recorded with the actual lift sign \(\eta=-1\). In particular, the
two noncanceling contributions are

\[
(-1)(-1)\lambda=\lambda,\qquad
(-1)(-1)\lambda^2=\lambda^2.
\]

Thus their coefficient on \(-P_0\) is
\(\lambda+\lambda^2=-1\bmod n\), and the compressed check is

\[
-(-P_0)-P_0=O.
\]

Both the raw sixteen-leaf identity and this compressed identity are evaluated
with exact secp256k1 point arithmetic. The artifact binds the replay to the
whole-group membership, GLV eigenvalue, orbit, and exact-cardinality theorems
already present in the repository.

## Reproduce

From the repository root:

```bash
python3 experiments/engine/pkc_smooth_m16_exceptional_fibers/generate.py
python3 experiments/engine/pkc_smooth_m16_exceptional_fibers/generate.py --check
python3 experiments/engine/pkc_smooth_m16_exceptional_fibers/validate.py
python3 experiments/engine/pkc_smooth_m16_exceptional_fibers/test_validate.py
(cd experiments/engine/pkc_smooth_m16_exceptional_fibers && sha256sum -c artifact.sha256)
python3 -m py_compile \
  experiments/engine/pkc_smooth_m16_exceptional_fibers/generate.py \
  experiments/engine/pkc_smooth_m16_exceptional_fibers/validate.py \
  experiments/engine/pkc_smooth_m16_exceptional_fibers/test_validate.py
```

The producer is self-contained and deterministic. The validator reconstructs
the decisive arithmetic without importing producer code, and the fault tests
rehash every mutated fixture so they exercise semantic checks rather than only
the checksum guard. The only artifact dependency is the TASK-016 semantic
bridge at SHA-256
`963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19`.
The producer also binds the primary claim extract
`data/source_claim_extracts/petit_kosters_messeng2016.json` at SHA-256
`f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f`.
The task contract is recorded only as a locator anchor. All listed source and
theorem paths are checked for existence, but task, policy, and generated state
files are not hashed.
