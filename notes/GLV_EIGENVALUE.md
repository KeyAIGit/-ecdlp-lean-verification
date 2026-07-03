# The GLV eigenvalue property as a conditional theorem

Companion to the machine-checked node `Ecdlp.Curve.secp256k1_glvHom_eq_zsmul`
(`Ecdlp/Proved/GlvEigenvalue.lean`). It explains *why* the geometric GLV endomorphism
`φ = glvHom` acts on the rational points as multiplication by a scalar `[k]` (the eigenvalue
the practical GLV method calls `λ`), and — precisely — which single ingredient is deep and
which is elementary.

## Formalization status — claim ↔ verified theorem

| Statement in the note | Machine-checked (`Ecdlp.Curve.…`) |
|---|---|
| endomorphism of a cyclic group is a scalar `[k]` (Lemma 1) | inlined in `secp256k1_glvHom_eq_zsmul` via Mathlib `IsAddCyclic.exists_generator` + `map_cyclic` |
| `φ` acts as `[k]` on `E(𝔽_p)` (Prop 2) | `secp256k1_glvHom_eq_zsmul` (part 1: `∀ P, glvHom P = k • P`) |
| `k²+k+1 ≡ 0` on the group (Prop 3) | `secp256k1_glvHom_eq_zsmul` (part 2: `∀ P, (k²+k+1) • P = 0`) |
| `φ² + φ + 1 = 0` in `End(E)` | `glvHom_minpoly` (`GlvMinPoly.lean`) |
| `λ² + λ + 1 ≡ 0 (mod n)` (arithmetic) | `Secp256k1.glv_lambda_eigenvalue` (`CubeRoot.lean`) |

**The deliberately unproved hypothesis** is `[IsAddCyclic secp256k1.toAffine.Point]`: that
`E(𝔽_p)` is cyclic. Establishing it requires `#E(𝔽_p) = n` — point-counting (Hasse / Frobenius
trace), absent from Mathlib for a 256-bit curve. So the verified theorem is a **reduction**: it
discharges the entire GLV eigenvalue property *elementarily, modulo cyclicity*, and names that
one input as the remaining barrier. The exposition below (drafted by Claude Fable 5 as pure
group theory) is the mathematical account of that reduction; only the theorem in the table is
kernel-verified.

---

## When an order-3 automorphism acts as a scalar on a cyclic group of rational points

**Setup.** Let $E/\mathbb{F}_p$ be an elliptic curve equipped with an automorphism $\varphi$ of order exactly $3$ fixing the identity and satisfying the relation
$$\varphi^2 + \varphi + 1 = 0 \quad \text{in } \operatorname{End}(E),$$
so that $\varphi$ is a primitive cube root of unity in the endomorphism ring. Assume throughout that the group of rational points $G = E(\mathbb{F}_p)$ is finite **cyclic** of order $N$. Since $\varphi$ is defined over $\mathbb{F}_p$, it commutes with the Galois action and hence restricts to a group endomorphism $\varphi|_G : G \to G$. We write the group law on $G$ additively, with $k \cdot x$ denoting $x$ added to itself $k$ times.

## 1. Endomorphisms of a finite cyclic group are scalars

**Lemma 1.** Let $G = \langle g \rangle$ be a cyclic group of order $N$, and let $f : G \to G$ be a group homomorphism. Then there exists an integer $k$, well defined modulo $N$, such that $f(x) = k \cdot x$ for all $x \in G$.

*Proof.* Since $f(g) \in G = \langle g \rangle$, there is an integer $k$ with $f(g) = k \cdot g$; the integer $k$ is determined exactly up to multiples of $N$, since $a \cdot g = b \cdot g \iff a \equiv b \pmod N$. An arbitrary element of $G$ has the form $x = m \cdot g$ for some $m \in \mathbb{Z}$, and additivity of $f$ gives
$$f(m \cdot g) = m \cdot f(g) = m \cdot (k \cdot g) = k \cdot (m \cdot g),$$
using commutativity of integer scalars on an abelian group. Hence $f(x) = k \cdot x$ for all $x \in G$. $\blacksquare$

**Remark.** The map $\mathbb{Z}/N \to \operatorname{End}(G)$, $k \mapsto [k]$, is a ring homomorphism; Lemma 1 says it is surjective, and injectivity follows by evaluating at the generator $g$ (which has exact order $N$). Thus $\operatorname{End}(G) \cong \mathbb{Z}/N$ *as a ring*: composition of endomorphisms corresponds to multiplication of scalars. This isomorphism fails for non-cyclic groups: on $(\mathbb{Z}/\ell)^2$ the endomorphism ring is the full matrix ring $M_2(\mathbb{Z}/\ell)$, and most endomorphisms are not scalars. Cyclicity is doing real work here.

## 2. The automorphism acts as a scalar

**Proposition 2.** Under the standing hypotheses, there exists $k \in \mathbb{Z}/N$ such that
$$\varphi(P) = k \cdot P \qquad \text{for all } P \in E(\mathbb{F}_p).$$

*Proof.* The restriction $\varphi|_G$ is a group homomorphism $G \to G$: it respects the group law because $\varphi \in \operatorname{End}(E)$, it fixes the identity by hypothesis, and it maps rational points to rational points because $\varphi$ is defined over $\mathbb{F}_p$. Apply Lemma 1. $\blacksquare$

