import sympy as sp
from sympy.polys.orderings import grevlex

def _lt(p):
    # leading term of nonzero Poly wrt grevlex: (monom, coeff)
    ts = p.terms()
    m = max(ts, key=lambda t: grevlex(t[0]))
    return m

def _div_mono(m1, m2):
    q = tuple(a-b for a, b in zip(m1, m2))
    return q if all(x >= 0 for x in q) else None

def _mono_poly(mono, coeff, gens, dom):
    return sp.Poly.from_dict({mono: coeff}, gens=gens, domain=dom)

class TrackedGB:
    def __init__(self, gens_exprs, gens):
        self.gens = tuple(gens)
        self.dom = sp.QQ
        n = len(gens_exprs)
        self.basis = []  # list of (poly, vec) vec: list of Poly cofactors, len n
        for i, g in enumerate(gens_exprs):
            p = sp.Poly(sp.expand(g), *self.gens, domain=self.dom)
            vec = [sp.Poly(1 if j == i else 0, *self.gens, domain=self.dom) for j in range(n)]
            self.basis.append((p, vec))
        self._buchberger()

    def _reduce(self, p, vec):
        rem = sp.Poly(0, *self.gens, domain=self.dom)
        while not p.is_zero:
            mono, coeff = _lt(p)
            hit = False
            for q, qv in self.basis:
                if q.is_zero: continue
                qm, qc = _lt(q)
                dm = _div_mono(mono, qm)
                if dm is not None:
                    f = _mono_poly(dm, coeff/qc, self.gens, self.dom)
                    p = p - f*q
                    vec = [a - f*b_ for a, b_ in zip(vec, qv)]
                    hit = True
                    break
            if not hit:
                t = _mono_poly(mono, coeff, self.gens, self.dom)
                rem = rem + t
                p = p - t
        return rem, vec

    def _buchberger(self, maxiter=4000):
        import itertools
        pairs = list(itertools.combinations(range(len(self.basis)), 2))
        it = 0
        while pairs:
            it += 1
            if it > maxiter: raise RuntimeError("buchberger cap")
            i, j = pairs.pop(0)
            pi, vi = self.basis[i]; pj, vj = self.basis[j]
            if pi.is_zero or pj.is_zero: continue
            mi, ci = _lt(pi); mj, cj = _lt(pj)
            lcm = tuple(max(a, b_) for a, b_ in zip(mi, mj))
            if tuple(a+b_ for a, b_ in zip(mi, mj)) == lcm:  # coprime -> skip
                continue
            fi = _mono_poly(_div_mono(lcm, mi), sp.QQ(1)/ci, self.gens, self.dom)
            fj = _mono_poly(_div_mono(lcm, mj), sp.QQ(1)/cj, self.gens, self.dom)
            sp_ = fi*pi - fj*pj
            sv = [fi*a - fj*b_ for a, b_ in zip(vi, vj)]
            rem, rv = self._reduce(sp_, sv)
            if not rem.is_zero:
                k = len(self.basis)
                self.basis.append((rem, rv))
                pairs.extend((x, k) for x in range(k))

    def express(self, f):
        """f expr -> (ok, cofactor exprs wrt original generators)"""
        p = sp.Poly(sp.expand(f), *self.gens, domain=self.dom)
        n = len(self.basis[0][1])
        vec = [sp.Poly(0, *self.gens, domain=self.dom) for _ in range(n)]
        rem, vec = self._reduce(p, [ -x for x in vec ])  # vec starts at 0
        # rem + sum(vec_i * g_i)?? bookkeeping: _reduce computes p = rem + sum((-vec)*g)...
        # We track: starting vec=0; each step vec -= f*qv  => at end p_orig = rem + sum over basis usage
        # basis vec expresses basis poly in originals; accumulate through qv already.
        cof = [ (-x).as_expr() for x in vec ]
        return rem.is_zero, cof, rem.as_expr()
