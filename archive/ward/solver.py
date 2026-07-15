import sympy as sp, time
from eds_common import e, reduce_full
from vmachine import B, c, d, VE_expr, VO_expr, window_rules
from tracked_gb2 import TrackedGB

_gb_cache = {}
def get_gb(key, exprs, gens):
    if key not in _gb_cache:
        t0 = time.time()
        _gb_cache[key] = TrackedGB(exprs, gens)
        print(f"   [gb {key} built {time.time()-t0:.0f}s, {len(_gb_cache[key].basis)} elems]", flush=True)
    return _gb_cache[key]

def subwindow_solve(tag, E, v, J, par_t):
    t0 = time.time()
    gens = [v[j] for j in J] + [B, c, d]
    rules = window_rules(v, J, par_t, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    names = [n_ for n_, _, _ in rules]; exprs = [r_ for _, r_, _ in rules]
    rem1, cof1 = reduce_full(sp.expand(E), rules, gens)
    total = {n_: sp.expand(cof1.get(n_, 0)) for n_ in names}
    print(f"\n=== {tag}: greedy left {0 if rem1==0 else len(sp.Poly(rem1,*gens).terms())} terms ({time.time()-t0:.0f}s)", flush=True)
    ok = (rem1 == 0)
    if not ok:
        rsyms = rem1.free_symbols
        Jsub = [j for j in J if v[j] in rsyms]
        Jsub = list(range(min(Jsub), max(Jsub)+1))
        subrules = window_rules(v, Jsub, par_t, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
        sgens = [v[j] for j in Jsub] + [B, c, d]
        key = (tuple(Jsub), par_t)
        gb = get_gb(key, [r_ for _, r_, _ in subrules], sgens)
        ok, cof2, rem2 = gb.express(rem1)
        print(f"   subwindow {Jsub} GB expressed={ok} ({time.time()-t0:.0f}s)", flush=True)
        if not ok:
            print("   residue:", sp.factor(rem2), flush=True)
            return False, None, None
        snames = [n_ for n_, _, _ in subrules]
        for k_, cf_ in cof2.items():
            nm = snames[k_]
            if nm not in total:
                total[nm] = 0; names.append(nm); exprs.append(subrules[k_][1])
            total[nm] = sp.expand(total[nm] + cf_)
    s = E - sum(total[n_]*ex for n_, ex in zip(names, exprs))
    exact = sp.expand(s) == 0
    print(f"   exact recheck: {exact}", flush=True)
    if exact:
        for n_ in names:
            cf = total.get(n_, 0)
            if cf != 0:
                pol = sp.Poly(cf, *gens)
                isint = all(sp.Rational(x).q == 1 for x in pol.coeffs())
                print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}", flush=True)
    return exact, names, total
