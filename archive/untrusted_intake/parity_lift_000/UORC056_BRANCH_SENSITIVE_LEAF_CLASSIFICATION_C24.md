# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C24: branch-sensitive leaf classification and normalization-torsor boundary

Date: 2026-08-14

Status: **C23 proves that rational circuits, determinants, and Sylvester resultants cannot distinguish the two global Hilbert-90 branches when all of their leaves, entries, coefficients, preprocessing state, and advice are identical in the two branch worlds. C24 classifies eleven of the strongest surviving mechanism families by four separate transformation laws: the global branch flip, the geometric involution, generator inversion, and generator replacement. The audit finds mathematically non-fixed objects, including the normalized anti-Frobenius period and the hidden GLV odd aggregate, but none is simultaneously a public leaf, constructible without orientation advice or huge dual state, aligned with the canonical Hilbert-90 branch, and below the complete sub-square-root cost gate. Standard theta-characteristic descent is branch-blind, standard metaplectic theta requires a full dual choice and linear-size state, p-adic continuation preserves an initial seed, known fast torsion sections give dependent equations, and determinants or resultants only transport a non-fixed coefficient that must first be constructed. No parity oracle or sub-square-root ECDLP algorithm is obtained.**

Only committed public artifacts, symbolic models, the frozen public field list, and public secp256k1 constants are used. No external point, unknown scalar, wallet, private key, or production target is accepted.

## 1. The exact C24 question

C23 changes the search criterion. It is no longer enough to propose:

```text
an addition,
a determinant,
a resultant,
a theta basis change,
a p-adic lift,
a normalization rule.
```

The first required object is now a public resource whose value is genuinely different in the two global branch worlds:

```text
W+ : canonical value represented by R,
W- : competing value represented by -R.
```

For a candidate leaf `L`, the first gate is:

```text
L(W+) != L(W-).                                  (C24.1)
```

If `(C24.1)` fails, C23 closes every finite rational circuit, determinant, and Sylvester resultant built from that leaf family, regardless of circuit depth or matrix dimension.

If `(C24.1)` holds only because a sign, dual point, path, characteristic, local trivialization, half-divisor choice, or coefficient has been inserted, that complete seed is itself the branch-sensitive resource and must be charged.

A positive candidate must therefore satisfy all four conditions:

```text
non-fixed under the global branch flip,
publicly constructible from E,G,Q,
canonically normalized without hidden orientation advice,
complete cost O(n^(1/2-epsilon)).                 (C24.2)
```

No audited candidate satisfies all four.

## 2. Four transformations must be separated

Every candidate is classified independently under:

```text
A. global branch flip:       R -> -R,
B. geometric involution:     tau(y)=-y,
C. generator inversion:      G -> -G,
D. generator replacement:    G -> [u]G.
```

These transformations are not interchangeable.

For the Hilbert-90 twist:

```text
tau(R)=R^-1,
```

while the residual constant ambiguity is:

```text
R -> -R.
```

A formula can be odd under point negation, anti-Frobenius, or generator inversion and still fail to select the global Hilbert-90 branch. Conversely, a candidate can be fixed under geometric tau but depend on a generator-relative normalization. Every positive claim must state all four laws rather than use the word "orientation" without specifying the action.

## 3. Abstract collision theorem

Let:

```text
P : World -> PublicData,
T : World -> Target.
```

Suppose two worlds satisfy:

```text
P(w1)=P(w2),
T(w1)!=T(w2).                                    (C24.3)
```

Then there is no universal decoder:

```text
D : PublicData -> Target
```

such that:

```text
D(P(w))=T(w)
```

for every world.

This is the generic quotient-collision theorem. It applies to a sign pair, a theta-characteristic torsor, a projective linearization torsor, a Hensel seed pair, or any group orbit on which the available public data are invariant but the desired target moves.

The corresponding seeded theorem is:

```text
if publicPlus=publicMinus
and F(publicPlus,statePlus)!=F(publicMinus,stateMinus),
then statePlus!=stateMinus.                       (C24.4)
```

