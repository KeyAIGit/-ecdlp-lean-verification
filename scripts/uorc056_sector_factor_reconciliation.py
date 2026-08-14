from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence
from uorc056_toy_factory import DEFAULT_INSTANCES, build_fixture, interpolate_from_basis, lagrange_basis, poly_add, poly_divmod, poly_mod, poly_mul, poly_scale, poly_sub
PROFILE_ID = 'UORC-056-SECTOR-FACTOR-RECONCILIATION-V16'
DEFAULT_OUTPUT = Path('experiments/uorc056/sector_factor_reconciliation_results.json')
SECP256K1_N = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
SECP256K1_LAMBDA = int('5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72', 16)

def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + '\n'

def trim(poly: Sequence[int], p: int) -> list[int]:
    out = [int(coefficient) % p for coefficient in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]

def poly_gcd(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    a = trim(left, p)
    b = trim(right, p)
    while b != [0]:
        _quotient, remainder = poly_divmod(a, b, p)
        a, b = (b, remainder)
    return poly_scale(a, pow(a[-1], -1, p), p)

def poly_xgcd(left: Sequence[int], right: Sequence[int], p: int) -> tuple[list[int], list[int], list[int]]:
    old_r, r = (trim(left, p), trim(right, p))
    old_s, s = ([1], [0])
    old_t, t = ([0], [1])
    while r != [0]:
        quotient, remainder = poly_divmod(old_r, r, p)
        old_r, r = (r, remainder)
        old_s, s = (s, poly_sub(old_s, poly_mul(quotient, s, p), p))
        old_t, t = (t, poly_sub(old_t, poly_mul(quotient, t, p), p))
    leading_inverse = pow(old_r[-1], -1, p)
    return (poly_scale(old_r, leading_inverse, p), poly_scale(old_s, leading_inverse, p), poly_scale(old_t, leading_inverse, p))

def poly_inv_mod(value: Sequence[int], modulus: Sequence[int], p: int) -> list[int]:
    gcd, inverse, _cofactor = poly_xgcd(value, modulus, p)
    if gcd != [1]:
        raise ZeroDivisionError('polynomial is not invertible modulo the modulus')
    return poly_mod(inverse, modulus, p)

def scale_variable(poly: Sequence[int], scale: int, p: int) -> list[int]:
    return trim([coefficient * pow(scale, degree, p) % p for degree, coefficient in enumerate(poly)], p)

def point_sign(k: int) -> int:
    return -1 if k & 1 else 1

def glv_state(k: int, n: int, lam: int) -> dict[str, int]:
    k0 = k % n
    if k0 == 0:
        raise ValueError('the canonical scalar must be nonzero')
    k1 = lam * k0 % n
    k2 = lam * k1 % n
    scalar_sum = k0 + k1 + k2
    if scalar_sum % n:
        raise AssertionError('GLV representatives do not sum to a multiple of n')
    gamma = scalar_sum // n
    if gamma not in (1, 2):
        raise AssertionError('unexpected order-three GLV carry digit')
    s0, s1, s2 = (point_sign(k0), point_sign(k1), point_sign(k2))
    carry = point_sign(gamma)
    sector = s1 * s2
    if s0 * s1 * s2 != carry:
        raise AssertionError('V15 carry did not equal the legacy GLV carry')
    if s0 != carry * sector:
        raise AssertionError('carry-sector factorization failed')
    return {'k0': k0, 'k1': k1, 'k2': k2, 'gamma': gamma, 'parity': s0, 'carry': carry, 'sector': sector}

def classify_branch(signs: Sequence[int]) -> str:
    s0, s1, s2 = signs
    if s0 == s1 == s2:
        return 'uniform'
    if s1 == s2:
        return 'minority_0'
    if s0 == s2:
        return 'minority_1'
    if s0 == s1:
        return 'minority_2'
    raise AssertionError('three signs must be uniform or have one minority')

def floor_sum(n: int, modulus: int, multiplier: int, offset: int) -> tuple[int, int]:
    if n < 0 or modulus <= 0 or multiplier < 0 or (offset < 0):
        raise ValueError('floor_sum expects nonnegative inputs and positive modulus')
    answer = 0
    rounds = 0
    while True:
        rounds += 1
        if multiplier >= modulus:
            answer += (n - 1) * n * (multiplier // modulus) // 2
            multiplier %= modulus
        if offset >= modulus:
            answer += n * (offset // modulus)
            offset %= modulus
        top = multiplier * n + offset
        if top < modulus:
            return (answer, rounds)
        n = top // modulus
        offset = top % modulus
        modulus, multiplier = (multiplier, modulus)

def parity_correlation_direct(n: int, multiplier: int) -> int:
    return sum((point_sign(k) * point_sign(multiplier * k % n) for k in range(1, n)))

def parity_correlation_certificate(n: int, multiplier: int) -> dict[str, int]:
    if n <= 1 or n % 2 == 0 or math.gcd(n, multiplier) != 1:
        raise ValueError('the correlation certificate needs odd n and a unit')
    half = (n - 1) // 2
    a1, rounds1 = floor_sum(half, n, multiplier, multiplier)
    a2, rounds2 = floor_sum(half, n, 2 * multiplier, 2 * multiplier)
    correlation = n - 1 - 4 * a2 + 8 * a1
    return {'half': half, 'A1': a1, 'A2': a2, 'correlation': correlation, 'A1_euclidean_rounds': rounds1, 'A2_euclidean_rounds': rounds2}

def diagnostic_floor_sum_replay(limit: int=255) -> dict[str, int | bool]:
    unit_multipliers = 0
    scalar_terms = 0
    for n in range(3, limit + 1, 2):
        for multiplier in range(1, n):
            if math.gcd(n, multiplier) != 1:
                continue
            unit_multipliers += 1
            scalar_terms += n - 1
            certificate = parity_correlation_certificate(n, multiplier)
            direct = parity_correlation_direct(n, multiplier)
            if certificate['correlation'] != direct:
                raise AssertionError(f'floor-sum correlation failed for n={n}, a={multiplier}')
    return {'odd_moduli_through': limit, 'unit_multipliers': unit_multipliers, 'scalar_terms': scalar_terms, 'all_passed': True}

def curve_record(instance) -> dict[str, Any]:
    p = instance.curve.p
    n = instance.subgroup_order
    beta = int(instance.cm_beta)
    beta2 = beta * beta % p
    lam = int(instance.glv_lambda)
    fixture = build_fixture(instance, include_all_markers=True)
    kernel = fixture['kernel_coefficients_low_to_high']
    half_points = [tuple(point) for point in fixture['base_half_points']]
    _kernel_again, basis = lagrange_basis([int(point[0]) for point in half_points], p)
    if _kernel_again != kernel:
        raise AssertionError('reconstructed interpolation kernel drifted')
    curve_polynomial = [instance.curve.b % p, instance.curve.a % p, 0, 1]
    inverse_curve_polynomial = poly_inv_mod(curve_polynomial, kernel, p)
    sector_polynomials: dict[int, list[int]] = {}
    representative_degrees: list[int] = []
    plus_counts: list[int] = []
    minus_counts: list[int] = []
    branch_reference: dict[str, int] | None = None
    scalar_reconciliation_checks = 0
    for marker in range(1, n):
        root = fixture['marked_roots'][str(marker)]['coefficients_low_to_high']
        root_beta = scale_variable(root, beta, p)
        root_beta2 = scale_variable(root, beta2, p)
        sector_from_root = poly_mod(poly_mul(poly_mul(root_beta, root_beta2, p), inverse_curve_polynomial, p), kernel, p)
        inverse_marker = pow(marker, -1, n)
        sector_values: list[int] = []
        branch_counts = {'uniform': 0, 'minority_0': 0, 'minority_1': 0, 'minority_2': 0}
        for half_index in range(1, (n - 1) // 2 + 1):
            relative_scalar = half_index * inverse_marker % n
            state = glv_state(relative_scalar, n, lam)
            sector_values.append(1 if state['sector'] == 1 else p - 1)
            signs = (point_sign(state['k0']), point_sign(state['k1']), point_sign(state['k2']))
            branch_counts[classify_branch(signs)] += 1
        sector_from_interpolation = interpolate_from_basis(sector_values, basis, p)
        if sector_from_root != sector_from_interpolation:
            raise AssertionError('oriented-root and scalar sector polynomials differ')
        if poly_mod(poly_sub(poly_mul(sector_from_root, sector_from_root, p), [1], p), kernel, p) != [0]:
            raise AssertionError('sector representative is not an involution')
        plus_factor = poly_gcd(kernel, poly_sub(sector_from_root, [1], p), p)
        minus_factor = poly_gcd(kernel, poly_add(sector_from_root, [1], p), p)
        if poly_mul(plus_factor, minus_factor, p) != kernel:
            raise AssertionError('binary sector factors do not multiply to K_H')
        inverse_minus_mod_plus = poly_inv_mod(poly_mod(minus_factor, plus_factor, p), plus_factor, p)
        plus_idempotent = poly_mod(poly_mul(minus_factor, inverse_minus_mod_plus, p), kernel, p)
        sector_from_crt = poly_mod(poly_sub(poly_scale(plus_idempotent, 2, p), [1], p), kernel, p)
        if sector_from_crt != sector_from_root:
            raise AssertionError('CRT involution reconstruction failed')
        plus_count = sector_values.count(1)
        minus_count = sector_values.count(p - 1)
        if len(plus_factor) - 1 != plus_count:
            raise AssertionError('plus-factor degree does not equal its root count')
        if len(minus_factor) - 1 != minus_count:
            raise AssertionError('minus-factor degree does not equal its root count')
        if branch_reference is None:
            branch_reference = branch_counts
        elif branch_counts != branch_reference:
            raise AssertionError('branch cardinalities changed under re-marking')
        sector_polynomials[marker] = sector_from_root
        representative_degrees.append(len(sector_from_root) - 1)
        plus_counts.append(plus_count)
        minus_counts.append(minus_count)
        for k in range(1, n):
            glv_state(k, n, lam)
            scalar_reconciliation_checks += 1
    if branch_reference is None:
        raise AssertionError('missing branch cardinalities')
    if len(set(representative_degrees)) != 1:
        raise AssertionError('sector polynomial degree changed under re-marking')
    if len(set(plus_counts)) != 1 or len(set(minus_counts)) != 1:
        raise AssertionError('sector-factor degrees changed under re-marking')
    for marker, sector in sector_polynomials.items():
        if sector != sector_polynomials[n - marker]:
            raise AssertionError('J_{-G}=J_G covariance failed')
        rotated_marker = lam * marker % n
        rotated_polynomial = poly_mod(scale_variable(sector, beta2, p), kernel, p)
        if sector_polynomials[rotated_marker] != rotated_polynomial:
            raise AssertionError('generator GLV covariance failed')
    plus_count = plus_counts[0]
    minus_count = minus_counts[0]
    representative_degree = representative_degrees[0]
    correlation = parity_correlation_direct(n, lam)
    certificate = parity_correlation_certificate(n, lam)
    if certificate['correlation'] != correlation:
        raise AssertionError('toy floor-sum certificate disagrees with replay')
    if correlation != 2 * (plus_count - minus_count):
        raise AssertionError('sector factor counts do not match correlation')
    if representative_degree != (n - 3) // 2:
        raise AssertionError('canonical sector polynomial is not maximal degree')
    minority_degree = branch_reference['minority_0']
    if not minority_degree == branch_reference['minority_1'] == branch_reference['minority_2']:
        raise AssertionError('the three minority factor degrees must agree')
    return {'id': instance.instance_id, 'p': p, 'n': n, 'lambda': lam, 'kernel_degree': (n - 1) // 2, 'sector_plus_factor_degree': plus_count, 'sector_minus_factor_degree': minus_count, 'direct_rational_degree_lower_bound': max(plus_count, minus_count), 'canonical_sector_polynomial_degree': representative_degree, 'branch_factor_degrees': branch_reference, 'parity_correlation': correlation, 'floor_sum_A1': certificate['A1'], 'floor_sum_A2': certificate['A2'], 'marked_roots': n - 1, 'kummer_evaluations': (n - 1) * (n - 1) // 2, 'scalar_reconciliation_checks': scalar_reconciliation_checks}

def secp256k1_record() -> dict[str, Any]:
    n = SECP256K1_N
    lam = SECP256K1_LAMBDA
    if (lam * lam + lam + 1) % n != 0:
        raise AssertionError('fixed secp256k1 lambda is not an order-three root')
    if pow(lam, 3, n) != 1 or lam == 1:
        raise AssertionError('fixed secp256k1 lambda has wrong order')
    certificate = parity_correlation_certificate(n, lam)
    correlation = certificate['correlation']
    if correlation != 208:
        raise AssertionError('fixed secp256k1 sector correlation drifted')
    if (n - 1 + correlation) % 4 or (n - 1 - correlation) % 4:
        raise AssertionError('sector sign counts are not integral')
    plus_degree = (n - 1 + correlation) // 4
    minus_degree = (n - 1 - correlation) // 4
    half_kernel_degree = (n - 1) // 2
    orbit_imbalance = correlation // 2
    each_minority = (half_kernel_degree - orbit_imbalance) // 4
    uniform = each_minority + orbit_imbalance
    if uniform + 3 * each_minority != half_kernel_degree:
        raise AssertionError('four branch factors do not partition K_H')
    if uniform + each_minority != plus_degree:
        raise AssertionError('plus sector factor has wrong branch decomposition')
    if 2 * each_minority != minus_degree:
        raise AssertionError('minus sector factor has wrong branch decomposition')
    lower_bound = max(plus_degree, minus_degree)
    return {'n': n, 'lambda': lam, 'lambda_order_three': True, 'half_kernel_degree': half_kernel_degree, 'floor_sum_A1': certificate['A1'], 'floor_sum_A2': certificate['A2'], 'floor_sum_A1_euclidean_rounds': certificate['A1_euclidean_rounds'], 'floor_sum_A2_euclidean_rounds': certificate['A2_euclidean_rounds'], 'sector_parity_correlation_all_nonzero_scalars': correlation, 'sector_plus_factor_degree': plus_degree, 'sector_minus_factor_degree': minus_degree, 'uniform_branch_factor_degree': uniform, 'each_minority_branch_factor_degree': each_minority, 'direct_field_valued_rational_degree_lower_bound': lower_bound, 'lower_bound_bit_length': lower_bound.bit_length(), 'claim_boundary': 'degree/representation lower bound for an ordinary rational function returning field values +/-1; not an arithmetic-circuit lower bound and not a bound for chi(f)'}

def run() -> dict[str, Any]:
    diagnostic = diagnostic_floor_sum_replay()
    if diagnostic != {'odd_moduli_through': 255, 'unit_multipliers': 13230, 'scalar_terms': 2240852, 'all_passed': True}:
        raise AssertionError('floor-sum diagnostic totals drifted')
    curve_rows = [curve_record(instance) for instance in DEFAULT_INSTANCES]
    marked_roots = sum((row['marked_roots'] for row in curve_rows))
    kummer_evaluations = sum((row['kummer_evaluations'] for row in curve_rows))
    scalar_checks = sum((row['scalar_reconciliation_checks'] for row in curve_rows))
    aggregate_plus = sum((row['marked_roots'] * row['sector_plus_factor_degree'] for row in curve_rows))
    aggregate_minus = sum((row['marked_roots'] * row['sector_minus_factor_degree'] for row in curve_rows))
    if marked_roots != 438 or kummer_evaluations != 23130:
        raise AssertionError('frozen V16 root/evaluation totals drifted')
    if scalar_checks != 46260:
        raise AssertionError('frozen V16 scalar reconciliation total drifted')
    if aggregate_plus != 11742 or aggregate_minus != 11388:
        raise AssertionError('frozen sector-sign totals drifted')
    return {'schema_version': '1.0', 'profile_id': PROFILE_ID, 'exact_reconciliation': {'carry_identity': 'c=sigma(Q)sigma(alpha Q)sigma(alpha^2 Q)=g_G(Q)', 'public_residue_bridge': 'c=C3_G(Q)R3_G(Q)=g_G(Q)', 'sector_identity': 'J_G(x(Q))=sigma(Q)g_G(Q)', 'sector_residue_form': 'J_G=C_G(alpha Q)C_G(alpha^2 Q)rho_G(alpha Q)rho_G(alpha^2 Q)', 'sector_R3_form': 'J_G=sigma(Q)C3_G(Q)R3_G(Q)', 'interpretation': 'V15 carry is exactly the legacy GLV carry; the sector is a complementary two-rotation product, not a public correction of R3'}, 'factor_normal_form': {'binary_factorization': 'K_H=K_{G,+}K_{G,-}, roots selected by J_G=+1 and -1', 'crt_idempotent': 'e_+=K_{G,-}*(K_{G,-}^{-1} mod K_{G,+}) mod K_H', 'crt_involution': 'J_G=2e_+-1 mod K_H', 'four_branch_factorization': 'K_H=K_uniform*K_minority0*K_minority1*K_minority2', 'generator_negation': 'J_{-G}=J_G', 'generator_glv_covariance': 'J_{alpha G}(X)=J_G(beta^2 X) mod K_H'}, 'floor_sum_certificate': {'formula': 'S(a;n)=(n-1)-4*A2+8*A1, A1=sum_{j=1}^m floor(a*j/n), A2=sum_{j=1}^m floor(2*a*j/n), m=(n-1)/2', 'diagnostic_odd_moduli_through': diagnostic['odd_moduli_through'], 'diagnostic_unit_multipliers': diagnostic['unit_multipliers'], 'diagnostic_scalar_terms': diagnostic['scalar_terms'], 'all_diagnostics_passed': diagnostic['all_passed']}, 'secp256k1': secp256k1_record(), 'exact_toy_replay': {'curves': len(curve_rows), 'marked_roots': marked_roots, 'kummer_evaluations': kummer_evaluations, 'scalar_reconciliation_checks': scalar_checks, 'aggregate_sector_plus_evaluations': aggregate_plus, 'aggregate_sector_minus_evaluations': aggregate_minus, 'all_canonical_sector_polynomial_degrees_maximal': True, 'curve_rows': curve_rows}, 'decision': 'legacy carry reconciled exactly; direct low-degree field-valued sector rational functions are excluded on secp256k1; compact high-degree circuits remain open', 'next_frontier': ['high-degree low-size or modular-composition evaluation of the sector involution', 'shared evaluation of legacy carry g_G and sector J_G without dense factors', 'additive mixed-CM-weight or field-valued circuits carrying a nontrivial C3 representation', 'formalize the floor-sum count and polynomial root-count transfer beyond the frozen arithmetic core'], 'scientific_boundary': 'No public sub-square-root parity evaluator or ECDLP algorithm is constructed.'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding='utf-8') != text:
            raise SystemExit('V16 sector-factor artifact drift')
        print('UORC056_SECTOR_FACTOR_RECONCILIATION_V16_OK')
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
