#!/usr/bin/env python3
"""CORE-II residual "+companion" identity — numeric ground truth (N7 grind reference).

`notes/N7_EVEN_X_REDUCTION.md` records that CORE-II
(`w(2k+1)w(2k-1) = 3A⁴ + 4P A³ + 84 A B³ + 28 P B³`) does not close as a finite
`linear_combination` from the `normEDS_odd` expansions + the proved `somos4` slice
alone: it leaves a residual whose surviving part is the "+companion"
`w(k-1)² w(k+2) + w(k-2) w(k+1)²` (the `+` twin of the `ω`-numerator's `−` form),
which is not in the somos4 `k±1` window.

This script pins that residual to an EXACT identity and certifies it on the real
`normEDS` sequence (built as in `core_check.py`, over a field where `β²=4x³+28`
has a root). For secp256k1 (`y²=x³+7`, `β²=4x³+28`, `c=3x⁴+84x`):

    w(k-1)² w(k+2) + w(k-2) w(k+1)²  =  6 x² w(k) w(k+1) w(k-1) - (4x³+28) w(k)³

Verified for k=1..11 over many random x with `CERT_OK`. Because it carries
individual `w(k±2)` (not the somos4 *product* `w(k+2)w(k-2)`), it is a genuine
5-term EDS relation — the precise remaining brick CORE-II needs, closable by its
own `normEDSRec'` induction (cofactor via `scripts/certs/eds_cofactor_gen.py`).
Nothing here enters Lean; the kernel remains the sole judge.
"""

import random

pp = 10007


def build_w(b, c, d, N):
    B4 = pow(b, 4, pp)
    pre = [0] * (N + 6)
    pre[1] = pre[2] = 1
    pre[3] = c % pp
    pre[4] = d % pp
    for idx in range(5, N + 6):
        n = idx - 5
        m = n // 2
        if n % 2 == 0:
            f1 = B4 if m % 2 == 0 else 1
            f2 = 1 if m % 2 == 0 else B4
            pre[idx] = (pre[m + 4] * pow(pre[m + 2], 3, pp) * f1
                        - pre[m + 1] * pow(pre[m + 3], 3, pp) * f2) % pp
        else:
            pre[idx] = (pow(pre[m + 2], 2, pp) * pre[m + 3] * pre[m + 5]
                        - pre[m + 1] * pre[m + 3] * pow(pre[m + 4], 2, pp)) % pp

    def w(n):
        n = int(n)
        if n < 0:
            return (-w(-n)) % pp
        return (pre[n] * (b if n % 2 == 0 else 1)) % pp

    return w


def main():
    random.seed(7)
    ok = True
    tested = 0
    for _ in range(4000):
        x = random.randrange(pp)
        rhs = (4 * x**3 + 28) % pp
        if rhs == 0 or pow(rhs, (pp - 1) // 2, pp) != 1:
            continue
        b = pow(rhs, (pp + 1) // 4, pp)
        if (b * b - rhs) % pp:
            continue
        c = (3 * x**4 + 84 * x) % pp
        d = (2 * x**6 + 280 * x**3 - 784) % pp
        w = build_w(b, c, d, 40)
        for k in range(1, 12):
            L = (w(k - 1)**2 * w(k + 2) + w(k - 2) * w(k + 1)**2) % pp
            R = (6 * x**2 * w(k) * w(k + 1) * w(k - 1) - (4 * x**3 + 28) * w(k)**3) % pp
            if L != R:
                ok = False
                print("FAIL", x, k, L, R)
            tested += 1
        if tested > 600:
            break
    print(f"tested {tested} pairs; +companion identity holds:", ok)
    if ok:
        print("CERT_OK")


if __name__ == '__main__':
    main()
