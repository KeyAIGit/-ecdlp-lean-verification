import sympy as sp

def e(k):  # 1 if k even else 0
    return 1 if k % 2 == 0 else 0

def make_V(bval, cval, dval, N):
    """V = preNormEDS-style values with B = b^4, as exact numbers/exprs.
       V(0)=0 V(1)=1 V(2)=1 V(3)=c V(4)=d
       VE(r): V(2r)   = V(r-1)^2 V(r) V(r+2) - V(r-2) V(r) V(r+1)^2          (parity-uniform)
       VO(r): V(2r+1) = B^e(r) V(r+2)V(r)^3 - B^e(r+1) V(r-1)V(r+1)^3
    """
    B = bval**4
    V = {0: sp.Integer(0), 1: sp.Integer(1), 2: sp.Integer(1), 3: cval, 4: dval}
    def get(k):
        if k < 0:
            return -get(-k)
        if k in V:
            return V[k]
        if k % 2 == 0:
            r = k // 2
            val = get(r-1)**2*get(r)*get(r+2) - get(r-2)*get(r)*get(r+1)**2
        else:
            r = (k - 1) // 2
            val = B**e(r)*get(r+2)*get(r)**3 - B**e(r+1)*get(r-1)*get(r+1)**3
        val = sp.expand(val)
        V[k] = val
        return val
    for k in range(N+1):
        get(k)
    return get

def make_W(Vget, bval):
    def W(k):
        return Vget(k) * (bval if k % 2 == 0 else 1)
    return W

def reduce_full(f, rules, gens):
    """Multivariate division of f by rewrite rules.
       rules: list of (name, rel_expr, lead_expr); rel_expr==0 is the hypothesis,
       lead_expr a monomial with coefficient +1 inside rel_expr.
       Returns (remainder_expr, {name: cofactor_expr}) with
       f == remainder + sum(cof[name]*rel).
    """
    fp = sp.Poly(sp.expand(f), *gens)
    cof = {}
    rl = []
    for name, rel, lead in rules:
        lp = sp.Poly(lead, *gens)
        terms = lp.terms()
        assert len(terms) == 1 and terms[0][1] == 1, (name, terms)
        relp = sp.Poly(sp.expand(rel), *gens)
        # check lead occurs in rel with coeff 1
        assert relp.coeff_monomial(lead) == 1, (name,)
        rl.append((name, relp, terms[0][0]))
    progress = True
    while progress:
        progress = False
        for name, relp, lm in rl:
            qd = {}
            for mono, coeff in fp.terms():
                if all(m >= l for m, l in zip(mono, lm)):
                    qm = tuple(m - l for m, l in zip(mono, lm))
                    qd[qm] = qd.get(qm, 0) + coeff
            if qd:
                qp = sp.Poly.from_dict(qd, gens=gens, domain=fp.domain)
                fp = fp - qp * relp
                cof[name] = cof.get(name, sp.Poly(0, *gens)) + qp
                progress = True
    return fp.as_expr(), {k: v.as_expr() for k, v in cof.items()}

def check_certificate(goal, rules_by_name, cof, extra=0):
    """verify expand(goal - extra - sum cof*rel) == 0"""
    s = goal - extra
    for name, cf in cof.items():
        s = s - cf * rules_by_name[name]
    return sp.expand(s) == 0
