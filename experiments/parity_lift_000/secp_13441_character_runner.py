#!/usr/bin/env python3
"""Safe runner for SECP-13441-CHARACTER-HELDOUT-022.

The underlying frozen screen uses a small trial-division helper for its toy
primes.  Its fixed secp256k1 cofactor is far too large for that helper.  This
runner replaces only that primality backend with SymPy's arbitrary-precision
`isprime` before invoking the unchanged experiment.
"""
from __future__ import annotations

import secp_13441_character_screen as screen
from sympy import isprime


def certified_is_prime(value: int) -> bool:
    return bool(isprime(value))


def main() -> None:
    screen.is_prime = certified_is_prime
    screen.main()


if __name__ == "__main__":
    main()
