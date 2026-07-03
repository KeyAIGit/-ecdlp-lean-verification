# Complex multiplication by the Eisenstein integers — the theory behind the GLV endomorphism

This is the mathematical companion to the machine-checked GLV endomorphism object in
`Ecdlp/Proved/Glv*.lean`. It is a self-contained, **purely mathematical** exposition of why a
`j = 0` short Weierstrass curve over `𝔽_p` (with `p ≡ 1 mod 3`) — of which secp256k1 is one —
carries an order-3 automorphism `φ : (x,y) ↦ (β·x, y)` satisfying `φ² + φ + 1 = 0`, and hence
has complex multiplication by `ℤ[ω]`. Everything below is standard theory (Silverman III–V);
the value the repo adds is that the concrete instance is checked by the Lean kernel.

## Formalization status — each claim ↔ its verified theorem

| Statement in the note | Machine-checked theorem (`Ecdlp.Curve.…`) | file |
|---|---|---|
| `φ` maps `E → E`, is bijective | `secp256k1_glv_preserves_equation`, `glvPoint_bijective` | `GlvEndomorphism`, `GlvAutomorphism` |
| `φ` is an additive homomorphism | `glvPoint_add`, `glvHom` | `GlvHom`, `GlvMonoidHom` |
| `φ³ = id` | `glvPoint_cube_eq_id` | `GlvAutomorphism` |
| `φ² + φ + 1 = 0` in `End(E)` | `secp256k1_glv_cube_relation`, `glvHom_minpoly` | `GlvCubeRelation`, `GlvMinPoly` |
| `φ ≠ id` ⇒ order **exactly** 3 (primitive) | `secp256k1_glvHom_ne_id` | `GlvOrderThree` |
| fixed locus: `φ(P)=P ⟺ x_P = 0` | `secp256k1_glvPoint_fixed_iff` | `GlvFixedLocus` |
| orbit sum `P + φP + φ²P = O` | `secp256k1_glvPoint_orbit_sum` | `GlvOrderThree` |
| `β² + β + 1 = 0`, `β ≠ 1` in `𝔽_p` | `Secp256k1.beta_field_eigenvalue`, `secp256k1_beta_ne_one` | `Secp256k1Params`, `GlvFixedLocus` |

What is **not** yet formalized (and is honestly out of reach in current Mathlib): the ring
*isomorphism* `End(E) ≅ ℤ[ω]` (only the embedding `ℤ[ω] ↪ End(E)` is within reach, and even
that needs the domain property of `End(E)`), the ordinary/supersingular dichotomy via
Frobenius, and the `φ = [λ]` eigenvalue identity on the torsion. Those depend on the Weil
pairing / point-counting layer that Mathlib does not yet have. See `notes/BARRIERS`-style
tracking and `VERIFIED.md`.

---

## 1. Setting

Let $p$ be a prime with $p \equiv 1 \pmod{3}$; the smallest such prime is $7$, so in particular $p \neq 2, 3$. Fix $b \in \mathbb{F}_p^{\times}$ and consider the short Weierstrass curve

$$E : y^2 = x^3 + b \quad \text{over } \mathbb{F}_p .$$

Its discriminant $\Delta = -432\,b^2$ is nonzero, so $E$ is smooth, and since $c_4 = 0$ its $j$-invariant is $0$. Write $O = [0:1:0]$ for the point at infinity, the identity of the group $E(\mathbb{F}_p)$.

Because $\mathbb{F}_p^{\times}$ is cyclic of order $p-1$ and $3 \mid p-1$, the field $\mathbb{F}_p$ contains an element $\beta$ of multiplicative order exactly $3$, a *primitive cube root of unity*. From the factorization $X^3 - 1 = (X-1)(X^2+X+1)$ and $\beta \neq 1$ we obtain the identity that drives everything below:

$$\beta^2 + \beta + 1 = 0, \qquad \beta^3 = 1 .$$

There are exactly two such elements, $\beta$ and $\beta^2 = \beta^{-1}$; fix one. Define

$$\varphi : E \longrightarrow E, \qquad \varphi(x,y) = (\beta x,\, y), \qquad \varphi(O) = O .$$

## 2. $\varphi$ is an automorphism of the curve

If $(x,y)$ satisfies $y^2 = x^3 + b$, then $(\beta x)^3 = \beta^3 x^3 = x^3$, hence $y^2 = (\beta x)^3 + b$: the image again lies on $E$, so $\varphi$ is well defined. It is bijective, with inverse $(x,y) \mapsto (\beta^2 x, y)$, since $\beta^2 \cdot \beta = 1$. Projectively, $\varphi$ is the restriction to $E$ of the linear automorphism $[X:Y:Z] \mapsto [\beta X : Y : Z]$ of $\mathbb{P}^2$, which fixes $O = [0:1:0]$. Because $\beta \in \mathbb{F}_p$, the map $\varphi$ is defined over $\mathbb{F}_p$ and in particular permutes the rational points $E(\mathbb{F}_p)$.

## 3. $\varphi$ is a group homomorphism

