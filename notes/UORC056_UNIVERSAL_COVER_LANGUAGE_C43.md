# UORC-056 C43: universal-cover and gauge-language atlas

Date: 2026-08-17

Status: seven filtered hypotheses resolved within explicit scopes. The package introduces one exact unifying normal form, one gauge-aware search language, four broad no-go boundaries, one exact symbolic recoding, and an arithmetic correction to inherited secp256k1 claims. No cheap parity decoder, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. Central target

Let

\[
H=\langle G\rangle\cong \mathbf Z/n\mathbf Z,
\qquad n\text{ odd},
\qquad Q=[k]G,
\qquad 1\le k<n.
\]

The target remains

\[
\sigma_G(Q)=(-1)^k.
\]

Previous packages established exact oriented-root, Miller-state, spectral-root, norm, resultant and gauge formulations. C42 localizes a target-dependent resultant back to the original missing marked branch

\[
Y_G(x(Q))/y(Q).
\]

C43 asks a more basic question:

```text
What mathematical object is parity before it is written as a field formula?
```

The answer is a character on a covering group composed with a non-homomorphic section. This identifies the common obstruction behind carry bits, oriented roots, spectral square-root branches, transfer gauges and long-division phase.

This is a new unifying language for this repository. It is not a claim that universal covers, group cohomology, symbolic dynamics, p-adic logarithms, tropical functions or trace sheaves are new mathematics in general.

## 2. Arithmetic audit before the new search

Two inherited draft branches used the claim

\[
\operatorname{ord}_n(2)=\frac{n-1}{2}
\]

for the secp256k1 subgroup order. Exact modular arithmetic rejects it.

For

\[
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337,
\]

C43 verifies the complete factorization

\[
n-1=
2^6\cdot3\cdot149\cdot631\cdot107361793816595537
\cdot174723607534414371449
\cdot341948486974166000522343609283189
\]

and proves by prime-divisor minimality checks that

\[
\boxed{
\operatorname{ord}_n(2)=\frac{n-1}{64}.
}
\]

This order is odd. Therefore \(-1\notin\langle2\rangle\), and the induced doubling action on

\[
(\mathbf Z/n\mathbf Z)^*/\{\pm1\}
\]

has the same order. Since the pair quotient has \((n-1)/2\) elements, it decomposes into

\[
\boxed{32\text{ doubling cycles},}
\]

not one transitive cycle.

The field-modulus claim is also corrected. For the secp256k1 base prime

\[
p=
115792089237316195423570985008687907853269984665640564039457584007908834671663,
\]

C43 verifies

\[
\boxed{
\operatorname{ord}_p(2)=\frac{p-1}{14}.
}
\]

Consequences:

1. the secp-specific transitivity and forced-rank conclusions in the affected draft packages are not valid;
2. the general componentwise gauge theorem does not depend on transitivity and remains a valid abstract obstruction;
3. all successor work must use the 32-cycle action certificate.

## 3. Broad language atlas and filtering

The search considered the following families of representations:

| Cluster | Languages considered | Decision before deep testing |
|---|---|---|
| Existing algebraic line | rational functions, division polynomials, elliptic nets, Miller functions, theta/Kummer, GLV norms, resultants | already substantially covered by C1-C42 |
| Cover and topology | universal cover, sections, central extensions, spin/metaplectic lifts, group cohomology, sheaf descent | select H1-H2 |
| Dynamics and computation | binary long division, automata, symbolic dynamics, kneading words, substitution systems | select H3 |
| Nonarchimedean | formal groups, p-adic logarithms, Coleman-style lifts, elliptic polylogarithms, syntomic regulators | select H4, retain only nonhomomorphic polylogarithmic subroute |
| Tropical | cyclic skeletons, tropical rational functions, chip firing, breakpoint complexity | select H5 |
| Arithmetic harmonic analysis | character sheaves, l-adic trace functions, arithmetic Fourier transforms | select H6 |
| Operator and categorical | transfer matrices, Pfaffians, determinants, spectral flow, tensor networks, open Wilson lines | absorb into H7 gauge typing |
| Meta-search | universal description search, MDL, typed symbolic synthesis, ML ranking | replace untyped enumeration by H7 gauge-aware AST types |
| Out of scope | quantum phase estimation and Shor-type algorithms | outside the classical target and cost model |

