# PUBLIC-FACTOR-QUOTIENT-AUDIT-021

Date: 2026-08-12

Status: exact binary quotient rule plus cross-family finite admission audit.

No external point, key, wallet, or production-sized discrete-log target is
accepted.

## 1. Why exact matching is not sufficient

Several frozen screens found exact formulas for the raw target

```text
R3(k) = rho(k) rho(lambda*k) rho(lambda^2*k).
```

The normalization-aware public point character is

```text
C(k) = s^k rho(k),
s in {+1,-1}.
```

For canonical GLV representatives summing to `gamma*n`, with odd `n`, the
public C3 orbit norm is

```text
P3(k) = C(k)C(lambda*k)C(lambda^2*k)
      = s^gamma R3(k).
```

Therefore an exact `R3` match has two completely different meanings:

```text
s=+1: R3=P3 is already public;
s=-1: R3=carry*P3 and an independent R3 formula reveals carry.
```

Every exact candidate must first be divided by the maximal known public factor.
Only the quotient is admitted as new information.

## 2. Unified admission rules

This audit combines the frozen outputs of:

```text
TRACE-CM-INDEX-SECTIONS-015
POINT-FUNCTION-INTEGER-ORIENTATION-019
SEVENTH-CHARACTER-POINT-FUNCTION-020
```

The rules are:

1. Exact carry is admitted only at order at least `271`.
2. Exact `R3` is admitted only in the point-scale `s=-1` branch.
3. A matched-null or inverse-log spectral signal must occur on at least two
   large cases with order at least `500` in the same family.
4. A learned higher-character lookup must pass its predeclared held-out gate.
5. An `s=+1` exact `R3` match is retained as a regression identity but labeled
   `public_factor_tautology`.
6. Exact carry at orders `19` or `31` is labeled `small_order_resonance`.

## 3. Current cross-family result

For both trace/CM sections and point-function integer orientations:

```text
scale-qualified exact carry matches       0
hard-branch exact R3 matches              0
public-factor exact R3 matches            7 per family
repeated large matched-null signals       0
repeated inverse-log spectral signals     0
```

The seven public exact `R3` orders are exactly the seven point-scale `s=+1`
orders:

```text
19, 31, 67, 271, 547, 571, 4021
```

The seventh-character held-out screen has:

```text
4 unseen curves,
12 target/orientation evaluations,
0 null-95% exceedances,
0 admitted lookup variants.
```

Thus no route survives the quotient, scale, repetition, and held-out gates.

## 4. Formal core

Multiplicative signs are represented as bits in `ZMod 2`; quotienting signs is
bit addition. `Ecdlp/Proved/PublicFactorQuotientAudit.lean` proves:

```text
public/public = 0,
R3/P3 = 0 in the s=+1 branch,
R3/P3 = carry in the s=-1 branch.
```

The theorem is a classification rule. It does not prove that a particular
screened section is public, nor does it formalize the statistical gates.

## 5. Consequence for future searches

Every new candidate should expose its factorization before correlation or exact
matching is scored:

```text
candidate = known_public_factor * residual_candidate.
```

The screen should compare `residual_candidate` against carry and hard-branch
`R3`. This prevents high-order public identities from receiving stronger status
than small-order accidental resonances.

For a candidate with an exact `R3` match:

```text
point-scale s=+1 -> close as a public identity;
point-scale s=-1 -> immediate manual review and exact carry reduction.
```

## 6. Remaining frontier

After quotienting the known public factors, the main unresolved classes are:

```text
integer orientations of the public point function Phi with growing conductor,
higher-order field characters beyond the negative seventh-character screen,
order-dependent sections whose residual is not a public normalized character,
a direct public cyclotomic carry or hard-branch R3 decoder.
```

The public point function remains important because it is computable from the
point without knowing its multiplier, while its defining division-polynomial
indices grow with the field and subgroup order. Fixed-conductor character-sum
bounds used for low-degree coordinate predicates do not directly classify it.

## 7. Artifacts

```text
experiments/parity_lift_000/public_factor_quotient_audit.py
Ecdlp/Proved/PublicFactorQuotientAudit.lean
.github/workflows/public-factor-quotient-audit.yml
```

## Claim boundary

This is a finite cross-family audit and an exact binary factor theorem, not a
universal lower bound. It constructs no public carry, parity, EDS-residue, or
ECDLP oracle.