## 3. The scalar is a primitive cube root of unity modulo $N$

**Proposition 3.** The scalar $k$ of Proposition 2 satisfies
$$k^2 + k + 1 \equiv 0 \pmod{N}.$$
If moreover $\varphi|_G \neq \mathrm{id}_G$, then $k \not\equiv 1 \pmod N$, and $k$ has multiplicative order exactly $3$ in $(\mathbb{Z}/N)^\times$.

*Proof.* Evaluate the ring relation $\varphi^2 + \varphi + 1 = 0$ at any $P \in G$. Since $\varphi(P) = k\cdot P$ and $\varphi^2(P) = k^2 \cdot P$, we get $(k^2 + k + 1)\cdot P = 0$ for all $P \in G$. Taking $P = g$ a generator, which has exact order $N$, forces $N \mid k^2 + k + 1$.

Multiplying $k^2+k+1 \equiv 0$ by $k-1$ gives $k^3 \equiv 1 \pmod N$, so $k$ is a unit mod $N$ of order dividing $3$. If $k \equiv 1$, then $\varphi(P) = P$ for all $P \in G$, i.e. $\varphi|_G = \mathrm{id}$; excluding this, the order of $k$ is exactly $3$. (Note $k \equiv 1$ together with $k^2+k+1 \equiv 0$ would also force $N \mid 3$, so for $N > 3$ the case $k \equiv 1$ is outright impossible.) $\blacksquare$

**Corollary 4.** If $N$ is prime and $\varphi|_G \neq \mathrm{id}$, then $3 \mid N - 1$, and $X^2 + X + 1$ has exactly two roots in $\mathbb{F}_N$, namely $k$ and $k^2$. These correspond to the two nontrivial powers of the automorphism: $\varphi = [k]$ and $\varphi^2 = [k^2]$ on $G$.

*Proof.* An element of order $3$ exists in $(\mathbb{Z}/N)^\times$, which is cyclic of order $N-1$; hence $3 \mid N-1$. Over the field $\mathbb{F}_N$ the quadratic $X^2+X+1$ has at most two roots; $k$ and $k^2$ are both roots ($k^2$ because $(k^2)^2 + k^2 + 1 = k^4 + k^2 + 1 \equiv k^2 + k + 1 \equiv 0$, using $k^3 \equiv 1$), and they are distinct since $k \not\equiv 1$ has order $3$. $\blacksquare$

## 4. What is elementary and what is not

Propositions 2 and 3 use nothing about elliptic curves beyond three formal facts: $\varphi$ restricts to an endomorphism of $G$, the relation $\varphi^2+\varphi+1=0$ holds, and — crucially — $G$ is cyclic of order $N$. Given those inputs, everything above is finite group theory of the most elementary kind.

The genuinely hard ingredient is the input itself: determining $\#E(\mathbb{F}_p)$ and verifying that the group is cyclic. That requires point-counting — the Hasse bound $|p + 1 - N| \le 2\sqrt{p}$, the trace of Frobenius, and in practice Schoof-type algorithms or CM theory — none of which is elementary. The eigenvalue statement $\varphi = [k]$ on $E(\mathbb{F}_p)$ is therefore a **conditional theorem**: elementary *modulo* the group structure of $E(\mathbb{F}_p)$. Any formal verification of it splits cleanly along this seam — the group-theoretic layer above is cheap to machine-check, while the cardinality claim must be certified separately. (This is exactly the seam realized in `GlvEigenvalue.lean`: the `[IsAddCyclic]` instance is the assumed input; everything else is proved.)

## 5. The same polynomial at two moduli

When $p \equiv 1 \pmod 3$, an order-3 automorphism of a curve $y^2 = x^3 + b$ is realized on coordinates by $(x, y) \mapsto (\beta x, y)$ where $\beta \in \mathbb{F}_p$ satisfies $\beta^2 + \beta + 1 = 0$ — a congruence **modulo $p$**, living on the coordinate field. The eigenvalue $k$ of Proposition 3 satisfies $k^2 + k + 1 \equiv 0$ **modulo $N$**, living on the group of order $N = \#E(\mathbb{F}_p)$. It is the same cyclotomic polynomial $\Phi_3(X) = X^2 + X + 1$, evaluated at two unrelated moduli: $\beta$ is a cube root of unity in $\mathbb{F}_p^\times$, $k$ a cube root of unity in $(\mathbb{Z}/N)^\times$.

Both record that $\varphi$ generates a copy of $\mathbb{Z}[\zeta_3]$ inside $\operatorname{End}(E)$, whose image in any faithful linear realization — on the tangent space, on coordinates, on the $N$-torsion or the Tate module — must again satisfy $\Phi_3$. But *identifying* the correct correspondence, i.e. which root $\beta$ pairs with which eigenvalue $k$, passes through the action of Frobenius and $\varphi$ on the Tate module. That link is exactly the deep, non-elementary part; everything downstream of it is Lemma 1.

---
*Provenance: the exposition (§1–5) was drafted by an AI model (Claude Fable 5) as pure group
theory, then adapted here; the "Formalization status" table maps it to the repository's
kernel-checked theorem. Only `secp256k1_glvHom_eq_zsmul` (and the lemmas it cites) is
machine-verified — the prose is context, not proof.*
