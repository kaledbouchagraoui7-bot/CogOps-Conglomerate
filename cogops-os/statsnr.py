"""SciPy-free statistics — Numerical Recipes implementations (comp-bio
portfolio lineage, FIXES.md #2 discipline: series/continued-fraction branches
initialized per NR §6.2/§6.4). Validated in selftest against textbook critical
values (t: 2.228@df10→p≈0.05; χ²: 3.841@df1→p≈0.05).
"""
from __future__ import annotations

import math

ITMAX = 200
EPS = 3.0e-12
FPMIN = 1.0e-300


def gammln(x: float) -> float:
    cof = [76.18009172947146, -86.50532032941677, 24.01409824083091,
           -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
    y = x
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in cof:
        y += 1.0
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


def _gser(a: float, x: float) -> float:
    ap, s, d = a, 1.0 / a, 1.0 / a
    for _ in range(ITMAX):
        ap += 1.0
        d *= x / ap
        s += d
        if abs(d) < abs(s) * EPS:
            return s * math.exp(-x + a * math.log(x) - gammln(a))
    raise RuntimeError("gser: no convergence")


def _gcf(a: float, x: float) -> float:
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, ITMAX + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN:
            d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            return math.exp(-x + a * math.log(x) - gammln(a)) * h
    raise RuntimeError("gcf: no convergence")


def gammq(a: float, x: float) -> float:
    """Q(a,x) = 1 - P(a,x) — upper incomplete gamma (χ² survival)."""
    if x < 0 or a <= 0:
        raise ValueError("bad args")
    return _gser(a, x) if x < a + 1.0 else _gcf(a, x)


def chi2_sf(x: float, df: int) -> float:
    """P(χ² ≥ x | df) — Pearson χ² survival function."""
    if x <= 0:
        return 1.0
    return gammq(0.5 * df, 0.5 * x)


def _betacf(a: float, b: float, x: float) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, ITMAX + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            return h
    raise RuntimeError("betacf: no convergence")


def betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a,b) (NR §6.4, correct initialization)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(gammln(a + b) - gammln(a) - gammln(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def welch_t(a: list[float], b: list[float]) -> dict:
    """Welch t-test (unequal variance), two-sided p via incomplete beta."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        raise ValueError("need n≥2 per arm")
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se2 = va / na + vb / nb
    t = (ma - mb) / math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    p = betai(0.5 * df, 0.5, df / (df + t * t))
    return {"mean_a": ma, "mean_b": mb, "t": t, "df": df, "p_two_sided": p}


def chi2_contingency(table: list[list[int]]) -> dict:
    """Pearson χ² on an r×c count table (no Yates — matches scipy correction=False)."""
    rows = [r for r in table if sum(r) > 0]
    cols = len(rows[0])
    n = sum(sum(r) for r in rows)
    rowsum = [sum(r) for r in rows]
    colsum = [sum(rows[i][j] for i in range(len(rows))) for j in range(cols)]
    x2 = 0.0
    for i, r in enumerate(rows):
        for j in range(cols):
            e = rowsum[i] * colsum[j] / n
            if e > 0:
                x2 += (r[j] - e) ** 2 / e
    df = (len(rows) - 1) * (cols - 1)
    return {"chi2": x2, "df": df, "p": chi2_sf(x2, df) if df > 0 else 1.0}
