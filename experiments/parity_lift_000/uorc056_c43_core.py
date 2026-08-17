from __future__ import annotations

from typing import Any

try:
    from uorc056_c39_half_miller import TOYS, environment, legendre
except ImportError:
    from half_miller_lab import TOYS, environment, legendre


PREVIOUS_HELD_OUT = (
    (61, 61, (2, 25), 13, 47),
    (97, 79, (1, 28), 35, 55),
    (211, 199, (3, 33), 14, 106),
)

NEW_HELD_OUT = (
    (349, 313, (2, 109), 122, 214),
    (433, 397, (1, 21), 198, 362),
    (577, 613, (1, 68), 213, 65),
    (733, 691, (6, 174), 307, 253),
    (823, 829, (1, 255), 174, 125),
    (907, 967, (2, 165), 384, 824),
)

ALL_ROWS = TOYS + PREVIOUS_HELD_OUT + NEW_HELD_OUT

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
SECP_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
SECP_A = 0x96512C530B53BECF99A0CC5F16EB89A4C21AEF26F30180F962104448283F449F
SECP_B = 0x7015EAE8011C9350D55357787AA75CFC7A95382D5E54AA836B076F226E046953

BASE_PAIRS = tuple((a, b) for a in range(-3, 4) for b in range(-3, 4) if b)
PERIOD_SHIFTS = tuple(
    (r, s)
    for r in range(-2, 3)
    for s in range(-2, 3)
    if (r, s) != (0, 0)
)
FEATURE_NAMES = ("quadratic_character", "lsb", "half", "quartile", "octant")

def count_base_points(p: int) -> int:
    total = 1
    for x in range(p):
        symbol = legendre((x * x * x + 7) % p, p)
        total += 1 if symbol == 0 else 2 if symbol == 1 else 0
    return total


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


class DivisionAtPoint:
    """Division-polynomial values at one non-2-torsion affine point."""

    def __init__(self, p: int, a: int, b: int, x: int, y: int):
        self.p = p
        self.a = a % p
        self.b = b % p
        self.x = x % p
        self.y = y % p
        self.inv_2y = pow(2 * self.y, -1, p)
        self.cache: dict[int, int] = {
            0: 0,
            1: 1,
            2: 2 * self.y % p,
        }
        self.cache[3] = (
            3 * self.x**4
            + 6 * self.a * self.x**2
            + 12 * self.b * self.x
            - self.a**2
        ) % p
        self.cache[4] = (
            4
            * self.y
            * (
                self.x**6
                + 5 * self.a * self.x**4
                + 20 * self.b * self.x**3
                - 5 * self.a**2 * self.x**2
                - 4 * self.a * self.b * self.x
                - 8 * self.b**2
                - self.a**3
            )
        ) % p

    def psi(self, index: int) -> int:
        if index < 0:
            return -self.psi(-index) % self.p
        if index in self.cache:
            return self.cache[index]
        p = self.p
        if index & 1:
            m = (index - 1) // 2
            value = (
                self.psi(m + 2) * pow(self.psi(m), 3, p)
                - self.psi(m - 1) * pow(self.psi(m + 1), 3, p)
            ) % p
        else:
            m = index // 2
            value = (
                self.psi(m)
                * self.inv_2y
                * (
                    self.psi(m + 2) * pow(self.psi(m - 1), 2, p)
                    - self.psi(m - 2) * pow(self.psi(m + 1), 2, p)
                )
            ) % p
        self.cache[index] = value
        return value


