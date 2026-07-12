# P2 RESULTS — Ward-EDS rank of apparition & torsion zero set (`HYP_WARD_EDS_001`)

**Measured, not asserted.** Every EDS-derived torsion fact below is independently re-verified by
an actual `ec_mul` group computation. Numbers are for the sizes actually run only. **No growth
fit, no asymptotic claim, and no "advantage / no-advantage" conclusion is drawn.** This rung
CONFIRMS the known `psi_n`-torsion equivalence numerically; it does not test any attack.

- **Method:** normalized Ward EDS `W_n = psi_n(P)` mod `p` via closed forms `W_0..W_4` + the
  doubling recurrence; large indices via the `O(log n)` single-term `eds_term`.
- **Curves:** corrected cofactor-1 `E_b : y² = x³ + b` from
  `experiments/p0_glv_semaev/toy_curves.py`, `find_toy_curve(bits, seed=1,
  require_cofactor_one=True)` — whole group `E(F_p) = ⟨G⟩` of **prime** order `ell`.
- **Determinism:** `seed = 1`. The manifest is written to
  `runs/HYP_WARD_EDS_001_p2-ward-eds_<id>.json`; the `<id>` suffix is derived from the run's UTC
  timestamp, so it differs on each replay while the measured numbers below are stable.

## Measured table — rank of apparition vs order

| bits | p | b | ell = #E (prime, cof 1) | `rho(G)` (least EDS zero) | `ord(G)` (independent `ec_mul`) | match | zero set `{n≤N : W_n≡0}` | `= {mult. of ord}` (each `ec_mul`-confirmed) |
|---|---|---|---|---|---|:--:|---|:--:|
| 16 | 65 539 | 11 | 65 287 | **65 287** | **65 287** | ✅ | {65 287, 130 574, 195 861} | ✅ |
| 20 | 1 048 609 | 29 | 1 047 379 | **1 047 379** | **1 047 379** | ✅ | {1 047 379, 2 094 758, 3 142 137} | ✅ |
| 24 | 16 777 333 | 2 | 16 785 211 | **16 785 211** | **16 785 211** | ✅ | {16 785 211, 33 570 422} | ✅ |

`rho(G) = ord(G) = ell` on every curve. The zero set within the scanned range `N` is **exactly**
the set of multiples of `ord(G)` (`N = 3·ell` for 16/20-bit, `N = 2·ell` for 24-bit; see scaling
note), and every zero index was re-confirmed by `[n]G = O` via `ec_mul`.

## Measured cross-checks (per curve, `seed=1`)

Console output of `run.py`:

```
[16b p=     65539 ell=     65287] rho(G)=65287 ord(G)=65287 appar_match=True | zeroset=[65287, 130574, 195861] ==multiples? True (ec_ok=True) | fullscanPts=5 match=True divPts=20 match=True | (P,n) samples=400 zeroCases=145 mismatch=0 | ward=999 somos=1000 | 1.098s
[20b p=   1048609 ell=   1047379] rho(G)=1047379 ord(G)=1047379 appar_match=True | zeroset=[1047379, 2094758, 3142137] ==multiples? True (ec_ok=True) | fullscanPts=3 match=True divPts=20 match=True | (P,n) samples=400 zeroCases=132 mismatch=0 | ward=998 somos=1000 | 3.214s
[24b p=  16777333 ell=  16785211] rho(G)=16785211 ord(G)=16785211 appar_match=True | zeroset=[16785211, 33570422] ==multiples? True (ec_ok=True) | fullscanPts=1 match=True divPts=20 match=True | (P,n) samples=400 zeroCases=127 mismatch=0 | ward=998 somos=1000 | 35.673s
[growth] infinite-order (3,5)/y^2=x^3-2 digit-lengths W_1..10=[1, 2, 3, 4, 8, 11, 14, 19, 24, 30] (no zeros? True); torsion (2,3)/y^2=x^3+1 apparition_Z=6
```

Console output of the independent `validate.py`:

```
[HYP_WARD_EDS_001_p2-ward-eds_<id>.json] errors=0 warnings=0
cross-check: 900 independent (P,n) torsion samples across 16/20/24-bit (311 genuine zero cases), 180 EDS<->group coordinate-identity checks; all consistent with ec_mul

VALIDATION: PASS
```

What each measured column means:

1. **`rho(G) = ord(G) = ell` (apparition).** The least `n>0` with `W_n(G) ≡ 0 (mod p)`, found by
   scanning the generated EDS, equals the order of `G` computed independently by `ec_mul`. Held on
   all three curves.

