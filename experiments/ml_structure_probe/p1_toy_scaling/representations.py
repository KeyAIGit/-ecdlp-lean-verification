#!/usr/bin/env python3
"""Public-only P1E representations and scalar-bit labels."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


PUBLIC_FIELDS = (
    "field_p",
    "group_order",
    "curve_a",
    "curve_b",
    "beta",
    "lambda",
    "gx",
    "gy",
    "qx",
    "qy",
)


def integer_bits(values: np.ndarray, width: int) -> np.ndarray:
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint64)
    return ((values.astype(np.uint64)[:, None] >> shifts) & 1).astype(np.float32)


def scalar_bits(records: np.ndarray, width: int) -> np.ndarray:
    return integer_bits(records["scalar"], width).astype(np.uint8)


def signed(bits: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(bits * np.float32(2.0) - np.float32(1.0))


def compressed_point_bits(
    x: np.ndarray, y: np.ndarray, width: int
) -> np.ndarray:
    parity = (y.astype(np.uint64) & 1).astype(np.float32).reshape((-1, 1))
    return np.concatenate((integer_bits(x, width), parity), axis=1)


def _opaque_point_bits(
    records: np.ndarray, prefix: str, width: int
) -> np.ndarray:
    del width
    opaque_width = 64
    output = np.empty((len(records), opaque_width), dtype=np.float32)
    x_field, y_field = (f"{prefix}x", f"{prefix}y")
    seen_labels: dict[int, tuple[int, int, int]] = {}
    for index, row in enumerate(records):
        payload = (
            b"keyai/p1-opaque-point/v1\0"
            + int(row["field_p"]).to_bytes(4, "big")
            + int(row[x_field]).to_bytes(4, "big")
            + int(row[y_field]).to_bytes(4, "big")
        )
        digest = hashlib.sha256(payload).digest()
        value = int.from_bytes(digest, "big")
        label = value >> (256 - opaque_width)
        point_identity = (
            int(row["field_p"]),
            int(row[x_field]),
            int(row[y_field]),
        )
        prior_identity = seen_labels.setdefault(label, point_identity)
        if prior_identity != point_identity:
            raise RuntimeError("64-bit opaque point-label collision")
        for bit in range(opaque_width):
            output[index, bit] = float((value >> (255 - bit)) & 1)
    return output


def _mismatched_q_coordinates(
    records: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Rotate Q within each curve/generator cluster without changing marginals."""
    qx = np.asarray(records["qx"]).copy()
    qy = np.asarray(records["qy"]).copy()
    groups = (
        records["curve_index"].astype(np.int64) * 16
        + records["generator_index"].astype(np.int64)
    )
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        if len(indices) < 2:
            raise ValueError("mismatched-Q control needs at least two rows per cluster")
        qx[indices] = np.roll(qx[indices], 1)
        qy[indices] = np.roll(qy[indices], 1)
    return qx, qy


@dataclass
class FeatureStore:
    records: np.ndarray
    width: int

    def __post_init__(self) -> None:
        if self.records.dtype.names is None:
            raise ValueError("P1E records must use a structured dtype")
        missing = set(PUBLIC_FIELDS + ("scalar",)) - set(self.records.dtype.names)
        if missing:
            raise ValueError(f"P1E records lack fields: {sorted(missing)}")
        self._cache: dict[str, np.ndarray] = {}

    def get(self, mode: str, leaked_bits: int = 0) -> np.ndarray:
        cache_key = f"{mode}/leak={leaked_bits}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        p_bits = integer_bits(self.records["field_p"], self.width)
        n_bits = integer_bits(self.records["group_order"], self.width)
        g_compressed = compressed_point_bits(
            self.records["gx"], self.records["gy"], self.width
        )
        q_compressed = compressed_point_bits(
            self.records["qx"], self.records["qy"], self.width
        )
        if mode == "compressed_relation_bits":
            value = np.concatenate((p_bits, n_bits, g_compressed, q_compressed), axis=1)
        elif mode == "affine_relation_bits":
            value = np.concatenate(
                (
                    p_bits,
                    n_bits,
                    integer_bits(self.records["gx"], self.width),
                    integer_bits(self.records["gy"], self.width),
                    integer_bits(self.records["qx"], self.width),
                    integer_bits(self.records["qy"], self.width),
                ),
                axis=1,
            )
        elif mode == "compressed_relation_glv_bits":
            value = np.concatenate(
                (
                    p_bits,
                    n_bits,
                    g_compressed,
                    q_compressed,
                    integer_bits(self.records["beta"], self.width),
                    integer_bits(self.records["lambda"], self.width),
                ),
                axis=1,
            )
        elif mode == "mismatched_relation_bits":
            mismatched_qx, mismatched_qy = _mismatched_q_coordinates(self.records)
            value = np.concatenate(
                (
                    p_bits,
                    n_bits,
                    g_compressed,
                    compressed_point_bits(
                        mismatched_qx, mismatched_qy, self.width
                    ),
                ),
                axis=1,
            )
        elif mode == "opaque_relation_bits":
            value = np.concatenate(
                (
                    p_bits,
                    n_bits,
                    _opaque_point_bits(self.records, "g", self.width),
                    _opaque_point_bits(self.records, "q", self.width),
                ),
                axis=1,
            )
        elif mode == "curve_generator_only_bits":
            value = np.concatenate((p_bits, n_bits, g_compressed), axis=1)
        else:
            raise ValueError(f"unknown P1E feature mode: {mode}")
        if leaked_bits:
            labels = scalar_bits(self.records, self.width).astype(np.float32)
            leak = labels if leaked_bits >= self.width else labels[:, -leaked_bits:]
            value = np.concatenate((value, leak), axis=1)
        value = signed(value)
        if not np.isfinite(value).all():
            raise FloatingPointError("non-finite P1E feature")
        self._cache[cache_key] = value
        return value


def public_fingerprint(records: np.ndarray) -> str:
    digest = hashlib.sha256()
    for field in PUBLIC_FIELDS:
        digest.update(np.ascontiguousarray(records[field]).tobytes())
    return digest.hexdigest()
