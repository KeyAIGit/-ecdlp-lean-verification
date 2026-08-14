#!/usr/bin/env sage
"""SageMath 10.9 replay of UORC-056 fixtures.

Usage from the repository root:
    sage experiments/uorc056/sage/uorc056_replay.sage
"""

import json
from pathlib import Path

fixture_dir = Path("experiments/uorc056/fixtures")
paths = sorted(path for path in fixture_dir.glob("*.json") if path.name != "manifest.json")
if not paths:
    raise RuntimeError("no UORC-056 fixtures found")

for path in paths:
    data = json.loads(path.read_text(encoding="utf-8"))
    p = ZZ(data["instance"]["field_prime"])
    n = ZZ(data["instance"]["subgroup_order"])
    a = ZZ(data["instance"]["curve"]["a"])
    b = ZZ(data["instance"]["curve"]["b"])
    F = GF(p)
    R.<X> = PolynomialRing(F)
    E = EllipticCurve(F, [a, b])
    G = E(*data["instance"]["base_generator"])
    assert G.order() == n

    kernel = R(data["kernel_coefficients_low_to_high"])
    assert kernel.degree() == (n - 1) // 2
    assert kernel.is_squarefree()
    expected_kernel = prod(X - (j * G)[0] for j in range(1, (n - 1) // 2 + 1))
    assert kernel == expected_kernel

    curve_polynomial = X^3 + F(a) * X + F(b)
    for marker_text, row in data["marked_roots"].items():
        marker = ZZ(marker_text)
        root = R(row["coefficients_low_to_high"])
        assert (root^2 - curve_polynomial) % kernel == 0
        Gu = marker * G
        assert list(Gu)[:2] == row["marked_generator"]
        for k in range(1, n):
            Q = k * Gu
            expected = F(-1 if k % 2 else 1)
            assert root(Q[0]) / Q[1] == expected

    root_g = R(data["marked_roots"]["1"]["coefficients_low_to_high"])
    root_neg_g = R(data["marked_roots"][str(n - 1)]["coefficients_low_to_high"])
    assert root_neg_g == -root_g

print(f"UORC056_SAGE_REPLAY_OK count={len(paths)}")