Thus a determinant or resultant with separated outputs has not created branch information from equal data. Its complete matrix state, coefficient state, normalization state, or oracle state must already differ.

These statements are formalized in:

```text
Ecdlp/Proved/Uorc056BranchSensitiveLeaf.lean
```

## 4. Machine classification

The C24 audit binds each classification to exact source markers and SHA-256 provenance. Eleven mechanism families are assigned to five disjoint classes:

| class | count | meaning |
|---|---:|---|
| canonical sign-blind | 2 | canonical construction erases or never sees the branch |
| transport only | 2 | aggregate output is only as non-fixed as an explicitly supplied factor |
| branch-sensitive large or seeded | 4 | a non-fixed object exists, but needs a dual state, seed, path, or hidden index |
| public fast but target dependent | 2 | efficiently evaluable section gives no independent target equation |
| open cost unresolved | 1 | not fully excluded, but no compact representation or exact branch law exists |

The exact families are:

```text
FROBENIUS-STICKELBERGER-DETERMINANT-050
INDEPENDENT-THETA-ROW-NORMALIZATION-051
TWISTED-THETA-CHARACTERISTIC-052
METAPLECTIC-THETA-INTERTWINER-053
P-ADIC-GLOBAL-BRANCH-054
ANTI-FROBENIUS-ORIENTATION-SEED-031
ABSOLUTE-EDS-SECTION-003
NONLOCAL-ODD-ANCHOR-004
GLV-CARRY-SEPARATION-005
FIELD-PERMUTATION-CARRY-IDENTITY-017
UORC056-SPARSE-TWO-TRANSLATION-RESULTANT-C5
```

## 5. Canonical sign-blind mechanisms

### 5.1 Standard twisted theta characteristics

On secp256k1 there is no nontrivial base-field two-torsion characteristic. The three geometric nontrivial characteristics form one Frobenius orbit, and their canonical norm is:

```text
product_i (x(P)-r_i)=y(P)^2.
```

After normalization at `G,Q`:

```text
y(Q)^2/y(G)^2.
```

This is unchanged by point negation and generator inversion. It is a canonical square and does not supply the marked branch.

Therefore:

```text
standard_twisted_theta_characteristic_survives_C23=false.
```

A higher-level theta structure with a genuinely non-fixed linearization remains a separate mechanism and is not equated with the closed standard characteristic descent.

### 5.2 Field-permutation GLV carry

The field-ordering predicate satisfies the exact identity:

```text
O_beta(x)=-C_beta((beta-1)x).
```

It is a known field carry after a public invertible change of variable. It is x-only and does not see the Hilbert-90 branch. Its Fourier behavior gives no separate inverse-polylogarithmic scalar observable.

## 6. Transport-only mechanisms

### 6.1 Common-basis Frobenius-Stickelberger determinant

The standard evaluation determinant factors as:

```text
public constant * multiplicative elliptic-net ratio.
```

It contributes no independent additive branch datum. Increasing determinant dimension or using public high indices does not change the factorization class.

### 6.2 Independent row trivializations

For:

```text
A'=diag(r_i) A C,
```

one has:

```text
det(A')=product_i(r_i) det(A) det(C).
```

The determinant sees only the product of the explicit row factors. If that product is branch-sensitive, the branch-sensitive resource was already present in the rows. If the factors are branch-blind, C23 applies.

This is the exact distinction between aggregation and construction.

## 7. Branch-sensitive but large or seeded mechanisms

### 7.1 Standard level-n theta and metaplectic intertwiners

A chosen dual point or dual character gives:

```text
e_n([k]G,T)=omega^k.
```

This is genuinely scalar-sensitive. It is also a full order-n character, not a canonical bit. The standard theta section space has dimension at least `n`, and the linearization ambiguity is the full group:

```text
Hom(H,mu_n).
```

A metaplectic operator changes basis after the theta structures and linearizations are fixed. It does not choose the missing dual direction from the public cyclic line alone.

Disposition:

```text
non-fixed resource exists,
public compact construction absent,
complete cost gate fails.
```

### 7.2 P-adic continuation

