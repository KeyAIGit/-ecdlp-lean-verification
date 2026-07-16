#!/usr/bin/env python3
"""Design-insurance check for Ecdlp/Proved/NormEDSConsecutiveZeros.lean.

Numerically validates, over F_p (p = 10007), every ingredient of the Ward-style
no-consecutive-zeros proof for `normEDS b c d`:

  1. the master elliptic relation Rel3 (IsEllSequence) for W built from Mathlib's
     normEDS_odd / normEDS_even doubling recurrences (transcription check);
  2. the translation identity (*):  W(n+rho)*W(n-rho) = -W(rho+1)*W(rho-1)*W(n)^2
     at every zero position rho;
  3. the theorem itself: no consecutive zeros when not(b=c=0) and not(c=d=0);
  4. sharpness of both hypotheses ((0,0,d) zeroes W2,W3; (b,0,0) zeroes W3,W4);
  5. the Case-A divisibility structure (zeros lie in rho*Z when W(rho+1) != 0).

Nothing from this script enters the Lean proofs — the kernel is the judge; this
is transcription/design insurance only. Prints CERT_OK on success.
"""

import random

P = 10007  # prime


def make_get(b, c, d, p=P):
    """W = normEDS b c d over F_p via normEDS_odd / normEDS_even (valid for b != 0;
    the even recurrence divides by b)."""
    W = {0: 0, 1: 1, 2: b % p, 3: c % p, 4: (d * b) % p}
    binv = pow(b, p - 2, p) if b % p else None

    def get(n):
        assert n >= 0
        if n in W:
            return W[n]
        if n % 2 == 1:
            m = (n - 1) // 2
            v = (get(m + 2) * pow(get(m), 3, p) - get(m - 1) * pow(get(m + 1), 3, p)) % p
        else:
            m = n // 2
            assert binv is not None, "even recurrence needs b != 0"
            v = (get(m) * (pow(get(m - 1), 2, p) * get(m + 2)
                           - get(m - 2) * pow(get(m + 1), 2, p))) % p * binv % p
        W[n] = v
        return v

    return get


def signed(get, p=P):
    def Ws(n):
        return get(n) if n >= 0 else (-get(-n)) % p
    return Ws


def main():
    random.seed(1)
    p = P

    # 1) Rel3 (IsEllSequence)
    for _ in range(10):
        b, c, d = (random.randrange(1, p) for _ in range(3))
        Wf = signed(make_get(b, c, d))
        for _ in range(60):
            m, n, r = (random.randrange(-40, 40) for _ in range(3))
            lhs = Wf(m + n) * Wf(m - n) * pow(Wf(r), 2, p) % p
            rhs = (Wf(m + r) * Wf(m - r) * pow(Wf(n), 2, p)
                   - Wf(n + r) * Wf(n - r) * pow(Wf(m), 2, p)) % p
            assert lhs == rhs, ("Rel3 FAIL", b, c, d, m, n, r)

    # 2) translation identity (*) at zeros
    for _ in range(60):
        b, c, d = (random.randrange(1, p) for _ in range(3))
        g = make_get(b, c, d)
        Wf = signed(g)
        zeros = [n for n in range(1, 250) if g(n) == 0]
        for rho in zeros[:3]:
            for n in range(-30, 60):
                lhs = Wf(n + rho) * Wf(n - rho) % p
                rhs = (-Wf(rho + 1) * Wf(rho - 1) * pow(Wf(n), 2, p)) % p
                assert lhs == rhs, ("star FAIL", b, c, d, rho, n)

    # 3) no consecutive zeros under the sharp hypotheses
    for _ in range(400):
        b = random.randrange(1, p)
        c = random.randrange(0, p)
        d = random.randrange(0, p)
        if (b % p == 0 and c % p == 0) or (c % p == 0 and d % p == 0):
            continue
        g = make_get(b, c, d)
        zs = [n for n in range(1, 320) if g(n) == 0]
        for i in range(len(zs) - 1):
            assert zs[i + 1] != zs[i] + 1, ("CONSECUTIVE ZEROS", b, c, d, zs[i])

    # 4) sharpness
    g = make_get(1234, 0, 0)
    assert g(3) == 0 and g(4) == 0, "sharpness (b,0,0) FAIL"
    # (0,0,d): W2 = b = 0 and W3 = c = 0 definitionally.

    # 5) Case-A divisibility: zeros subset of rho*Z when W(rho+1) != 0
    for _ in range(40):
        b, c, d = (random.randrange(1, p) for _ in range(3))
        g = make_get(b, c, d)
        zs = [n for n in range(1, 250) if g(n) == 0]
        if not zs:
            continue
        rho = zs[0]
        if g(rho + 1) % p != 0:
            assert all(z % rho == 0 for z in zs), ("dvd FAIL", b, c, d, rho, zs)

    print("CERT_OK")


if __name__ == "__main__":
    main()
