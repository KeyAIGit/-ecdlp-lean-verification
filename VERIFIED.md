# Verified claims ledger

Index of machine-checked theorems. Each row maps a knowledge-graph claim to the
Lean theorem that verifies it. `status = proved` means Lean's trusted kernel
accepts the proof with **no `sorry`** (enforced by the CI gate). The
authoritative commit is the latest green `main`; the full operation log lives in
git history and the GitHub Actions tab.

| claim_id | Lean theorem | file | method | status |
|---|---|---|---|---|
| sec2-secp256k1-field-005 | `Secp256k1.p_special_form` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| glv-subgroup-eigenvalue-006 | `Secp256k1.glv_lambda_eigenvalue` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| glv-subgroup-eigenvalue-006 (ZMod form) | `Ecdlp.Targets.glv_eigenvalue_zmod` | Ecdlp/Statements.lean | Mathlib | proved |
| supporting: lambda^3 = 1 mod n | `Secp256k1.lambda_is_cube_root` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: lambda != 1 | `Secp256k1.lambda_ne_one` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta^2+beta+1 = 0 mod p | `Secp256k1.beta_field_eigenvalue` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta^3 = 1 mod p | `Secp256k1.beta_is_cube_root` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: lam < n | `Secp256k1.lam_lt_n` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta < p | `Secp256k1.beta_lt_p` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| pollard-multistage-004 (Lagrange foundation) | `order_dvd_card` | Ecdlp/Lagrange.lean | Mathlib | proved |
| sec2-secp256k1-group-006 / sec2-domain-parameters-001 (cofactor) | `Ecdlp.Proved.cofactor_card_mul_index` | Ecdlp/Proved/Cofactor.lean | Mathlib | proved |
| prime-order ⇒ generator (no small subgroup) | `Ecdlp.Proved.orderOf_eq_card_of_prime` | Ecdlp/Proved/PrimeOrder.lean | Mathlib | proved |
| GLV eigenvalue is a cube root of unity (ring form) | `Ecdlp.Proved.cube_root_of_eigenvalue` | Ecdlp/Proved/CubeRoot.lean | Mathlib | proved |
| generic-group: distinct affine forms collide ≤ once | `Ecdlp.GenericGroup.collisionSet_card_le_one` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| generic-group: ≤ q·q−q colliding logs (union bound) | `Ecdlp.GenericGroup.badSet_card_le` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| **generic-group DLP lower bound `p ≤ q·q` (Shoup/Nechaev `Ω(√p)`)** | `Ecdlp.GenericGroup.generic_dlog_query_bound` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| generic-group lower bound, square-root form `√p ≤ q` | `Ecdlp.GenericGroup.generic_dlog_sqrt_bound` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| quantitative Shoup bound: success count ≤ q·q−q+1 | `Ecdlp.GenericGroup.generic_success_le` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| secp256k1 group order `2^255 < n` | `Ecdlp.GenericGroup.two_pow_255_lt_secp256k1_n` | Ecdlp/Proved/Secp256k1GenericSecurity.lean | native_decide | proved |
| **secp256k1 ≥ 128-bit generic security (`2^127 < q`)** | `Ecdlp.GenericGroup.secp256k1_generic_security` | Ecdlp/Proved/Secp256k1GenericSecurity.lean | Mathlib + native_decide | proved¹ |
| baby-step giant-step decomposition (`O(√n)` upper bound) | `Ecdlp.GenericGroup.bsgs_decomp` | Ecdlp/Proved/BabyStepGiantStep.lean | Mathlib | proved |
| baby/giant step count `n ≤ ⌈√n⌉²` (`Θ(√n)` closure) | `Ecdlp.GenericGroup.bsgs_steps_sq_ge` | Ecdlp/Proved/BabyStepGiantStep.lean | Mathlib | proved |
| Pollard rho: a collision exists within `card` steps (pigeonhole) | `Ecdlp.GenericGroup.pollard_rho_collision` | Ecdlp/Proved/PollardRho.lean | Mathlib | proved |

**Total: 23 theorems proved** (9 concrete facts via `native_decide`, 14 structural
via Mathlib). **0 open obligations.** The generic discrete-log complexity is now
bracketed on both sides: `Ω(√p)` lower bound (`generic_dlog_query_bound`) and
`O(√n)` upper bound (`bsgs_decomp`), i.e. `Θ(√n)`; Pollard rho's collision is
guaranteed by pigeonhole.

¹ `secp256k1_generic_security` is stated conditional on the hypothesis
`[Fact n.Prime]` — the standard, published primality of the secp256k1 group order
(SEC 2), which is not brute-force decidable for a 256-bit number. This is a
hypothesis, **not an axiom**; the kernel still checks the full derivation.

## How this grows
A new claim from `formalizable` becomes a theorem in `Ecdlp/`, gets committed,
and CI verifies it. On green, add its row here. The no-`sorry` gate guarantees a
green build means every listed theorem is fully proved.