Selection criteria were:

1. the language must not be only a renaming of a class already closed;
2. it must expose a transformation law invisible in ordinary coordinates;
3. it must admit an exact theorem or finite replay;
4. preprocessing, advice and representation cost remain charged;
5. a negative result must name the surviving class instead of claiming an unrestricted impossibility.

## 4. H1: universal-cover section

### 4.1 Exact sequence

Write the subgroup abstractly as

\[
0\longrightarrow n\mathbf Z
\longrightarrow \mathbf Z
\stackrel{\pi}{\longrightarrow}
\mathbf Z/n\mathbf Z
\longrightarrow0.
\]

On the cover \(\mathbf Z\), define the genuine character

\[
\chi(z)=(-1)^z.
\]

Because \(n\) is odd,

\[
\chi(n)=-1.
\]

Hence \(\chi\) is nontrivial on the kernel of \(\pi\) and cannot descend to a character of \(H\).

Choose the canonical set-theoretic section

\[
s:\mathbf Z/n\mathbf Z\to\{0,1,\ldots,n-1\}\subset\mathbf Z.
\]

Then parity is exactly

\[
\boxed{
\sigma(a)=\chi(s(a)).
}
\]

This is the first central normal form of C43.

### 4.2 Carry as the section defect

Define

\[
c(a,b)=\frac{s(a)+s(b)-s(a+b)}{n}\in\{0,1\}.
\]

Then

\[
\boxed{
\sigma(a+b)=\sigma(a)\sigma(b)(-1)^{c(a,b)}.
}
\]

Thus the addition carry from C33 is not an unrelated bit. It is exactly the defect of the canonical section from being a homomorphism.

Associativity gives the integer cocycle identity

\[
c(a,b)+c(a+b,d)=c(b,d)+c(a,b+d).
\]

### 4.3 Section gauge

Every set-theoretic section has the form

\[
s_t(a)=s(a)+nt(a)
\]

for an arbitrary integer-valued function \(t\). Therefore

\[
\chi(s_t(a))=(-1)^{t(a)}\chi(s(a)).
\]

This is exactly a componentwise sign gauge. The C39-C40 root transformation

\[
R_i\mapsto s_iR_i
\]

is the finite-algebra incarnation of changing the covering section.

### Decision

```text
Exact new normal form: found.
Cheap evaluation of the canonical section from Q: not found.
```

The problem is no longer best stated as "find a formula for parity." It is:

\[
\boxed{
\text{evaluate the canonical section phase without reconstructing the lift.}
}
\]

## 5. H2: mu_2 cohomology, spin and metaplectic lifts

A natural hope is that parity is an intrinsic spin bit or a nontrivial double cover of the odd cyclic subgroup.

For trivial action on \(\mu_2=\{\pm1\}\),

\[
H^1(C_n,\mu_2)=\operatorname{Hom}(C_n,\mu_2)=0
\]

because a homomorphism image \(u\in\mu_2\) must satisfy \(u^n=1\), and odd \(n\) forces \(u=1\).

For central extensions, choose a lift \(x\) of a generator. Its only scalar relation is

\[
x^n=\alpha,
\qquad \alpha\in\mu_2.
\]

If \(\alpha=-1\), replace \(x\) by \(-x\). Since \(n\) is odd,

\[
(-x)^n=-x^n=1.
\]

Hence every such extension splits and

\[
H^2(C_n,\mu_2)=0.
\]

The signed carry is explicitly

\[
(-1)^{c(a,b)}
=
\sigma(a)\sigma(b)\sigma(a+b),
\]