class DivisionSequence(DivisionAtPoint):
    def __init__(self, row: tuple[int, int, tuple[int, int], int, int]):
        E, n, G, S, beta, lam = environment(row)
        super().__init__(E.p, E.a, E.b, G[0].a, G[1].a)
        self.E = E
        self.n = n
        self.G = G
        self.S = S
        self.beta = beta
        self.lam = lam

    def quasi_constants(self) -> tuple[int, int]:
        w_n1 = self.psi(self.n + 1)
        A = (
            self.psi(self.n + 2)
            * pow(self.psi(2) * w_n1 % self.p, -1, self.p)
        ) % self.p
        B = w_n1 * pow(A, -1, self.p) % self.p
        return A, B

    def dependent_net(self, a: int, b: int, k: int) -> int | None:
        """Normalized rank-two net W_(G,[k]G)(a,b) on its preferred chart."""
        w_k = self.psi(k)
        w_k1 = self.psi(k + 1)
        if w_k == 0 or w_k1 == 0:
            return None
        numerator = self.psi(a + b * k)
        exponent_k = b * b - a * b
        exponent_k1 = a * b

        def signed_power(value: int, exponent: int) -> int | None:
            if exponent >= 0:
                return pow(value, exponent, self.p)
            if value == 0:
                return None
            return pow(pow(value, -1, self.p), -exponent, self.p)

        left = signed_power(w_k, exponent_k)
        right = signed_power(w_k1, exponent_k1)
        if left is None or right is None:
            return None
        denominator = left * right % self.p
        if denominator == 0:
            return None
        return numerator * pow(denominator, -1, self.p) % self.p


def verify_fixture(row: tuple[int, int, tuple[int, int], int, int]) -> None:
    E, n, G, S, beta, lam = environment(row)
    assert count_base_points(E.p) == n
    assert E.on_curve(G)
    assert E.mul(n, G) is None
    assert E.mul(lam, G) == (G[0] * E.c(beta), G[1])
    assert (lam * lam + lam + 1) % n == 0
    assert E.on_curve(S)


def near_period_value(ds: DivisionSequence, k: int) -> int:
    Q = ds.E.mul(k, ds.G)
    assert Q is not None
    return DivisionAtPoint(ds.p, 0, 7, Q[0].a, Q[1].a).psi(ds.n + 1)


def alpha_bit(a: int, b: int, r: int, s: int) -> int:
    return (a * s + b * r + s * s + r * s) & 1


def beta_bit(a: int, b: int, r: int, s: int) -> int:
    return (a * s + b * r + r * s) & 1


def period_lattice_character_rhs(
    c: int,
    near_k: int,
    near_k1: int,
    a: int,
    b: int,
    r: int,
    s: int,
) -> int:
    alpha = alpha_bit(a, b, r, s)
    beta = beta_bit(a, b, r, s)
    return (
        (c if ((r + beta) & 1) else 1)
        * (near_k if alpha else 1)
        * (near_k1 if beta else 1)
    )



def secp256k1_certificate() -> dict[str, Any]:
    sequence = DivisionAtPoint(SECP_P, 0, 7, SECP_GX, SECP_GY)
    assert sequence.psi(SECP_N) == 0
    w_n1 = sequence.psi(SECP_N + 1)
    A = (
        sequence.psi(SECP_N + 2)
        * pow(sequence.psi(2) * w_n1 % SECP_P, -1, SECP_P)
    ) % SECP_P
    B = w_n1 * pow(A, -1, SECP_P) % SECP_P
    assert A == SECP_A
    assert B == SECP_B
    assert quadratic_character(A, SECP_P) == 1
    assert quadratic_character(B, SECP_P) == -1
    assert quadratic_character(w_n1, SECP_P) == -1

    checks = 0
    residues = (
        1,
        2,
        3,
        5,
        7,
        8,
        17,
        31,
        127,
        255,
        (SECP_N - 1) // 2,
        (SECP_N + 1) // 2,
        SECP_N - 2,
        SECP_N - 1,
    )
    for residue in residues:
        for period in (-2, -1, 0, 1, 2):
            assert sequence.psi(period * SECP_N + residue) == (
                sequence.psi(residue)
                * pow(A, residue * period, SECP_P)
                * pow(B, period * period, SECP_P)
            ) % SECP_P
            checks += 1

    return {
        "p": SECP_P,
        "n": SECP_N,
        "A": A,
        "A_hex": hex(A),
        "B": B,
        "B_hex": hex(B),
        "chi_A": quadratic_character(A, SECP_P),
        "chi_B": quadratic_character(B, SECP_P),
        "chi_psi_n_plus_1_at_G": quadratic_character(w_n1, SECP_P),
        "p_mod_4": SECP_P % 4,
        "v2_p_minus_1": 1,
        "quasiperiodicity_checks": checks,
        "division_sequence_cache_entries": len(sequence.cache),
    }

