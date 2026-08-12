# PARITY-LIFT-000: EDS residue alignment and normalization audit

Date: 2026-08-11
Status: untrusted, non-executable research intake

This note aligns the generator-relative parity question with the existing
elliptic-divisibility-sequence literature. It records a source-level
normalization discrepancy explicitly rather than hiding it inside notation.
Nothing here computes an unknown-target discrete logarithm or EDS residue.

## 1. Exact target bit

Let `G` generate a cyclic subgroup of odd order `n`, and let

```text
Q = [k]G,   0 < k < n.
```

Write

```text
W_G(k) = psi_k(G)
```

for the associated elliptic divisibility sequence and let `chi` be the quadratic
character of the base field. The EDS Residue bit is

```text
rho_G(Q) = chi(W_G(k)).
```

The surviving algorithmic question is therefore:

> Given only public `(G,Q)`, compute `rho_G(Q)` below the matched generic
> square-root baseline without first recovering `k`.

This is narrower and more exact than asking for an unspecified theta phase.

## 2. Raw point function

For a nonzero point `P` of order `m` relatively prime to `q-1`, define the raw
public point function

```text
phi_raw(P) =
  (W_P(q-1) / W_P(q-1+m))^(1/m^2).
```

The inverse exponent exists when `gcd(m,q-1)=1`. The value is computed from the
point `P`; it does not require knowing a scalar representation of `P`.

The rank-one elliptic-net transport identity gives the unnormalised point
function law

```text
phi_raw([k]P) = phi_raw(P)^(k^2) W_P(k).       (R)
```

The branch replays (R) on fixed toy curves and on fixed known secp256k1 scalar
multiples. This is still only bounded computational evidence until an
independent CAS replay and formal source-level derivation are attached.

## 3. Normalized perfectly periodic sequence

Divide the raw point function by its public value at the base point:

```text
W_tilde_P(k) = phi_raw([k]P) / phi_raw(P).
```

Then (R) is equivalent to

```text
W_tilde_P(k) = phi_raw(P)^(k^2-1) W_P(k).     (N)
```

Thus the `k^2` and `k^2-1` exponents are not interchangeable on an absolute
quadratic-character bit. They describe respectively:

- the raw public point function `phi_raw([k]P)`; and
- the normalized sequence `W_tilde_P(k)`.

Ratios of neighbouring terms cancel the global factor, but absolute residue
claims must name the chosen normalization.

## 4. Published-display discrepancy

Lauter and Stange define the same ratio-root point function and then display

```text
phi([k]P) = phi(P)^(k^2-1) W_P(k).
```

Taken literally at `k=1`, this would imply `phi(P)=W_P(1)=1`. That is not true
for the fixed secp256k1 replay, where the ratio-root value is a nontrivial field
element and a quadratic non-residue.

The surrounding construction immediately before the theorem describes the
`k^2-1` expression as a normalized equivalent sequence, while the raw point
function naturally carries `k^2`. The safest current interpretation is:

- equation (R) for the raw point function;
- equation (N) for the normalized perfectly periodic EDS;
- the published display contains a normalization mismatch or omitted global
  factor.

This branch does **not** label the source an erratum without author confirmation.
It records the discrepancy as an explicit review blocker.

## 5. Exact parity bridge

Assume

```text
chi(phi_raw(G)) = -1.
```

Taking quadratic characters in (R) gives

```text
chi(phi_raw(Q))
  = chi(phi_raw(G))^(k^2) chi(W_G(k))
  = (-1)^k rho_G(Q),
```

because `k^2` and `k` have the same parity. Therefore

```text
boxed:  (-1)^k = chi(phi_raw(Q)) rho_G(Q).     (B_raw)
```

Using the normalized sequence instead gives

```text
chi(W_tilde_G(k))
  = (-1)^(k^2-1) rho_G(Q)
  = -(-1)^k rho_G(Q),
```

hence

```text
boxed:  (-1)^k = -chi(W_tilde_G(k)) rho_G(Q). (B_norm)
```