so it is a coboundary, not a nontrivial topological class.

### Decision

```text
Intrinsic mu_2 character: impossible.
Nontrivial central spin/metaplectic double cover: impossible.
Carry cocycle as a protected cohomology class: false.
```

Any successful construction must use extra ordered, analytic, generator-marked or section data. Pure group topology cannot supply the bit.

## 6. H3: doubling symbolic dynamics

Let

\[
r_j=s(2^jk)\in\{0,\ldots,n-1\}
\]

and define the upper-half carry

\[
d_j=\left\lfloor\frac{2r_j}{n}\right\rfloor\in\{0,1\}.
\]

Then

\[
r_{j+1}=2r_j-nd_j.
\]

Modulo two, oddness of \(n\) gives

\[
\boxed{r_{j+1}\bmod2=d_j.}
\]

Equivalently,

\[
\boxed{
\sigma(2^{j+1}k)=(-1)^{d_j}.
}
\]

The same carry is the next binary digit of \(k/n\):

\[
\boxed{d_j=
\left\lfloor\frac{2^{j+1}k}{n}\right\rfloor
-2\left\lfloor\frac{2^jk}{n}\right\rfloor.}
\]

Therefore the parity sequence along the public doubling orbit is exactly the binary long-division word of \(k/n\).

This is a positive exact recoding, but not a decoder. Computing \(d_j\) from the point \([2^jk]G\) is precisely the hidden upper-half branch.

The replay verifies 102,600 symbolic-dynamics identities across twelve odd prime orders. The frozen pair actions are not uniform:

| order | pair cycles under doubling |
|---:|---:|
| 31 | 3 |
| 79 | 1 |
| 67 | 1 |
| 127 | 9 |
| 139 | 1 |
| held-out 61 | 1 |
| secp256k1 | 32 |

### Decision

```text
Exact automaton language: found.
New observable exposed: hidden upper-half digit.
Coordinate-level shortcut: not found.
```

## 7. H4: p-adic logarithmic lift

Let \(A\) be a torsion-free additive group, for example the additive group of a characteristic-zero p-adic field. Any homomorphism

\[
\ell:C_n\to A
\]

is zero, because for a generator \(g\)

\[
n\ell(g)=\ell(ng)=0
\]

and torsion-freeness forces \(\ell(g)=0\).

Consequently an ordinary additive elliptic logarithm cannot retain a nonzero phase on finite prime-to-p torsion. In the formal group, multiplication by \(n\) is locally invertible when \(p\nmid n\), so there is no nonzero prime-to-p formal torsion to log.

A nonzero analytic coordinate can appear only after choosing a lift modulo a period lattice. That choice is again a section of a covering object and therefore reintroduces H1.

This does not close all p-adic objects. The p-adic elliptic polylogarithm and Eisenstein-Kronecker specializations at prime-to-p torsion points are nonhomomorphic higher objects. They remain admissible only if a generator-marked specialization can be evaluated uniformly and shown to carry the required endpoint gauge charge without materializing an order-n table or period lift.

### Decision

```text
Ordinary p-adic/formal logarithm: closed.
Canonical logarithmic parity phase: impossible.
Nonhomomorphic marked polylogarithm/regulator: retained as a narrow future class.
```

## 8. H5: tropical cyclic skeleton

Place the canonical residues in cyclic order and sample a continuous piecewise-linear function \(f\) whose threshold sign is required to equal

\[
\sigma(k)=(-1)^k.
\]

For odd \(n\), adjacent signs differ on exactly \(n-1\) of the \(n\) cyclic arcs. The intermediate value theorem forces a distinct zero crossing on every sign-changing arc.

A nonzero affine segment has at most one zero. Therefore any exact thresholded PL decoder needs at least

\[
\boxed{n-1}
\]

zero-crossing affine segments.

The bound is independent of how the cyclic skeleton is embedded. A tropical coordinate change can move the bends but cannot remove the alternation count.

