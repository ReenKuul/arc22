# scorecard.py
# ARC-22 Scorecard — multi-metric structural detector.
# Version 0.2 (2026-09-29). Imports arc22.py v3 without modification.
# Fix: compliance_rate returns dict; parse_token returns dict; CR already in %.

import math
from collections import defaultdict

import arc22


def _slot_of(token):
    p = arc22.parse_token(token)
    return {
        "P": p.get("prefix") or "",
        "G": p.get("gallows") or "",
        "K": p.get("kernel") or "",
        "S": p.get("suffix") or "",
    }


def _cramers_v(table):
    r = len(table)
    c = len(table[0])
    n = sum(sum(row) for row in table)
    if n == 0 or r < 2 or c < 2:
        return 0.0
    row_tot = [sum(row) for row in table]
    col_tot = [sum(table[i][j] for i in range(r)) for j in range(c)]
    chi2 = 0.0
    for i in range(r):
        for j in range(c):
            e = row_tot[i] * col_tot[j] / n
            if e > 0:
                chi2 += (table[i][j] - e) ** 2 / e
    return math.sqrt(chi2 / (n * min(r - 1, c - 1)))


def positional_cramers_v(tokens, n_bins=10):
    n = len(tokens)
    if n == 0:
        return {"V_overall": 0.0, "V_P": 0.0, "V_G": 0.0, "V_K": 0.0, "V_S": 0.0}
    bin_size = max(1, n // n_bins)
    slot_names = ["P", "G", "K", "S"]
    overall = [[0] * n_bins for _ in range(4)]
    per_slot = {s: [[0] * n_bins for _ in range(2)] for s in slot_names}
    for idx, tok in enumerate(tokens):
        b = min(idx // bin_size, n_bins - 1)
        slots = _slot_of(tok)
        for si, s in enumerate(slot_names):
            present = 1 if slots[s] else 0
            if present:
                overall[si][b] += 1
            per_slot[s][present][b] += 1
    result = {"V_overall": _cramers_v(overall)}
    for s in slot_names:
        result["V_" + s] = _cramers_v(per_slot[s])
    return result


def non_stationarity(tokens, k=10):
    n = len(tokens)
    if n == 0 or k < 2:
        return {"NS": 0.0, "trend": 0.0, "CR_windows": []}
    win = max(1, n // k)
    crs = []
    for i in range(k):
        lo = i * win
        hi = n if i == k - 1 else (i + 1) * win
        chunk = tokens[lo:hi]
        if not chunk:
            continue
        cr = arc22.compliance_rate(chunk)["CR"]
        crs.append(cr)
    if not crs:
        return {"NS": 0.0, "trend": 0.0, "CR_windows": []}
    mean_cr = sum(crs) / len(crs)
    ns = (max(crs) - min(crs)) / mean_cr if mean_cr > 0 else 0.0
    m = len(crs)
    xs = list(range(m))
    mx = sum(xs) / m
    my = mean_cr
    num = sum((xs[i] - mx) * (crs[i] - my) for i in range(m))
    den = sum((xs[i] - mx) ** 2 for i in range(m))
    trend = num / den if den > 0 else 0.0
    return {"NS": ns, "trend": trend, "CR_windows": crs}


def burstiness_cv2(tokens, min_freq=5):
    positions = defaultdict(list)
    for i, tok in enumerate(tokens):
        positions[tok].append(i)
    cvs = []
    for tok, pos in positions.items():
        if len(pos) < min_freq:
            continue
        gaps = [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]
        if not gaps:
            continue
        mg = sum(gaps) / len(gaps)
        if mg == 0:
            continue
        var = sum((g - mg) ** 2 for g in gaps) / len(gaps)
        cvs.append(var / (mg * mg))
    if not cvs:
        return {"CV2_mean": 0.0, "CV2_median": 0.0, "n_tokens": 0}
    cvs.sort()
    med = cvs[len(cvs) // 2] if len(cvs) % 2 else (cvs[len(cvs) // 2 - 1] + cvs[len(cvs) // 2]) / 2
    return {"CV2_mean": sum(cvs) / len(cvs), "CV2_median": med, "n_tokens": len(cvs)}


def scorecard(path, label=None, k_windows=10, n_bins=10, min_freq=5):
    tokens = arc22.load_corpus(path)
    if label is None:
        label = path
    cr_dict = arc22.compliance_rate(tokens)
    cr  = cr_dict["CR"]
    e3  = cr_dict["E3"]
    e6  = cr_dict["E6"]
    h2  = arc22.h2_bpc(tokens)
    lz  = arc22.lz77_ratio(tokens)
    v   = positional_cramers_v(tokens, n_bins=n_bins)
    ns  = non_stationarity(tokens, k=k_windows)
    bu  = burstiness_cv2(tokens, min_freq=min_freq)
    report = {
        "label": label,
        "n_tokens": len(tokens),
        "CR": cr, "E3": e3, "E6": e6,
        "H2": h2, "LZ77": lz,
        "V_overall": v["V_overall"],
        "V_P": v["V_P"], "V_G": v["V_G"], "V_K": v["V_K"], "V_S": v["V_S"],
        "NS": ns["NS"], "trend": ns["trend"],
        "CV2_mean": bu["CV2_mean"], "CV2_median": bu["CV2_median"],
    }
    return report


def print_report(r):
    print(f"=== {r['label']} ===")
    print(f"tokens          : {r['n_tokens']}")
    print(f"CR              : {r['CR']:.2f}%")
    print(f"E3              : {r['E3']:.2f}%")
    print(f"E6              : {r['E6']:.2f}%")
    print(f"H2 (BPC)        : {r['H2']:.4f}")
    print(f"LZ77            : {r['LZ77']:.4f}")
    print(f"V (overall)     : {r['V_overall']:.4f}")
    print(f"V_P/G/K/S       : {r['V_P']:.4f} / {r['V_G']:.4f} / {r['V_K']:.4f} / {r['V_S']:.4f}")
    print(f"NS (non-stat.)  : {r['NS']:.4f}   trend: {r['trend']:+.5f}")
    print(f"CV2 mean/median : {r['CV2_mean']:.4f} / {r['CV2_median']:.4f}")
    print()


def scorecard_many(items):
    reports = []
    for path, label in items:
        r = scorecard(path, label=label)
        print_report(r)
        reports.append(r)
    print("=== SUMMARY ===")
    hdr = f"{'label':<20}{'CR%':>8}{'V':>8}{'NS':>8}{'trend':>10}{'CV2':>8}"
    print(hdr)
    for r in reports:
        print(f"{r['label']:<20}{r['CR']:>8.2f}{r['V_overall']:>8.4f}"
              f"{r['NS']:>8.4f}{r['trend']:>+10.5f}{r['CV2_mean']:>8.4f}")
    return reports
