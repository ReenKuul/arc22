# field.py
# Stage 2 (Variant C) — "real minus one property" field.
# 7 corpora derived from real_ZL3b by removing exactly one property.
# v2 (2026-09-29): load_lines now replicates arc22.clean_zl_line() exactly.
#   - _RE_NON_EVA strips non-EVA chars
#   - tokens shorter than 2 are dropped
# This guarantees C7_halves == real.

import os
import random
import re

import arc22


SEED = 42

_RE_COMMENT = re.compile(r'<![^>]*>')
_RE_IVTFF_TAG = re.compile(r'<[^>]*>')
_RE_ALTERN = re.compile(r'\[[^\]]*\]')
_RE_UNCERT = re.compile(r'\{[^\}]*\}')
_RE_NON_EVA = re.compile(r'[^a-z]')


# ---------------------------------------------------------------------------
# IO: read real corpus preserving line structure (matches arc22.clean_zl_line)
# ---------------------------------------------------------------------------

def load_lines(path):
    r"""Read IVTFF-flat file, return list of lists of tokens (per line).

    Replicates arc22.clean_zl_line() exactly:
      - replace <...>, <!...> with space
      - delete [a:b], {...}
      - split on dot, whitespace, comma, semicolon, colon
      - strip non-EVA chars, lowercase
      - drop tokens shorter than 2
    Empty lines (after cleaning) are dropped.
    """
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            line = _RE_COMMENT.sub(" ", line)
            line = _RE_IVTFF_TAG.sub(" ", line)
            line = _RE_ALTERN.sub("", line)
            line = _RE_UNCERT.sub("", line)

            raw_toks = re.split(r"[.\s,;:]+", line)
            toks = []
            for t in raw_toks:
                t = _RE_NON_EVA.sub("", t.strip().lower())
                if len(t) >= 2:
                    toks.append(t)
            if toks:
                lines.append(toks)
    return lines


def write_flat(lines, path):
    """Write list of lists of tokens as IVTFF-flat file."""
    with open(path, "w", encoding="utf-8") as f:
        for toks in lines:
            f.write(".".join(toks) + "\n")


def write_flat_tokens(tokens, path, tokens_per_line=10):
    """Write flat token list, wrapping every N tokens."""
    with open(path, "w", encoding="utf-8") as f:
        for i in range(0, len(tokens), tokens_per_line):
            chunk = tokens[i:i + tokens_per_line]
            f.write(".".join(chunk) + "\n")


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def c1_shuffle_tokens(lines, rng):
    flat = [t for line in lines for t in line]
    rng.shuffle(flat)
    out = []
    i = 0
    for line in lines:
        n = len(line)
        out.append(flat[i:i + n])
        i += n
    return out


def c2_shuffle_lines(lines, rng):
    out = [list(line) for line in lines]
    rng.shuffle(out)
    return out


def _random_suffix(rng):
    return rng.choice(arc22.SUFFIXES_S)


def c3_random_suffixes(lines, rng):
    out = []
    for line in lines:
        new_line = []
        for tok in line:
            p = arc22.parse_token(tok)
            pref = p.get("prefix") or ""
            gal  = p.get("gallows") or ""
            ker  = p.get("kernel") or ""
            if not ker:
                new_line.append(tok)
                continue
            new_line.append(pref + gal + ker + _random_suffix(rng))
        out.append(new_line)
    return out


def c4_drop_prefixes(lines, rng):
    out = []
    for line in lines:
        new_line = []
        for tok in line:
            p = arc22.parse_token(tok)
            gal = p.get("gallows") or ""
            ker = p.get("kernel") or ""
            suf = p.get("suffix") or ""
            if ker:
                new_line.append(gal + ker + suf)
            else:
                new_line.append(tok)
        out.append(new_line)
    return out


def c5_drop_gallows(lines, rng):
    out = []
    for line in lines:
        new_line = []
        for tok in line:
            p = arc22.parse_token(tok)
            pref = p.get("prefix") or ""
            ker  = p.get("kernel") or ""
            suf  = p.get("suffix") or ""
            if ker:
                new_line.append(pref + ker + suf)
            else:
                new_line.append(tok)
        out.append(new_line)
    return out


def c6_random_kernels(lines, rng):
    out = []
    for line in lines:
        new_line = []
        for tok in line:
            p = arc22.parse_token(tok)
            pref = p.get("prefix") or ""
            gal  = p.get("gallows") or ""
            suf  = p.get("suffix") or ""
            if p.get("kernel"):
                new_line.append(pref + gal + rng.choice(arc22.KERNELS) + suf)
            else:
                new_line.append(tok)
        out.append(new_line)
    return out


def c7_halves(lines, rng):
    return [list(line) for line in lines]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def generate_all(src_path, out_dir="field", seed=SEED):
    os.makedirs(out_dir, exist_ok=True)
    lines = load_lines(src_path)

    n_tok = sum(len(l) for l in lines)
    print(f"source: {src_path}")
    print(f"lines : {len(lines)}")
    print(f"tokens: {n_tok}")
    print()

    jobs = [
        ("C1_shuffle_tokens",  c1_shuffle_tokens),
        ("C2_shuffle_lines",   c2_shuffle_lines),
        ("C3_random_suffixes", c3_random_suffixes),
        ("C4_drop_prefixes",   c4_drop_prefixes),
        ("C5_drop_gallows",    c5_drop_gallows),
        ("C6_random_kernels",  c6_random_kernels),
        ("C7_halves",          c7_halves),
    ]

    paths = []
    for name, fn in jobs:
        rng_local = random.Random(seed)
        out_lines = fn(lines, rng_local)
        out_path = os.path.join(out_dir, name + ".txt")
        write_flat(out_lines, out_path)
        n_out = sum(len(l) for l in out_lines)
        print(f"{name:<22} -> {out_path}  ({n_out} tokens)")
        paths.append((out_path, name))

    return paths


if __name__ == "__main__":
    generate_all("voynich_zl3b.txt")
