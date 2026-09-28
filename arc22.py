#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARC-22: Algorithmic Register Compiler
Parser for the Voynich Manuscript (EVA/ZL transcription).

Single specification. No version suffixes in the model name.
__version__ refers to this code implementation, not the model.
"""

__version__ = "1.0"

import re
import math
import zlib
import argparse
from collections import Counter


# ============================================================
# Спецификация ARC-22
# ============================================================

DIGRAPHS = [
    'ckh', 'cph', 'cfh', 'cth', 'ch', 'sh', 'th',
    'tch', 'kch', 'pch', 'fch'
]

PREFIXES = [
    'qo', 'o', 'd', 'y', 'cth', 'ch', 'sh'
]

GALLOWS = ['k', 't', 'p', 'f', 'T']

KERNELS = [
    'sho', 'chor', 'shol', 'chol', 'shor', 'kai', 'tai', 'ar', 'or',
    'ol', 'al', 'ed', 'ain', 'ai', 'a', 'o', 'e', 'ach', 'at',
    'ckh', 'cth', 'cph', 'cfh', 'kch', 'tch', 'pch', 'fch',
    'lk', 'ld', 'lt', 'ii',
    'ee', 'y', 'ch', 'eo', 'i', 'sh', 'eeo', 'eee'
]

SUFFIXES = [
    'aiiin', 'iin', 'edy', 'dy', 'in', 'y', 'l', 'r', 'n', 's',
    'm', 'ol', 'am', 'ys',
    'ee', 'eee', 'eo', 'eedy', 'eeedy'
]

PREFIXES_S = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES_S = sorted(SUFFIXES, key=len, reverse=True)


# ============================================================
# Очистка ZL3b (IVTFF-формат)
# ============================================================

_RE_COMMENT   = re.compile(r'<![^>]*>')
_RE_IVTFF_TAG = re.compile(r'<[^>]*>')
_RE_ALTERN    = re.compile(r'\[[^\]]*\]')
_RE_UNCERT    = re.compile(r'\{[^\}]*\}')
_RE_NON_EVA   = re.compile(r'[^a-z]')


def clean_zl_line(line):
    """
    Принимает строку ZL3b, возвращает список чистых EVA-токенов.
    Удаляет IVTFF-маркеры: <...>, <!...>, [a:b], {...}.
    """
    line = _RE_COMMENT.sub(' ', line)
    line = _RE_IVTFF_TAG.sub(' ', line)
    line = _RE_ALTERN.sub('', line)
    line = _RE_UNCERT.sub('', line)

    raw = re.split(r'[.\s,;:]+', line)
    out = []
    for t in raw:
        t = _RE_NON_EVA.sub('', t.strip().lower())
        if len(t) >= 2:
            out.append(t)
    return out


# ============================================================
# Парсер 4-слотовой матрицы
# ============================================================

def parse_token(token):
    """
    Разбор токена по матрице:
        [Prefix] -> [Gallows] -> [Kernel] -> [Suffix]

    Возвращает dict:
        {'prefix', 'gallows', 'kernel', 'suffix', 'error'}
    где error = None | 'E3' | 'E6'.
    E3 — нет ядра; E6 — ядро не входит в KERNELS.
    """
    if token in KERNELS:
        return {'prefix': None, 'gallows': None,
                'kernel': token, 'suffix': None, 'error': None}

    work = token
    prefix = suffix = gallows = None

    for p in PREFIXES_S:
        if work.startswith(p) and len(work) > len(p):
            prefix = p; work = work[len(p):]; break

    if work and work[0] in GALLOWS:
        gallows = work[0]; work = work[1:]

    for s in SUFFIXES_S:
        if work.endswith(s) and len(work) > len(s):
            suffix = s; work = work[:-len(s)]; break

    kernel = work if work else None

    if not kernel and prefix:
        work = token[len(prefix):]
        for s in SUFFIXES_S:
            if work.endswith(s) and len(work) > len(s):
                suffix = s; work = work[:-len(s)]; break
        kernel = work if work else None
        gallows = None

    error = None
    if not kernel: error = 'E3'
    elif kernel not in KERNELS: error = 'E6'

    return {'prefix': prefix, 'gallows': gallows,
            'kernel': kernel, 'suffix': suffix, 'error': error}


# ============================================================
# Метрики
# ============================================================

def compliance_rate(tokens):
    """
    CR = (total - E3 - E6) / total.
    Возвращает dict с total, compliant, CR, E3, E6.
    """
    total = len(tokens)
    if total == 0:
        return {'total': 0, 'compliant': 0,
                'CR': 0.0, 'E3': 0.0, 'E6': 0.0}
    e3 = e6 = 0
    for t in tokens:
        err = parse_token(t)['error']
        if err == 'E3': e3 += 1
        elif err == 'E6': e6 += 1
    comp = total - e3 - e6
    return {'total': total, 'compliant': comp,
            'CR': comp / total * 100.0,
            'E3': e3 / total * 100.0,
            'E6': e6 / total * 100.0}


def char_entropy(tokens, n):
    """Энтропия n-грамм символов, в битах."""
    ng = Counter(); total = 0
    for t in tokens:
        for i in range(len(t) - n + 1):
            ng[t[i:i+n]] += 1; total += 1
    if total == 0: return 0.0
    h = 0.0
    for c in ng.values():
        p = c / total; h -= p * math.log2(p)
    return h


def h2_bpc(tokens):
    """H2 в bits per character = энтропия биграмм / средняя длина токена."""
    h2 = char_entropy(tokens, 2)
    if not tokens: return 0.0
    avg_len = sum(len(t) for t in tokens) / len(tokens)
    return h2 / avg_len if avg_len > 0 else 0.0


def lz77_ratio(tokens):
    """LZ77 через zlib. Отношение сжатого к исходному."""
    text = ' '.join(tokens).encode('utf-8')
    if len(text) == 0: return 0.0
    return len(zlib.compress(text, level=6)) / len(text)


# ============================================================
# Загрузка корпуса
# ============================================================

def load_corpus(path):
    """Загружает ZL3b-файл и возвращает список токенов."""
    tokens = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('#'): continue
            tokens.extend(clean_zl_line(line))
    return tokens


def load_generated(path):
    """Загружает сгенерированный текст (пропускает шапку с #)."""
    tokens = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            tokens.extend(clean_zl_line(line))
    return tokens


# ============================================================
# Вывод
# ============================================================

def print_metrics(label, tokens):
    cr = compliance_rate(tokens)
    h2b = h2_bpc(tokens)
    lz = lz77_ratio(tokens)
    print(f"\n=== {label} ===")
    print(f"  Токенов:        {cr['total']}")
    print(f"  COMPLIANT:      {cr['compliant']}")
    print(f"  CR:             {cr['CR']:.2f}%")
    print(f"  E3:             {cr['E3']:.2f}%")
    print(f"  E6:             {cr['E6']:.2f}%")
    print(f"  H2 (BPC):       {h2b:.4f}")
    print(f"  LZ77 ratio:     {lz:.4f}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='ARC-22 parser and metrics for the Voynich Manuscript (EVA/ZL).'
    )
    parser.add_argument('--voynich', required=True,
                        help='Путь к файлу ZL3b транскрипции')
    parser.add_argument('--generated', default=None,
                        help='Путь к сгенерированному тексту (опционально)')
    args = parser.parse_args()

    voy = load_corpus(args.voynich)
    print_metrics('Полный корпус Войнича', voy)

    if args.generated:
        gen = load_generated(args.generated)
        print_metrics('Сгенерированный текст', gen)

    print("\n" + "="*55)
    print("ПРЕ-РЕГИСТРИРОВАННЫЕ ОЖИДАНИЯ")
    print("="*55)
    print("  CR Войнич:       44.38%  (± 2 п.п.)")
    print("  CR generated:    50.50%  (± 2 п.п.)")
    print("  E3 Войнич:       6.74%")
    print("  E6 Войнич:       48.88%")
    print("  E3 generated:    6.95%")
    print("  E6 generated:    42.55%")
    print("  H2 (BPC):        2.28 – 2.59")
    print("  LZ77 Войнич:     0.3641 (± 0.02)")


if __name__ == '__main__':
    main()