The structural reason is rigidity: **every morphism of elliptic curves that sends the identity to the identity is a group homomorphism** (Silverman, *AEC*, III.4.8). Since $\varphi$ is a morphism of $E$ to itself with $\varphi(O) = O$, it is an endomorphism of the group $E$, and being invertible it lies in $\mathrm{Aut}(E)$. $\varphi$ is thus a special case of the general fact that algebraic-group endomorphisms are exactly the variety morphisms fixing the identity.

One can also see this concretely through the chord–tangent law, for which the governing principle is: $P + Q + R = O$ if and only if $P, Q, R$ are the three intersection points of $E$ with a line, counted with multiplicity. The projective-linear map $[X:Y:Z] \mapsto [\beta X:Y:Z]$ carries lines to lines, preserves intersection multiplicities, maps $E$ to $E$, and fixes $O$. Hence collinear triples on $E$ go to collinear triples, so $P+Q+R = O$ implies $\varphi(P)+\varphi(Q)+\varphi(R) = O$. Since also $\varphi(-P) = -\varphi(P)$ (negation is $(x,y) \mapsto (x,-y)$, which visibly commutes with $\varphi$), applying the collinearity relation to $P$, $Q$, $-(P+Q)$ yields $\varphi(P+Q) = \varphi(P) + \varphi(Q)$.

## 4. The minimal polynomial: $\varphi^2 + \varphi + 1 = 0$

Composition gives $\varphi^2(x,y) = (\beta^2 x, y)$ and $\varphi^3(x,y) = (\beta^3 x, y) = (x,y)$, so $\varphi^3 = \mathrm{id}$. Moreover $\varphi \neq \mathrm{id}$: as morphisms, $\varphi = \mathrm{id}$ would force $\beta x = x$ identically on $E$, i.e. $(\beta - 1)x = 0$ as a function on $E$, which is impossible since $\beta \neq 1$ and $x$ is nonconstant. (Concretely, $\varphi$ moves every point of $E(\overline{\mathbb{F}}_p)$ with $x \neq 0$, and all but at most three points have $x \neq 0$.) The same argument with $\beta^2 \neq 1$ shows $\varphi^2 \neq \mathrm{id}$. Hence $\varphi$ has order exactly $3$ in $\mathrm{Aut}(E)$.

Now work in the endomorphism ring $\mathrm{End}(E)$, where addition is pointwise ($(\psi + \chi)(P) = \psi(P) + \chi(P)$) and multiplication is composition. This ring has no zero divisors: a nonzero isogeny is surjective on $\overline{\mathbb{F}}_p$-points, so if $\psi \circ \chi = 0$ with $\chi \neq 0$, then $\psi$ vanishes on all of $E$, i.e. $\psi = 0$. In $\mathrm{End}(E)$,

$$(\varphi - 1)(\varphi^2 + \varphi + 1) = \varphi^3 - 1 = 0,$$

and $\varphi - 1 \neq 0$ because $(\varphi - 1)(P) = \varphi(P) - P \neq O$ for any point with $x \neq 0$. Since $\mathrm{End}(E)$ is a domain,

$$\varphi^2 + \varphi + 1 = 0 \quad \text{in } \mathrm{End}(E).$$

This is the minimal polynomial: $X^2 + X + 1 = \Phi_3(X)$ is irreducible over $\mathbb{Q}$, and $\varphi$ satisfies no degree-one relation, for if $\varphi$ were a rational multiple $r \cdot \mathrm{id}$ then $\varphi^3 = \mathrm{id}$ would give $r^3 = 1$, so $r = 1$ and $\varphi = \mathrm{id}$, a contradiction. Thus $\varphi$ is a *primitive* cube root of unity in $\mathrm{End}(E)$.

## 5. Ordinarity and complex multiplication by $\mathbb{Z}[\omega]$

Let $\omega = e^{2\pi i/3} = \tfrac{-1+\sqrt{-3}}{2}$, whose minimal polynomial over $\mathbb{Q}$ is likewise $X^2 + X + 1$, and let $\mathbb{Z}[\omega] \cong \mathbb{Z}[X]/(X^2+X+1)$ be the ring of Eisenstein integers. By the relation just proved, $X \mapsto \varphi$ induces a ring homomorphism $\iota : \mathbb{Z}[\omega] \to \mathrm{End}(E)$ with $\iota(\omega) = \varphi$. It is injective: its kernel is an ideal $I \subseteq \mathbb{Z}[\omega]$, and any nonzero $z \in I$ would put the positive integer $N(z) = z\bar{z} \in I$, forcing the multiplication-by-$N(z)$ map to vanish on $E$; but $[n] \neq 0$ for every $n \neq 0$, since $\deg[n] = n^2 > 0$. Hence

$$\mathbb{Z}[\omega] \;\cong\; \mathbb{Z}[\varphi] \;\hookrightarrow\; \mathrm{End}(E):$$

the curve has **complex multiplication by the Eisenstein integers**, with $\varphi$ playing the role of $\omega$.

