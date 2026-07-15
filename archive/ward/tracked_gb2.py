import sympy as sp
from sympy.polys.orderings import grevlex

def _lt(p):
    return max(p.terms(), key=lambda t: grevlex(t[0]))

def _div_mono(m1, m2):
    q = tuple(a-b for a, b in zip(m1, m2))
    return q if all(x >= 0 for x in q) else None

def _mono_poly(mono, coeff, gens, dom):
    return sp.Poly.from_dict({mono: coeff}, gens=gens, domain=dom)

class TrackedGB:
    def __init__(self, gens_exprs, gens, maxiter=20000):
        self.gens = tuple(gens); self.dom = sp.QQ
        n = len(gens_exprs)
        self.basis = []
        for i, g in enumerate(gens_exprs):
            p = sp.Poly(sp.expand(g), *self.gens, domain=self.dom)
            vec = {i: sp.Poly(1, *self.gens, domain=self.dom)}
            m, cLT = _lt(p)
            self.basis.append((p, vec))
        self._buchberger(maxiter)

    def _reduce(self, p, vec):
        rem = sp.Poly(0, *self.gens, domain=self.dom)
        while not p.is_zero:
            mono, coeff = _lt(p)
            hit = False
            for q, qv in self.basis:
                qm, qc = _lt(q)
                dm = _div_mono(mono, qm)
                if dm is not None:
                    f = _mono_poly(dm, coeff/qc, self.gens, self.dom)
                    p = p - f*q
                    for k_, cf_ in qv.items():
                        vec[k_] = vec.get(k_, sp.Poly(0, *self.gens, domain=self.dom)) - f*cf_
                    hit = True
                    break
            if not hit:
                t = _mono_poly(mono, coeff, self.gens, self.dom)
                rem = rem + t; p = p - t
        return rem, vec

    def _buchberger(self, maxiter):
        import itertools, heapq
        def lcm_deg(i, j):
            mi, _ = _lt(self.basis[i][0]); mj, _ = _lt(self.basis[j][0])
            l = tuple(max(a,b) for a,b in zip(mi,mj))
            return sum(l)
        pairs = [(lcm_deg(i,j), i, j) for i, j in itertools.combinations(range(len(self.basis)), 2)]
        heapq.heapify(pairs)
        it = 0
        while pairs:
            it += 1
            if it > maxiter: raise RuntimeError("cap")
            _, i, j = heapq.heappop(pairs)
            pi, vi = self.basis[i]; pj, vj = self.basis[j]
            mi, ci = _lt(pi); mj, cj = _lt(pj)
            lcm = tuple(max(a,b) for a,b in zip(mi,mj))
            if tuple(a+b for a,b in zip(mi,mj)) == lcm: continue
            fi = _mono_poly(_div_mono(lcm, mi), 1/ci, self.gens, self.dom)
            fj = _mono_poly(_div_mono(lcm, mj), 1/cj, self.gens, self.dom)
            spol = fi*pi - fj*pj
            sv = {}
            for k_, cf_ in vi.items(): sv[k_] = sv.get(k_, sp.Poly(0, *self.gens, domain=self.dom)) + fi*cf_
            for k_, cf_ in vj.items(): sv[k_] = sv.get(k_, sp.Poly(0, *self.gens, domain=self.dom)) - fj*cf_
            rem, rv = self._reduce(spol, sv)
            if not rem.is_zero:
                k = len(self.basis)
                self.basis.append((rem, rv))
                for x in range(k):
                    heapq.heappush(pairs, (lcm_deg(x, k), x, k))

    def express(self, f):
        p = sp.Poly(sp.expand(f), *self.gens, domain=self.dom)
        rem, vec = self._reduce(p, {})
        cof = {}
        for _, bvec in [(None, None)]:
            pass
        # vec maps original-generator index -> Poly (negated contribution)
        cof = {k_: (-cf_).as_expr() for k_, cf_ in vec.items() if not cf_.is_zero}
        return rem.is_zero, cof, rem.as_expr()