Formal sigma and formal logarithm are local to the reduction kernel. Nonzero prime-to-p subgroup points do not enter that kernel under any useful known multiplier. Hensel or Newton lifting continues whichever root seed was initially supplied:

```text
+seed lifts to +branch,
-seed lifts to -branch.
```

Canonical lifting transports the subgroup but does not select the marked branch. A global Coleman path could escape only if its path and period normalization are independently public and non-fixed. No such path is known.

Disposition:

```text
continuation can transport branch data,
continuation does not create the initial branch seed.
```

### 7.3 Normalized anti-Frobenius period

The exact normalized observable:

```text
U_G(Q)=A_G(Q)/A_G(G)
```

has strong covariance:

```text
U_[-G](Q)=-U_G(Q),
U_[uG](Q)=U_G([u^-1]Q)
```

under the chosen character normalization.

This is one of the strongest genuinely generator-sensitive objects in the repository. However, evaluating it still requires the order-n dual phase or an explicit quotient state of size:

```text
(n-1)/6.
```

The source also does not establish that a compact value of `U_G` is the canonical Hilbert-90 branch at the query. Thus:

```text
anti_frobenius_generator_sensitive_observable_known=true,
anti_frobenius_sub_sqrt_evaluator_found=false.
```

### 7.4 Hidden nonlocal GLV odd aggregate

The hidden object:

```text
R3(Q)=rho_G(Q)rho_G(phi Q)rho_G(phi^2 Q)
```

has odd EDS gauge weight and is Kummer/GLV compatible. It is linked to the public orbit norm by the canonical carry bit `gamma`:

```text
C3(Q)=(-1)^gamma(Q) R3(Q).
```

This is a valid structural localization. It is not a public leaf because neither `R3` nor `gamma` has a public compact decoder.

## 8. Public fast but target-dependent mechanisms

### 8.1 First absolute order-n torsion jet

The first invariant torsion jet is fast and genuinely order-dependent. Its exact transformation law on secp256k1 collapses to the already-public point-function factor. It does not provide a second independent equation for the hidden EDS residue or parity.

### 8.2 Known GLV orbit sections

The first torsion jet and the nearest period sections all have the same `gR3` multiplier as the public point-function norm. Bounded products do not isolate `R3` or `g`.

The needed object is not merely another fast algebraic section. It must have a different exact GLV carry multiplier.

Current result:

```text
new_GLV_carry_multiplier_found=false.
```

## 9. Structurally open sparse resultant

The remaining sparse circulant family includes:

```text
D_(a,b,c)(k)=det(aI+bT+cT^k)
            =Res(z^n-1,a+bz+cz^k).
```

Known affine exponent symmetries reject several coefficient subfamilies. The fully asymmetric family and one symmetry-compatible `a=b` family are not completely excluded by those symmetries.

However, no positive C24 leaf exists because:

```text
no non-fixed Hilbert-90 coefficient has been identified,
no exact target branch law has been proved,
the explicit resultant has degree n,
the natural state has dimension n,
no sub-square-root coordinate evaluator is known.
```

A resultant with a non-fixed coefficient would transport that coefficient. C24 finds no public sub-square-root generator for such a coefficient.

Therefore:

```text
sparse_resultant_family_structurally_open=true,
nonfixed_resultant_coefficient_found=false,
complete_cost_gate_passed=false.
```

## 10. Strongest surviving objects

After classification, the best survivors are not eleven unrelated ideas. They reduce to four resource problems:

1. **Normalized anti-Frobenius period**

   Exact generator covariance exists. The missing step is direct evaluation without the full dual phase or quotient state.

2. **Hidden GLV odd aggregate and carry**

   Exact target structure exists. The missing step is a public decoder for `R3`, `gamma`, or a second section with a different carry multiplier.

3. **Higher-level theta linearization**

   A full dual character can encode the scalar. The missing step is a public nonprojective linearization with compact state and no dual advice.

4. **Sparse asymmetric resultant**

   Some coefficient families remain symmetry-compatible. The missing step is both a non-fixed coefficient law and a complete sub-square-root evaluation method.

