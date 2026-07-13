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
the *relation-generation* behaviour beyond a constant factor? The experiments seek reproducible
partial evidence; a general no-go is not assumed. Five rungs so far, each a
strictly sharper test of the *same* question:

| rung | dir | what it measures | method | verified by | measured verdict |
|---|---|---|---|---|---|
| **P0** `p0_glv_semaev/` | m=2 | relation **yield law** | ENUMERATE all pair sums `P_i±P_j`, hash x-coords — Θ(\|F\|²) | every hit re-checked by `ec_add`; `validate_run.py` | yield `≈ c·B²/p`; GLV = constant ~3× factor, **no exponent change**. Lookup model only. |
| **P1** `p1_petit/` | m=2 | relation **solving** | SOLVE `S₃(x_i,X,x_R)=0` per base x-coord (Tonelli–Shanks) — O(\|F\|)/target | `validate.py`: independent O(\|F\|²) brute-force EC enum → identical set, spurious=0, PASS | same relation set as P0 obtained by *solving* not enumerating; GLV = constant ~3× storage. |
| **m=3** `p1_petit_m3/` | m=3 | distinct-index 3-term relation **solving** | SOLVE `S₄=Res_Y(S₃(x_i,x_j,Y),S₃(X,x_R,Y))=0` (deg ≤4 in `X`) per unordered distinct base pair — O(\|F\|²·deg4)/target | `validate.py`: O(\|F\|³) brute-force enumeration independent of `S₄`, but sharing `confirm_relation3` → identical distinct-index set, spurious=0, PASS | Agreement on tested instances; repeated indices excluded; not a separate EC oracle. |
| **P3** `p3_sm_system/` | m=2,3 | explicit finite-set system `{Sₘ₊₁=0, f_F(Xᵢ)=0}`, `f_F=∏(X-a)` | SymPy lex Gröbner solve plus a custom graded Macaulay proxy; plain vs coupled `U=X³` | independent brute-force EC replay → identical tested relation set, spurious=0, PASS | proxy returned `2\|F\|+1` for tested m=2 sizes; stopping rule lacks external GB/theorem validation. The tested auxiliary-variable GLV presentation was slower; no general no-go. |
| **P4** `p4_petit/` | m=2, \|F\|=4 | one composed-polynomial-map presentation | six-variable toy system measured with P3's proxy | independent factor-base rebuild + brute-force EC replay → identical tested relation set, spurious=0, PASS | proxy 7 vs 9, but much larger/slower matrices for this presentation. Not faithful Petit and not a general composed-map result. |

**What the line establishes (measured):** the tested toy formulations give reproducible partial
negatives, and their relation sets replay against EC arithmetic in the stated scopes.

**What the line does NOT establish (open):** an exact/general degree-of-regularity law, an optimal
prime-field factor-base encoding, a nonredundant invariant-coordinate formulation, faithful Petit,
`m ≥ 3` full solving degree, `m ≥ 4` systems, or non-toy primes. None draws an
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