2. **Zero set = multiples of the order.** Within the scanned range, `{n : W_n ≡ 0}` is exactly the
   arithmetic progression `ell·{1,2,...}`; **each** member was re-verified `[n]G = O`, and a sample
   of 200 non-multiples was re-verified `W_n ≠ 0 ∧ [n]G ≠ O`. So the EDS zeros are precisely the
   torsion indices — measured, not assumed. (This also makes the **zero-pattern period** exactly
   `rho = ell`. The full value-period of `W_n mod p` is large: no period `≤ 30·ell` was found on the
   16-bit curve, so it is left **undetermined** here — not claimed.)

3. **Random points.** For random `P = [s]G`: full-scan points (5 / 3 / 1 at 16 / 20 / 24-bit) had
   their entire zero set in `[1, ell]` equal to `{ell}`, i.e. `rho(P) = ell`; 20 further points per
   curve confirmed `rho(P) = ell` by the divisor argument (`W_ell(P)=0`, `W_1≠0`, `ell` prime), each
   matched by `ec_mul`. All matched.

4. **Broad `(P,n)` torsion equivalence.** 400 `(P,n)` samples per curve (`run.py`) and 900 fresh
   samples in `validate.py` — mixing small `n`, `n ≈ ell`, and exact multiples of `ell` — gave
   `W_n ≡ 0 ⟺ [n]P = O` with **0 mismatches** (311 genuine both-zero cases in the validator).

5. **Recurrence identities.** Ward's full master recurrence (~1000 random `(m,n)` per curve) and the
   `n=2` Somos-4 slice (1000 random `m` per curve) hold on the generated sequence — the same
   Somos-4 identity proved over any `CommRing` in `Ecdlp/Proved/NormEDSSomos4.lean`.

6. **Coordinate identity (independent tie).** 180 checks of `x([n]P) = x_P − W_{n-1}W_{n+1}/W_n²`
   against real `ec_mul` coordinates — links the EDS values to the group law through separate
   arithmetic. All held.

7. **Growth over Z (tiny cases).** For the infinite-order point `(3,5)` on `y²=x³−2`, `|W_n|` grows
   doubly-exponentially with no zeros (`W_1..10` digit-lengths `1,2,3,4,8,11,14,19,24,30`); for the
   torsion point `(2,3)` on `y²=x³+1` (order 6 over Q) the integer EDS vanishes exactly at
   `n = 6, 12` — apparition over Z equals the order, illustrating the same law with an exact zero.

## What this does NOT establish

This experiment measures known EDS structure and supports **no** ECDLP complexity claim. In
particular it does **not** test, and nothing here should be read as evidence about:

- **Any EDS-based attack or DLP speedup.** Computing `rho(P)` requires either scanning `n` up to
  `ord(P)` or already knowing the group structure; it is `Θ(ord(P))` work — the **same order** as
  the DLP it would need to solve — not a shortcut. The `O(log n)` `eds_term` evaluates `W_n` at a
  *given* `n`; it does not find the first zero cheaply.
- **`p`-adic, anomalous-curve (Smart/SSSA), or Weil/Tate-pairing methods.** None are implemented or
  implied. EDS here are a structural probe, not a lifting or descent.
- **Any invariant/GLV coordinate advantage.** Not tested on this rung (that is P0/P1's subject).
- **Asymptotics / scaling in `p`.** Three field sizes, chosen for correctness of the apparition and
  torsion measurement, not a growth exponent. No `T(p)`, no `p^{1/2−ε}`, no verdict.
- **Any statement about secp256k1.** Toy curves only. No break is observed or implied.

**EDS re-encode elliptic-curve point arithmetic** (the coordinate identity above makes this
explicit); they give **no known prime-field ECDLP advantage**. This rung only **confirms the
`psi_n`-torsion equivalence numerically**.

## Scaling note (24-bit)

The 24-bit apparition scan is `Θ(ell) ≈ 1.7·10⁷` field operations; computing the full sequence to
`3·ell` (as at 16/20-bit) and running several full-scan random points would be minutes of pure
Python. To stay fast the 24-bit run uses `N = 2·ell` for the zero set and **one** full-scan random
point (20 divisor-argument points and 400 `(P,n)` samples are unaffected, since `eds_term` is
`O(log n)`). All 24-bit checks that ran passed identically to the smaller sizes.

## Honest verdict

`rho(P) = ord(P)` and `{n : W_n ≡ 0} = ord(P)·ℤ` are **measured and independently `ec_mul`-verified**
on 16/20/24-bit cofactor-1 toy curves, with 0 mismatches across ~2100 torsion checks and full
recurrence/coordinate cross-checks (`VALIDATION: PASS`). This **confirms the classical
`psi_n`-torsion equivalence numerically** and nothing more: no attack, no speedup, no asymptotic
claim, no statement about secp256k1. `HYP_WARD_EDS_001` stays **proposed**; no Lean formalization
is triggered by a confirmation of already-known structure.