### Decision

```text
Sublinear-segment tropical decoder: impossible.
Exact tropical representation size: Omega(n).
```

This does not exclude a nonlocal tropical object whose evaluation avoids explicit segment representation. Such an object would need an additional compressed circuit model and must still pass the gauge type test in H7.

## 9. H6: l-adic trace functions and arithmetic Fourier transforms

Let

\[
\zeta=e^{2\pi i/n}
\]

and extend parity by omitting the identity. For a character frequency \(r\), define

\[
S_r=\sum_{k=1}^{n-1}(-1)^k\zeta^{-rk}.
\]

A geometric-series calculation gives

\[
\boxed{
S_r=\frac{1-\zeta^{-r}}{1+\zeta^{-r}}.
}
\]

At \(r=(n-1)/2\),

\[
\boxed{
|S_r|=\cot\left(\frac{\pi}{2n}\right).
}
\]

Now consider any candidate class with a verified character-twist estimate

\[
\left|\sum_{P\in E(\mathbf F_p)}t(P)\rho(P)\right|
\le B\sqrt p
\]

for all group characters \(\rho\). If \(t([k]G)=(-1)^k\) on nonzero points and \(|t(O)|\le R\), then the triangle inequality forces

\[
\boxed{
B\ge
\frac{\cot(\pi/(2n))-R}{\sqrt p}.
}
\]

For secp256k1 and \(R=1\), the exact replay obtains

\[
\log_2 B\ge127.3485038705\ldots
\]

Thus any sheaf/trace-function family whose square-root twist constant remains bounded or polylogarithmic cannot equal parity. Its effective complexity must grow on the order of \(\sqrt n\).

This is a transfer theorem, not an unrestricted theorem about every l-adic complex. It applies once the proposed class supplies the stated uniform twist bound with a charged complexity parameter. The arithmetic Fourier-transform framework on connected commutative algebraic groups gives the correct ambient language for such tests.

### Decision

```text
Bounded-complexity trace-function decoder: closed under the stated twist bound.
Required secp twist constant: greater than 2^127.3485.
Unbounded/high-complexity sheaf: not excluded, but its cost must be charged.
```

## 10. H7: gauge-typed universal description language

The largest practical result of C43 is a new static type system for the search engine.

Let each component root \(R_i\) transform under an independent vertex sign

\[
R_i\mapsto s_iR_i.
\]

Assign it the gauge charge

\[
\operatorname{chg}(R_i)=e_i
\in(\mathbf Z/2\mathbf Z)^r.
\]

The type rules are:

\[
\operatorname{chg}(AB)=
\operatorname{chg}(A)+\operatorname{chg}(B),
\]

\[
\operatorname{chg}(A^2)=0,
\]

\[
A+B\text{ is well typed only if }
\operatorname{chg}(A)=\operatorname{chg}(B).
\]

For an oriented transfer

\[
T_{ij}=R_j/R_i,
\]

\[
\operatorname{chg}(T_{ij})=e_i+e_j.
\]

Therefore:

- root squares are neutral;
- transfer squares are neutral;
- norms and symmetric orbit products are neutral;
- determinants and Pfaffians built from neutral entries are neutral;
- every closed loop telescopes to zero charge;
- an open path from anchor \(a\) to query \(q\) has charge \(e_a+e_q\).

With the anchor fixed, the target parity orientation has query charge \(e_q\). Hence a grammar containing only public neutral atoms can be rejected without evaluation:

\[
\boxed{
\text{neutral inputs cannot synthesize a charged parity output.}
}
\]

The only surviving local type is

\[
\boxed{
\text{an unsquared anchor-to-query open transport.}
}
\]

An open Wilson line, relative torsion, endpoint Pfaffian or transfer matrix is not a new mechanism unless it supplies a public numerical rule for this charged transport. Naming a charged object is useful because it narrows the target, but evaluating it from squared edge data remains equivalent to choosing the missing branch.

### Decision