The two bridges agree after the known global factor is handled correctly.

## 6. secp256k1 fixed-public condition

For the standard secp256k1 field size `p`, subgroup order `n`, and generator
`G`, the frozen verifier records

```text
gcd(n,p-1) = 1,
chi(phi_raw(G)) = -1.
```

It checks (R), (N), (B_raw), and (B_norm) only on a fixed list of known public
scalars. It accepts no external point and never computes `rho_G(Q)` for an
unknown target.

Consequently, on secp256k1 the parity problem is exactly aligned with the
absolute EDS residue problem:

```text
publicly computable factor  x  hidden EDS residue  =  scalar parity sign.
```

This is a reduction of the unknown, not a shortcut.

## 7. Why the public point function alone is insufficient

The value `phi_raw(Q)` is computable from `Q`, but (B_raw) contains the unknown
factor `rho_G(Q)`. Computing only the public side does not determine parity.

Conversely, an exact algorithm for `rho_G(Q)` gives exact parity; the existing
bit-peeling reduction then recovers the entire canonical scalar in at most
`ceil(log2 n)` oracle calls.

Therefore a successful EDS-residue decoder would be a full ECDLP breakthrough,
not a weak auxiliary statistic.

## 8. Fixed-index balance obstruction

For fixed public index `m`, elliptic-net transport has the schematic form

```text
W_Q(m) = W_G(mk) / W_G(k)^(m^2).
```

After perfect-periodic normalization, the quadratic exponent contributions
cancel. Finite products and ratios of a fixed collection of such observations
remain balanced unless a construction introduces an absolute, unbalanced
section or equivalent extra information.

`Ecdlp/Proved/EdsResidueBalance.lean` formalizes the elementary exponent
cancellation used by this obstruction. It does not formalize the full elliptic
net identity or prove EDS Residue hard.

## 9. Surviving mechanism classes

The simple classes screened so far do not recover `rho_G(Q)`:

- a single low-index `chi(psi_m(Q))`;
- finite products or ratios of several fixed low indices;
- sign-erasing Kummer/even-theta/orbit invariants;
- a global order-two translation character on the odd-order point cycle.

The remaining meaningful classes are:

1. an unbalanced theta, sigma, or elliptic-net section whose absolute
   normalization is public and cheap;
2. a p-adic or analytic observable with an exact precision and total-cost
   theorem;
3. a nonlocal relation that fixes the absolute EDS sign from public relative
   residues;
4. a character-sum construction outside the bounded fixed-index family and
   with a demonstrated sub-square-root scaling law.

Each candidate must expose where the missing absolute sign enters and why its
evaluation does not already solve ECDLP internally.

## 10. Current disposition

| Item | Status |
|---|---|
| EDS Residue is the exact surviving bit | source-backed |
| parity-to-ECDLP reduction | proved in Lean |
| raw `k^2` point-function law | derived and bounded-replayed; independent replay pending |
| normalized `k^2-1` law | algebraically equivalent to raw law |
| published equation normalization | discrepancy recorded; author confirmation absent |
| `gcd(n,p-1)=1` for secp256k1 | fixed-public exact computation |
| `chi(phi_raw(G))=-1` | fixed-public replay; independent CAS pending |
| unknown-target `rho_G(Q)` algorithm | absent |
| sub-Pollard complexity claim | absent |

## Sources

- Kristin E. Lauter and Katherine E. Stange, *The elliptic curve discrete
  logarithm problem and equivalent hard problems for elliptic divisibility
  sequences*, SAC 2008 / LNCS 5381, 2009.
- Katherine E. Stange, *Elliptic nets and elliptic curves*, Algebra & Number
  Theory 5 (2011), for elliptic-net transformation laws.
- Repository anchors: `Ecdlp/Proved/ScalarParity.lean`,
  `Ecdlp/Proved/EdsResidueBalance.lean`, and
  `experiments/parity_lift_000/verify_secp_eds_residue_bridge.py`.
