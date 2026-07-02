# A machine-checked formalization of the secp256k1 GLV endomorphism

**Claim.** This repository contains, to our knowledge, the **first Lean 4 + Mathlib
formalization of the secp256k1 GLV endomorphism as a complex-multiplication automorphism**:
the rational self-map `φ : (x, y) ↦ (β·x, y)` is proved to be a bijective additive
endomorphism of the curve's point group satisfying `φ² + φ + 1 = 0` — a primitive cube
root of unity in `End(E)` of order 3. Every statement below is accepted by the Lean
kernel with **no `sorry` and no custom axioms**; the GLV endomorphism itself is **not
present in Mathlib** (confirmed against the pinned v4.31 source: no GLV/CM-automorphism
construction for a concrete curve).

This note consolidates the object into one citable unit. It is a *formalization* result,
not a cryptanalysis result: it says nothing about the hardness of the ECDLP.

---

## The object

`secp256k1` is the short Weierstrass curve `Y² = X³ + 7` over `𝔽_p`. Because its
`j`-invariant is `0` (`secp256k1_j_eq_zero`), it has complex multiplication by `ℤ[ζ₃]`;
the CM automorphism is realized concretely by scaling the `X`-coordinate by the field
cube-root factor `β ∈ 𝔽_p` (`β³ = 1`, `β² + β + 1 = 0`). We build this map rung by rung
into a first-class object and prove its algebraic structure.

`glvPoint : secp256k1.toAffine.Point → secp256k1.toAffine.Point`
(`Ecdlp/Proved/GlvEndomorphism.lean`).

## The verified ladder

### 1 — Eigenvalue arithmetic (the CM data)
| Statement | Name |
|---|---|
| `β` (in `𝔽_p`) and `λ` (in `ℤ/n`) are the GLV eigenvalue data | `Secp256k1.glv_lambda_eigenvalue` |
| a root of `x²+x+1` is a cube root of unity (ring form) | `Ecdlp.Proved.cube_root_of_eigenvalue` |
| such a root has **order exactly 3** (primitive) | `Ecdlp.Proved.orderOf_eigenvalue_eq_three` |
| `β` has order 3 in `𝔽_p`; `λ` has order 3 in `ℤ/n` | `secp256k1_beta_orderOf`, `secp256k1_lambda_orderOf` |
| `X³ = 1` has exactly 3 roots in `𝔽_p` | `secp256k1_three_cube_roots_of_unity` |
| `secp256k1` has `j = 0` (CM by `ℤ[ζ₃]`) | `secp256k1_j_eq_zero` |

### 2 — The map is well defined on the curve
| Statement | Name |
|---|---|
| `φ` preserves the curve equation `Y²=X³+7` (via `β³=1`) | `secp256k1_glv_preserves_equation` |
| `φ` preserves nonsingularity (`β` a unit) | `secp256k1_glv_preserves_nonsingular` |
| → hence `glvPoint : Point → Point` is defined | `glvPoint` |

### 3 — The map is an additive endomorphism
| Statement | Name |
|---|---|
| GLV scales the addition **slope** by `β²` (all branches) | `secp256k1_glv_slope` (+ secant/tangent lemmas) |
| β-equivariance of `addX` (new `X` scales by `β`) | `secp256k1_glv_addX` |
| β-equivariance of `addY` (`Y` unchanged) | `secp256k1_glv_addY` |
| **`φ(P+Q) = φ(P) + φ(Q)`** (the homomorphism property) | `glvPoint_add` |
| bundled as a Mathlib `AddMonoidHom` `glvHom : Point →+ Point` | `glvHom` |

### 4 — The endomorphism-ring structure (the CM identity)
| Statement | Name |
|---|---|
| **`φ² + φ + 1 = 0`** pointwise (primitive cube root of unity) | `secp256k1_glv_cube_relation` |
| the same as an **operator identity** in `End(E)` | `glvHom_minpoly` |
| **`φ³ = id`** — the CM automorphism has order dividing 3 | `glvPoint_cube_eq_id` |
| **`φ` is bijective** — an automorphism (inverse `φ²`) | `glvPoint_bijective` |
| `φ` preserves the `n`-torsion `E[n]` (restricts to `End(E[n])`) | `secp256k1_glv_preserves_torsion` |

### 5 — Related torsion facts (the `3`-torsion where the CM lives)
| Statement | Name |
|---|---|
| 3-division polynomial `Ψ₃ = 3X⁴ + 84X`, `deg = 4` | `secp256k1_Ψ₃`, `secp256k1_Ψ₃_natDegree` |
| `≤ 4` three-torsion `x`-coordinates (`#E[3] ≤ 9`) | `secp256k1_three_torsion_x_card_le` |

## Scope, stated honestly

**What is proved:** `φ` is a bijective additive automorphism of `E(𝔽_p)` that is a
primitive cube root of unity in `End(E)` — the full CM-automorphism structure, reached
with elementary field algebra and the affine addition formula, needing **no `λ`-scalar and
no point counting**.

**What is *not* proved (the open crown):** that `φ` acts on the base-point subgroup `⟨G⟩`
as scalar multiplication by the GLV eigenvalue `λ`, i.e. `φ(G) = λ • G`. This — the fact
the GLV scalar-decomposition speed-up actually *uses* — is gated on knowing the group
structure `#E(𝔽_p) = n` (a Schoof/Hasse point-counting foundation absent from Mathlib), so
the operator `φ²+φ+1=0` cannot yet be transferred to the scalar identity `λ²+λ+1 ≡ 0
(mod n)` acting on points. See `notes/GLV_LAMBDA.md`. This boundary is a feature of the
honest map, not a gap to paper over.

## Reproduce

```
lake exe cache get && lake build      # builds the whole verified base, incl. all GLV files
lake env lean Ecdlp/AxiomAudit.lean   # confirms: no sorryAx, no custom axioms
```
GLV sources: `Ecdlp/Proved/Glv*.lean` (Endomorphism, Slope, SlopeTangent, SlopeAll,
AddFormula, Hom, MonoidHom, CubeRelation, Torsion, MinPoly, Automorphism).

## Why this is a contribution

- **Novelty:** Mathlib formalizes elliptic curves and their group law generically, but not
  the concrete GLV/CM automorphism of a named curve. This is the object built.
- **Rigor:** kernel-checked, no axioms, reproducible under a pinned toolchain.
- **Substrate value:** it is a self-contained, navigable, verified sub-graph that a future
  automated reasoner can load and build on without re-deriving — exactly the intended use
  of this environment.

Suggested venue for a short paper / tool note: **ITP**, **CPP**, or the **Lean/Mathlib
community** (a `Mathlib` PR upstreaming the reusable `x²+x+1 ⇒ order 3` and CM-automorphism
lemmas would be the highest-impact form).