```text
Gauge-aware AST type system: found and implemented.
Automatic rejection of neutral grammars: exact.
Surviving type: open endpoint-charged transport.
Numerical charged transport law: not found.
```

This type system should precede symbolic-family algebra and universal description search. It prevents the engine from spending compute on candidates that are structurally unable to transform like parity.

## 11. Consolidated result

| ID | New language | Outcome |
|---|---|---|
| H1 | universal cover plus canonical section | exact positive normal form |
| H2 | mu_2 cohomology/spin/metaplectic lift | closed for odd cyclic groups |
| H3 | symbolic doubling dynamics | exact binary-word recoding, no shortcut |
| H4 | p-adic logarithmic lift | ordinary log closed; marked polylog remains |
| H5 | tropical cyclic skeleton | Omega(n) PL representation boundary |
| H6 | l-adic trace functions | bounded-complexity class closed under twist bound |
| H7 | gauge-typed AST/open transport | exact static filter; one surviving charged type |

The central synthesis is

\[
\boxed{
\text{parity is not an intrinsic function of the odd cyclic group;}\\
\text{it is the phase of a chosen section of a cover.}
}
\]

The computational problem is therefore

\[
\boxed{
\text{find a uniformly evaluable, generator-marked, endpoint-charged observable}
}
\]

rather than another gauge-neutral formula.

## 12. Exact replay

The deterministic Python replay verifies:

```text
7 resolved hypotheses
12 diagnostic odd prime orders
51,876 universal-cover addition identities
5,800,344 carry cocycle identities
102,600 symbolic-doubling identities
exact secp n-1 and p-1 factorizations
ord_n(2)=(n-1)/64
ord_p(2)=(p-1)/14
32 secp pair-quotient doubling cycles
exact nonzero-parity Fourier peak on all diagnostic orders
secp trace-bound exponent 127.3485038705...
gauge-charge telescoping for squares, loops and open paths
0 arithmetic errors
```

The replay uses only public constants and synthetic cyclic groups. It accepts no external point, wallet, key or unknown production scalar.

## 13. Successor problem

The next admissible package should not begin with another neutral formula. It should target one of two charged mechanisms:

### C44-A: marked p-adic polylogarithmic transport

Construct a low-level specialization at \((G,Q)\) whose transformation under section gauge is the endpoint charge \(e_G+e_Q\). Reject it immediately if it factors through an ordinary logarithm, a symmetric norm, an uncharged torsion specialization or an order-n table.

### C44-B: local GLV open transport

Search for a public unsquared relation among

\[
R(Q),\quad R(\phi Q),\quad R(\phi^2Q)
\]

whose type is not neutral and whose evaluation does not require choosing the three roots independently. The type checker must run before numerical screening.

The stronger priority is C44-B because it is closest to the surviving local structure of C42 while respecting the corrected 32-cycle secp action.

## 14. Claim boundary

C43 does not claim:

1. a parity oracle;
2. a sub-square-root ECDLP algorithm;
3. an unrestricted lower bound for all p-adic, tropical or l-adic constructions;
4. that the underlying mathematical theories are novel;
5. that every charged object is efficiently evaluable;
6. a Lean-kernel proof of all seven packages in this first replay.

It gives exact elementary proofs, deterministic finite replay, a corrected secp action certificate, a broad transfer-function boundary and a new gauge-aware candidate language.

## 15. Literature anchors

- Forey, Fresan and Kowalski, *Arithmetic Fourier transforms over finite fields: generic vanishing, convolution, and equidistribution*, arXiv:2109.11961, version 6.
- Bannai, Kobayashi and Tsuji, *On the de Rham and p-adic realizations of the Elliptic Polylogarithm for CM elliptic curves*, arXiv:0711.1701.
- The Stacks Project, Stein factorization and proper/affine morphism results, used only for the scoped observation that a globally regular matrix-valued representation of a proper connected elliptic curve in an affine algebraic group is constant.
