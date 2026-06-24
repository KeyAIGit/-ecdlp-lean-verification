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

**Total: 13 theorems proved** (8 concrete secp256k1 facts via `native_decide`,
5 structural via Mathlib). **0 open obligations.**

## How this grows
A new claim from `formalizable` becomes a theorem in `Ecdlp/`, gets committed,
and CI verifies it. On green, add its row here. The no-`sorry` gate guarantees a
green build means every listed theorem is fully proved.
