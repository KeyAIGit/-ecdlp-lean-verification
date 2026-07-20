#!/usr/bin/env python3
"""Design-insurance cert for Ecdlp/Proved/CubicSeparable.lean (E[2] separability brick).

Verifies the Bézout cofactors u₀, v₀ embedded in the Lean file satisfy the two
`native_decide` residue goals — (C u₀)·(X³+7) + (C v₀·X)·(3X²) = 1, i.e.
7·u₀ = 1 and u₀ + 3·v₀ = 0 mod p — and that u₀ = 7⁻¹, v₀ = −21⁻¹; plus the premise
p ∤ 21 that makes X³+7 separable (derivative 3X² vanishes only at 0, where the value is
7 ≠ 0), giving exactly 3 distinct roots over 𝔽̄_p and #E[2] = 1 + 3 = 4 = 2².

Nothing here enters the Lean proofs (the kernel re-checks the native_decide goals); this
is transcription/design insurance only. Prints CERT_OK on success.
"""

P = 2**256 - 2**32 - 977  # secp256k1 prime

# Constants exactly as written in Ecdlp/Proved/CubicSeparable.lean (u₀, v₀).
U0 = 99250362203413881791632272864589635302802843999120483462392214863921858289997
V0 = 5513909011300771210646237381366090850155713555506693525688456381328992127222


def main():
    assert (7 * U0) % P == 1, "residue 7*u0 = 1 FAILED"
    assert (U0 + 3 * V0) % P == 0, "residue u0 + 3*v0 = 0 FAILED"
    assert U0 == pow(7, P - 2, P), "u0 != 7^-1"
    assert V0 % P == (-pow(21, P - 2, P)) % P, "v0 != -21^-1"
    assert P % 3 != 0 and P % 7 != 0, "p divides 21 — cubic would be inseparable"
    # The full Bézout identity as a polynomial residue check at a few sample points:
    for t in (0, 1, 2, 12345, P - 1):
        lhs = (U0 * (t**3 + 7) + (V0 * t) * (3 * t**2)) % P
        assert lhs == 1, f"Bezout identity != 1 at x={t}"
    print("CERT_OK")


if __name__ == "__main__":
    main()
