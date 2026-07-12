#!/usr/bin/env python3
"""Independent replay and scientific-scope validator for P0 run manifests.

This is intentionally separate from the experiment driver.  A run is not accepted
merely because the producing script printed a success marker: the committed
manifest, curve parameters, GLV eigenvalue, and example relations are checked again.

Legacy manifests remain readable.  They receive a warning when a cofactor greater
than one means that an ambient-curve factor base was not contained in ``<G>``.
Schema-v1 manifests fail closed on that condition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path

import sympy

from toy_curves import ToyCurve, ec_add, ec_mul

HERE = Path(__file__).resolve().parent


def sha256_obj(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def on_curve(P, p: int, b: int) -> bool:
    if P is None:
        return True
    x, y = P
    return (y * y - x * x * x - b) % p == 0


def add_signed(P, coefficient: int, p: int):
    return ec_mul(coefficient, P, 0, p)


def resolve_code_path(recorded: str) -> Path:
    candidate = Path(recorded)
    if candidate.is_absolute():
        return candidate
    repo_root = HERE.parent.parent
    direct = repo_root / candidate
    if direct.is_file():
        return direct
    legacy = HERE / candidate.name
    return legacy


def validate_example(measurement: dict, errors: list[str]) -> None:
    example = measurement.get("example_relation")
    if not example:
        return
    p = int(measurement["p"])
    b = int(measurement["b"])
    # Invariant/GLV variants record both stored representatives and the actual
    # phi^m-transformed points used in the equality. Replay the latter when present.
    Pi = tuple(example.get("phi_m_P_i", example.get("phi_s_P_i", example["P_i"])))
    Pj = tuple(example.get("phi_m_P_j", example.get("phi_s_P_j", example["P_j"])))
    R = tuple(example["R"])
    for name, point in (("P_i", Pi), ("P_j", Pj), ("R", R)):
        if not on_curve(point, p, b):
            errors.append(f"{name} is not on E_{b}/F_{p}: {point}")
    lhs = ec_add(
        add_signed(Pi, int(example["e_i"]), p),
        add_signed(Pj, int(example["e_j"]), p),
        0,
        p,
    )
    if lhs != R:
        errors.append(f"relation replay failed: {lhs} != {R}")
    generator = measurement.get("generator")
    if generator is not None and "k" in example:
        expected = ec_mul(int(example["k"]), tuple(generator), 0, p)
        if expected != R:
            errors.append(f"target replay failed: [k]G={expected} != R={R}")


def validate_measurement(
    measurement: dict,
    schema_version: int,
    errors: list[str],
    warnings: list[str],
) -> None:
    p = int(measurement["p"])
    b = int(measurement["b"])
    ell = int(measurement["ell"])
    cofactor = int(measurement["cofactor"])
    order = int(measurement.get("order", ell * cofactor))
    label = f"p={p}, b={b}, B={measurement.get('base_size', '?')}"

    if not sympy.isprime(p):
        errors.append(f"{label}: p is not prime")
    if p % 3 != 1:
        errors.append(f"{label}: p != 1 mod 3")
    if not sympy.isprime(ell):
        errors.append(f"{label}: ell is not prime")
    if order != ell * cofactor:
        errors.append(f"{label}: order != ell * cofactor")
    trace = p + 1 - order
    if trace * trace > 4 * p:
        errors.append(f"{label}: order violates Hasse")
    if order % (ell * ell) == 0:
        errors.append(f"{label}: ell^2 divides #E; <G> uniqueness was not established")

    if cofactor != 1:
        msg = (
            f"{label}: cofactor={cofactor}; an x-factor base sampled from all E(F_p) "
            "contains points whose logarithms relative to G may be undefined"
        )
        if schema_version >= 1:
            errors.append(msg)
        else:
            warnings.append("LEGACY SCIENTIFIC-SCOPE WARNING: " + msg)

    generator = measurement.get("generator")
    beta = measurement.get("beta")
    lam = measurement.get("lambda")
    if generator is not None and beta is not None and lam is not None:
        G = tuple(generator)
        C = ToyCurve(p, b, order, ell, cofactor, G, int(beta), int(lam), p.bit_length())
        if not C.on_curve(G):
            errors.append(f"{label}: generator is not on the curve")
        if ec_mul(ell, G, 0, p) is not None:
            errors.append(f"{label}: [ell]G != O")
        if (C.lam * C.lam + C.lam + 1) % ell != 0:
            errors.append(f"{label}: lambda is not a nontrivial cube-root eigenvalue")
        if C.phi(G) != ec_mul(C.lam, G, 0, p):
            errors.append(f"{label}: phi(G) != [lambda]G")
    elif schema_version >= 1:
        errors.append(f"{label}: schema-v1 measurement lacks generator/beta/lambda replay data")

    validate_example(measurement, errors)


def validate_manifest(path: Path, check_code: bool = False) -> tuple[list[str], list[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []
    schema_version = int(doc.get("schema_version", 0))

    expected_hash = sha256_obj(doc.get("results", {}))
    if doc.get("results_hash") != expected_hash:
        errors.append("results_hash does not match canonical results payload")

    if schema_version >= 1:
        for field in ("git_commit", "command", "timestamp", "code_hashes", "tools"):
            if not doc.get(field):
                errors.append(f"schema-v1 manifest missing {field}")

    if check_code:
        for recorded, digest in doc.get("code_hashes", {}).items():
            code_path = resolve_code_path(recorded)
            if not code_path.is_file():
                errors.append(f"recorded code file is missing: {recorded}")
                continue
            actual = hashlib.sha256(code_path.read_bytes()).hexdigest()
            if actual != digest:
                errors.append(f"code hash mismatch for {recorded}: {actual} != {digest}")

    results = doc.get("results", {})
    measurements: list[dict] = []
    for key, value in results.items():
        if (key == "measurements" or key.endswith("_measurements")) and isinstance(value, list):
            measurements.extend(item for item in value if isinstance(item, dict))
    if not measurements and "skeptic" not in str(doc.get("variant", "")):
        warnings.append("manifest contains no measurement rows")
    for measurement in measurements:
        validate_measurement(measurement, schema_version, errors, warnings)
    return errors, warnings


def self_test() -> None:
    """Audit the CM discriminator and GLV eigenvalue against an exact small-field oracle."""
    from toy_curves import exact_curve_order, find_toy_curve

    for bits in (12, 16):
        curve = find_toy_curve(bits, seed=7, require_cofactor_one=True)
        assert exact_curve_order(curve.p, curve.b) == curve.order
        assert curve.phi(curve.gen) == ec_mul(curve.lam, curve.gen, 0, curve.p)
        assert curve.cofactor == 1
    print("P0 correctness self-test OK")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="*", type=Path)
    parser.add_argument("--check-code", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    manifests = args.manifests or sorted((HERE / "runs").glob("*.json"))
    failed = False
    for manifest in manifests:
        errors, warnings = validate_manifest(manifest, check_code=args.check_code)
        print(f"[{manifest.name}] errors={len(errors)} warnings={len(warnings)}")
        for warning in warnings:
            print(f"  WARNING: {warning}")
        for error in errors:
            print(f"  ERROR: {error}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