No candidate is promoted merely because it lies outside one negative theorem.

## 11. Complete cost audit

A positive leaf must charge:

```text
field extensions,
precision,
dual-character construction,
path or characteristic selection,
coefficient generation,
preprocessing,
advice,
memory,
representation,
online evaluation,
branch extraction,
exception handling.
```

Current failures are:

| candidate | missing or oversized resource |
|---|---|
| level-n theta | dual point and dimension at least n |
| metaplectic lift | projective trivialization or full dual character |
| p-adic continuation | initial seed and public global path |
| anti-Frobenius period | dual phase or state of size `(n-1)/6` |
| hidden R3 | public R3 or GLV-carry decoder |
| torsion jets | independent target equation |
| sparse resultant | degree-n state and non-fixed coefficient generator |

Consequently:

```text
C_preprocessing + C_advice + C_memory
+ C_representation + C_online
```

has not been proved to be `O(n^(1/2-epsilon))` for any branch-sensitive leaf.

## 12. Formalization

The new Lean file formalizes:

```text
FactorsThrough(publicData,target),
collision blocks factorization through public data,
two-world branch-sensitive target obstruction,
invariant quotient data cannot compute a moving orbit target,
invariant quotient data cannot globally select orbit representatives,
separated deterministic outputs force separated complete seed/state,
equal public data and equal seed imply equal output.
```

The formal theorem deliberately does not claim that every concrete elliptic-curve candidate factors through invariant public data. C24 records that as a mechanism-specific obligation. This prevents the abstract information theorem from being overextended to a candidate whose public inputs actually contain a new non-fixed resource.

## 13. Reproducible source audit

The executable audit:

```text
experiments/parity_lift_000/uorc056_branch_sensitive_leaf_audit.py
```

verifies:

```text
all eleven source files exist,
all classification-specific source markers remain present,
SHA-256 provenance for each source,
unique candidate identifiers,
exact class counts,
all four transformation fields are explicitly populated,
no candidate is silently promoted through the cost gate,
finite normalization-torsor collision fixtures,
finite-field sign-pair and complete-state fixtures.
```

The finite fixtures illustrate the abstract theorem. The theorem itself is kernel-checked and does not depend on those screens.

## 14. Final flags

```text
branch_sensitive_public_leaf_found=false
branch_sensitive_leaf_constructible_without_advice=false
twisted_theta_survives_C23=false
higher_level_theta_nonfixed_linearization_open=true
p_adic_branch_path_publicly_canonical=false
anti_frobenius_generator_sensitive_observable_known=true
anti_frobenius_sub_sqrt_evaluator_found=false
hidden_GLV_R3_section_known=true
public_GLV_R3_or_carry_decoder_found=false
new_GLV_carry_multiplier_found=false
nonfixed_resultant_coefficient_found=false
compressed_nonfixed_determinant_found=false
sparse_resultant_family_structurally_open=true
complete_cost_gate_passed=false
compact_branch_odd_evaluator_found=false
sub_sqrt_evaluator_found=false
parity_oracle_found=false
sub_sqrt_ecdlp_found=false
```

## 15. Successor

The successor is:

```text
SPARSE-CIRCULANT-PARITY-CLASSIFICATION-074.
```

It should take the one concrete addition-enabled family that remains structurally open:

```text
D_(a,b,c)(k)=Res(z^n-1,a+bz+cz^k),
```

and decide whether any coefficient family can have the exact canonical parity law before attempting a large implementation.

The first obligations are:

1. classify the full `S3` and Möbius action on `(a,b,c,k)`;
2. derive every parity-changing orbit witness for `n=1 mod 4`;
3. identify all coefficient strata not rejected by symmetry;
4. derive a recurrence, transfer matrix, or sparse resultant formula for the surviving strata;
5. charge coefficient bit size, resultant degree, state dimension, preprocessing, and one-value evaluation;
6. reject any method that receives `k`, all roots of unity, or a degree-n object as hidden input;
7. produce either an exact branch/parity formula with total sub-square-root cost or a scoped symmetry/representation no-go theorem.
