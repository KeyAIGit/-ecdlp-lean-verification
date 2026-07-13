#!/usr/bin/env python3
"""
Certificate: re-verify every NUMERIC fact the Lean proof
`secp256k1_card_point_eq_n : Nat.card secp256k1.toAffine.Point = Secp256k1.n`
depends on. No elliptic-curve library is used; only sympy/int arithmetic.

Facts checked (each mirrors a `native_decide` or Nat lemma in the Lean file):
  (F1) p is the secp256k1 field prime  = 2^256 - 2^32 - 977.
  (F2) p mod 3 = 1   (so 3 | p-1; cubes form the index-3 subgroup).
  (F3) n <= 2*p + 1.
  (F4) 2*p + 1 < 3*n   (with F3, forces #E in {n, 2n}).
  (F5) (-7)^((p-1)/3) mod p != 1   (so -7 is NOT a cube in F_p).
  (F6) x^3 = -7 has NO root in F_p  (independent brute check via the same
       cubic-residue exponent test: -7 is a cube iff (-7)^((p-1)/3) == 1).
Extra sanity (not load-bearing but cross-checks the story):
  (S1) 3 * ((p-1)//3) == p-1.
  (S2) ((-7)^((p-1)/3))^3 mod p == 1  (it is a nontrivial cube root of unity).
  (S3) 2*n <= 2*p+1  (size bound alone does NOT kill 2n; 2-torsion needed).
"""
from sympy import isprime

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

ok = True
def check(name, cond):
    global ok
    status = "OK " if cond else "FAIL"
    print(f"  [{status}] {name}")
    ok = ok and cond

# F1
check("F1  p = 2^256 - 2^32 - 977", p == 2**256 - 2**32 - 977)
check("F1b p is prime", isprime(p))
check("F1c n is prime", isprime(n))

# F2
check("F2  p mod 3 == 1", p % 3 == 1)

# S1
e = (p - 1) // 3
check("S1  3*((p-1)//3) == p-1", 3 * e == p - 1)

# F3, F4, S3
check("F3  n <= 2*p + 1", n <= 2*p + 1)
check("F4  2*p + 1 < 3*n", 2*p + 1 < 3*n)
check("S3  2*n <= 2*p + 1 (2n NOT excluded by size)", 2*n <= 2*p + 1)

# F5 : (-7)^((p-1)/3) mod p != 1
val = pow((-7) % p, e, p)
check("F5  (-7)^((p-1)/3) mod p != 1", val != 1)
print(f"       value = {val}")

# S2 : its cube is 1  (nontrivial cube root of unity)
check("S2  (value)^3 mod p == 1", pow(val, 3, p) == 1)

# F6 : x^3 = -7 has no solution in F_p.
# Cubic residue criterion in F_p* with 3 | p-1: a (!=0) is a cube iff a^((p-1)/3)==1.
# -7 != 0 mod p, and F5 says the test fails, so -7 is a non-cube => no root.
neg7 = (-7) % p
check("F6a -7 != 0 mod p", neg7 != 0)
is_cube = pow(neg7, e, p) == 1
check("F6  x^3 = -7 has NO root in F_p (cubic-residue test fails)", not is_cube)

# Independent cross-check of F6 for a SMALL analogue to sanity the criterion:
# pick a known cube c=8=2^3 -> 8^((p-1)/3) must be 1.
check("F6-xcheck 8 IS a cube (8^e==1)", pow(8, e, p) == 1)

print()
if ok:
    print("CERT_OK")
else:
    print("CERT_FAIL")
    raise SystemExit(1)