The hypothesis $p \equiv 1 \pmod 3$ also rules out the supersingular case. Indeed, $\varphi$ is defined over $\mathbb{F}_p$, so it commutes with the $p$-power Frobenius $\pi$. If $E$ were supersingular, then (Waterhouse) $\pi^2 = -p$ and the $\mathbb{F}_p$-rational endomorphism algebra would be the imaginary quadratic field $\mathbb{Q}(\pi) = \mathbb{Q}(\sqrt{-p})$, which cannot contain the field $\mathbb{Q}(\varphi) \cong \mathbb{Q}(\sqrt{-3})$ when $p \neq 3$. So $E$ is ordinary — this recovers, for our situation, Deuring's classical criterion that a $j = 0$ curve over $\mathbb{F}_p$ ($p > 3$) is supersingular exactly when $p \equiv 2 \pmod 3$. For an ordinary curve, $\mathrm{End}(E)$ is an order in an imaginary quadratic field; since it contains $\mathbb{Z}[\omega]$, the *maximal* order of $\mathbb{Q}(\sqrt{-3})$, we conclude $\mathrm{End}(E) \cong \mathbb{Z}[\omega]$ exactly. Consistently, $\mathrm{Aut}(E) \cong \mathbb{Z}[\omega]^{\times} = \{\pm 1, \pm\omega, \pm\omega^2\}$, the cyclic group of order $6$ attached to $j = 0$.

## 6. The pointwise trace-zero identity

Because addition in $\mathrm{End}(E)$ is pointwise, evaluating the operator identity $\varphi^2 + \varphi + \mathrm{id} = 0$ at any $P \in E(\overline{\mathbb{F}}_p)$ — in particular at any rational point — gives

$$P + \varphi(P) + \varphi^2(P) = O .$$

Geometrically this is transparent. For $P = (x_0, y_0)$, the three points $P$, $\varphi(P) = (\beta x_0, y_0)$, $\varphi^2(P) = (\beta^2 x_0, y_0)$ share their $y$-coordinate, so they lie on the horizontal line $Y = y_0$. That line meets $E$ where $X^3 = y_0^2 - b$, and using $\beta^2 + \beta + 1 = 0$ one checks

$$(X - x_0)(X - \beta x_0)(X - \beta^2 x_0) = X^3 - x_0^3,$$

so the three intersection points of the line with $E$ (with multiplicity) are exactly the $\langle\varphi\rangle$-orbit of $P$. Three collinear points sum to $O$. Thus every orbit of the order-$3$ automorphism sums to the identity. The degenerate orbits — the fixed points $O$ and $(0, \pm\sqrt{b})$, the latter rational only when $b$ is a square — satisfy $3P = O$; they constitute $\ker(\varphi - 1)$, a group of order $3 = N_{\mathbb{Q}(\omega)/\mathbb{Q}}(\omega - 1) = \deg(\varphi - 1)$.

## Remark — the two faces of $X^2 + X + 1 = 0$

The operator identity $\varphi^2 + \varphi + 1 = 0$ in $\mathrm{End}(E)$ and the field identity $\beta^2 + \beta + 1 = 0$ in $\mathbb{F}_p$ are two appearances of the same equation. In one direction, $\varphi$ acts on the invariant differential by $\varphi^{*}\!\left(\tfrac{dx}{2y}\right) = \beta\,\tfrac{dx}{2y}$, and the action on the cotangent space at $O$ is a ring homomorphism $\mathrm{End}(E) \to \mathbb{F}_p$ carrying $\varphi \mapsto \beta$; under it the endomorphism relation maps precisely onto the scalar relation. In the other direction, $\beta^2 + \beta + 1 = 0$ says that $x_0 + \beta x_0 + \beta^2 x_0 = 0$, i.e. that the cubic $X^3 - x_0^3$ has vanishing $X^2$-coefficient; by Vieta this is exactly the collinearity of the orbit $\{P, \varphi(P), \varphi^2(P)\}$, which is the geometric content of $P + \varphi(P) + \varphi^2(P) = O$. The abstract relation in $\mathrm{End}(E)$ is thus the faithful lift, through the group law, of an elementary identity among cube roots of unity in $\mathbb{F}_p$.

---

### References
1. J. H. Silverman, *The Arithmetic of Elliptic Curves*, 2nd ed., Springer GTM 106 — III.4 (endomorphism rings, rigidity), III.5 (invariant differential), V.3–V.4 (ordinary vs. supersingular).
2. D. A. Cox, *Primes of the Form $x^2 + ny^2$*, Wiley — complex multiplication and orders in imaginary quadratic fields.
3. W. C. Waterhouse, *Abelian varieties over finite fields*, Ann. Sci. É.N.S. (4) 2 (1969) — endomorphism algebras over prime fields.

---
*Provenance: the mathematical exposition (§1–6, Remark) was drafted by an AI model (Claude
Fable 5) as pure algebraic-geometry background, then adapted here; the "Formalization status"
table and framing map it to the repository's kernel-checked theorems. The exposition is
context, not a proof — only the Lean theorems in the table are machine-verified.*
