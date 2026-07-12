# Experiments — index

Reproducible cryptanalytic-mathematics experiments for the ECDLP substrate. Each is an
*honest measurement*, not a claim: it either advances a testable direction in
`HYPOTHESES.yaml` or closes a window. The governing rule (learned the hard way — see the
retraction noted in `p0_glv_semaev/`) is **measure what the code actually does, and verify
it independently before reporting**. Every experiment ships its own brute-force / replay
validator, and no experiment here touches the Lean ledger or the headline theorem count.

## The GLV–Semaev line (`HYP_GLV_SEMAEV_001`, status: ACTIVE)

The hypothesis: for `j=0` curves `E_b: y²=x³+b` over `p≡1 (mod 3)`, does closing a Semaev
factor base under the order-3 GLV automorphism orbit (`x ↦ βx`, invariant `u=x³`) change
the *relation-generation* behaviour beyond a constant factor? Expected honest outcome is a
**negative / no-go**; the value is a reproducible barrier map. Three rungs so far, each a
strictly sharper test of the *same* question:

| rung | dir | what it measures | method | verified by | measured verdict |
|---|---|---|---|---|---|
| **P0** `p0_glv_semaev/` | m=2 | relation **yield law** | ENUMERATE all pair sums `P_i±P_j`, hash x-coords — Θ(\|F\|²) | every hit re-checked by `ec_add`; `validate_run.py` | yield `≈ c·B²/p`; GLV = constant ~3× factor, **no exponent change**. Lookup model only. |
| **P1** `p1_petit/` | m=2 | relation **solving** | SOLVE `S₃(x_i,X,x_R)=0` per base x-coord (Tonelli–Shanks) — O(\|F\|)/target | `validate.py`: independent O(\|F\|²) brute-force EC enum → identical set, spurious=0, PASS | same relation set as P0 obtained by *solving* not enumerating; GLV = constant ~3× storage. |
| **m=3** `p1_petit_m3/` | m=3 | 3-term relation **solving** | SOLVE `S₄=Res_X(S₃,S₃)=0` (deg ≤4 in `x_k`) per base pair — O(\|F\|²·deg4)/target | `validate.py`: independent O(\|F\|³) brute-force triple EC enum → identical set, spurious=0, PASS | S₄-solve complete & sound; GLV = constant ~3× storage. |

**What the line establishes (measured):** the GLV/`u=x³` orbit closure gives a **constant**
(~3×) reduction in stored factor-base seeds at every rung, and the summation-polynomial
*solve* reproduces exactly the brute-force relation set with **zero spurious roots** — the
direct empirical signature of Semaev's `S_m` iff-theorems.

**What the line does NOT establish (open):** none of these rungs builds or reduces an actual
`S_m` polynomial *system*; none measures a **degree of regularity**, a **Gröbner-basis**
cost, `m ≥ 4`, or a faithful **Petit** composed-rational-map construction; and none draws an
asymptotic or advantage/no-advantage conclusion. The `O(\|F\|^{m-1}·solve)` loops are **not**
subexponential index-calculus algorithms. So the real question — whether invariant-coordinate
*relation generation* changes the prime-field asymptotics — remains **open**, and
`HYP_GLV_SEMAEV_001` stays **ACTIVE**. No result here is a step toward breaking secp256k1.

## Conventions
- Toy curves come from `p0_glv_semaev/toy_curves.py` (`find_toy_curve(bits, seed, require_cofactor_one=True)`); only **cofactor-1** (prime-order) curves are used.
- Every run writes a provenance manifest (`manifest.py`: code hashes + seed + params + tool versions + output hash) under the experiment's `runs/`.
- Reproduce any rung: `python3 run.py` then `python3 validate.py` (must print `VALIDATION: PASS`); the `*solve*.py` modules run their own unit self-tests as `__main__`.
- Citations to prior art (Semaev, Gaudry, Diem, Faugère–Gaudry–Huot–Renault, Petit) are catalogued in `data/source_registry.json`.

## Other directions

| exp | hypothesis | what it measures | verified by | verdict |
|---|---|---|---|---|
| **P2** `p2_ward_eds/` | `HYP_WARD_EDS_001` (proposed) | Ward EDS rank-of-apparition `ρ(P)` + zero set | `validate.py`: 900 `(P,n)` samples cross-checked by `ec_mul`, PASS | `ρ(P)=ord(P)`, zero set = multiples of `ord(P)`; **confirms** the classical `Wₙ≡0 ⟺ [n]P=O` torsion equivalence and nothing more. DESCRIPTIVE — `ρ(P)` is Θ(ord(P)) work, **no** DLP advantage. |

## Next
See `HYPOTHESES.yaml` for the open `tests:` (the `REMAINING:` items under
`HYP_GLV_SEMAEV_001`). New experiments follow the same measure-and-independently-verify
discipline.
