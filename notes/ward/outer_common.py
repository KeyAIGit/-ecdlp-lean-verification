import sympy as sp, time
from eds_common import e, reduce_full
from vmachine import B, c, d, vsmall, VE_expr, VO_expr, window_rules
from tracked_gb2 import TrackedGB

def mk(fam, rng):
    return {j: sp.Symbol(f'{fam}{j}'.replace('-','m')) for j in rng}

def pairing_rules(P, Q, A, T, par_s, par_t, Prng, Qrng):
    rules = []
    for a in Prng:
        for b_ in Qrng:
            if (a+b_) % 2 == 0:
                i = (a+b_)//2; j = (a-b_)//2
                al = e(par_s+i+1)*e(par_t+j); be = e(par_s+i)*e(par_t+j+1)
                rhs = B**al*A[i+1]*A[i-1]*T[j]**2 - B**be*T[j+1]*T[j-1]*A[i]**2
                name = f"VStar1(s{i:+d},t{j:+d})"
            else:
                i = (a+b_-1)//2; j = (a-b_-1)//2
                rhs = T[j+1]*T[j]*A[i+2]*A[i-1] - T[j+2]*T[j-1]*A[i+1]*A[i]
                name = f"VStarOdd(s{i:+d},t{j:+d})"
            rules.append((name, sp.expand(P[a]*Q[b_] - rhs), P[a]*Q[b_]))
    return rules

def run_case(tag, E, P, Q, A, T, par_s, par_t, Prng, Qrng, Awin, Twin):
    t0 = time.time()
    prules = pairing_rules(P, Q, A, T, par_s, par_t, Prng, Qrng)
    arules = [(n_.replace('(t','(s'), r_, l_) for n_, r_, l_ in window_rules(A, Awin, par_s,
              {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})]
    trules = window_rules(T, Twin, par_t, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
    allrules = prules + arules + trules
    gens = [P[a] for a in Prng] + [Q[b_] for b_ in Qrng] + [A[i] for i in Awin] + [T[j] for j in Twin] + [B, c, d]
    rem1, cof1 = reduce_full(sp.expand(E), allrules, gens)
    names = [n_ for n_, _, _ in allrules]; exprs = [r_ for _, r_, _ in allrules]
    total = {n_: sp.expand(cof1.get(n_, 0)) for n_ in names}
    nt = 0 if rem1 == 0 else len(sp.Poly(rem1, *gens).terms())
    print(f"\n=== {tag}: greedy left {nt} terms ({time.time()-t0:.0f}s)", flush=True)
    ok = (rem1 == 0)
    if not ok:
        rem = rem1
        for wtag, rls, win, vv, pp in [("A", arules, Awin, A, par_s), ("T", trules, Twin, T, par_t)]:
            if rem == 0: break
            rsyms = rem.free_symbols
            Jsub = [j for j in win if vv[j] in rsyms]
            if not Jsub: continue
            Jsub = list(range(min(Jsub), max(Jsub)+1))
            subrules = window_rules(vv, Jsub, pp, {'VS': True, 'VSl3': True, 'VG3': True, 'VSlOdd3': True})
            if wtag == "A":
                subrules = [(n_.replace('(t','(s'), r_, l_) for n_, r_, l_ in subrules]
            if not subrules: continue
            sgens = [vv[j] for j in Jsub] + [B, c, d]
            # tail may involve BOTH windows' symbols; GB is per-window so treat other window symbols
            # as coefficients: impossible with Poly domain QQ -> use all gens for Poly, rules only sub.
            fullg = [A[i] for i in Awin] + [T[j] for j in Twin] + [B, c, d]
            gb = TrackedGB([r_ for _, r_, _ in subrules], fullg)
            okk, cof2, rem = gb.express(rem)
            print(f"   {wtag}-window GB pass ({time.time()-t0:.0f}s): now rem terms = "
                  f"{0 if rem==0 else len(sp.Poly(rem,*gens).terms())}", flush=True)
            snames = [n_ for n_, _, _ in subrules]
            for k_, cf_ in cof2.items():
                nm = snames[k_]
                if nm not in total:
                    total[nm] = 0; names.append(nm); exprs.append(subrules[k_][1])
                total[nm] = sp.expand(total[nm] + cf_)
            rem = rem if rem == 0 else sp.expand(rem)
        ok = (rem == 0)
        if not ok:
            print("   FINAL residue (factored):", sp.factor(rem), flush=True)
            return
    s = E - sum(total[n_]*ex for n_, ex in zip(names, exprs))
    print("   exact recheck:", sp.expand(s) == 0, flush=True)
    for n_ in names:
        cf = total.get(n_, 0)
        if cf != 0:
            pol = sp.Poly(cf, *gens)
            isint = all(sp.Rational(x).q == 1 for x in pol.coeffs())
            print(f"   [{n_}] * ({sp.factor(cf)})   int={isint}", flush=True)
