# ARC-22

**ARC-22** — structural analysis tool for undeciphered scripts.

Originally proposed as a hypothesis about the Voynich Manuscript. The name **ARC-22** (Algorithmic Register Compiler) is historical: it reflects the original hypothesis that the manuscript is a register (Register), compiled from a four-slot matrix (Compiler). In the current work, ARC-22 is used as a **structural analysis tool**, not as a decipherment. The literal meaning of the name (Register, Compiler) is not confirmed. The name is retained as a project identifier; the interpretation of R and C is an open question.

## Repository contents

| File | Description | Status |
| --- | --- | --- |
| `arc22.py` | Core parser + base metrics (CR, E3, E6, H₂, LZ77) | stable |
| `scorecard.py` | Multi-metric structural analyzer (adds V, NS, CV²) | **draft** |
| `field.py` | Generator of the "real minus one property" field (C1–C7) | **draft** |
| `requirements.txt` | No dependencies | —   |
| `LICENSE` | MIT | —   |

## arc22.py — base parser

Four-slot token model:

```
Token = [Prefix] → [Gallows] → [Kernel] → [Suffix]
```

Key functions:

- `clean_zl_line(line)` — IVTFF cleanup
- `parse_token(token)` — four-slot parsing
- `compliance_rate(tokens)` — CR + E3 + E6
- `char_entropy(tokens, n)` — H_n
- `h2_bpc(tokens)` — H₂ in bits per character
- `lz77_ratio(tokens)` — zlib compression ratio
- `load_corpus(path)` — read ZL3b / IVTFF-flat
- `load_generated(path)` — same for generated corpora
- `print_metrics(label, tokens)` — formatted output

### Base results (ZL3b, real)

| Metric | Value |
| --- | --- |
| CR  | 63.96% |
| E3  | 0.00% |
| E6  | 36.04% |
| H₂ (BPC) | 1.1133 |
| LZ77 | 0.3107 |

## scorecard.py — multi-metric analyzer (draft)

Imports `arc22.py` as-is; does not modify it. Adds three metrics on top of the base set:

- **Positional Cramér's V** — association between slot and token position
- **Non-stationarity ratio (NS)** — drift of CR across document windows
- **Burstiness CV²** — clustering of token occurrences

Public API:

```python
from scorecard import scorecard, scorecard_many

report = scorecard("voynich_zl3b.txt", label="real_ZL3b")
scorecard_many([("file1.txt", "label1"), ("file2.txt", "label2")])
```

**Status: draft version.** Will be refined after the four-slot paradigm is left behind.

## field.py — "real minus one property" field (draft)

Generates seven corpora derived from `voynich_zl3b.txt`, each obtained by removing exactly one structural property:

| Corpus | Removed property |
| --- | --- |
| C1_shuffle_tokens | token order |
| C2_shuffle_lines | line order |
| C3_random_suffixes | specific suffix |
| C4_drop_prefixes | prefix slot |
| C5_drop_gallows | gallows slot |
| C6_random_kernels | specific kernel |
| C7_halves | (control — copy of real) |

`C7_halves` is a copy of the source and serves as a pipeline purity check.

**Status: draft version.** Will be refined together with `scorecard.py`.

### Reproducing the field

Requirements:

1. `voynich_zl3b.txt` — available at Hugging Face: `Ched-ai/voynich-eva`
2. `arc22.py`, `field.py`, `scorecard.py` — this repository

Steps:

```bash
python field.py            # generates field/C1...C7.txt
python scorecard.py field/C1_shuffle_tokens.txt C1
```

Deterministic: seed = 42.

## Field results (summary)

| label | CR% | V   | NS  | trend | CV² |
| --- | --- | --- | --- | --- | --- |
| real_ZL3b | 63.96 | 0.0245 | 0.1410 | −0.70689 | 1.6467 |
| real_Takahashi | 61.72 | 0.0226 | 0.1532 | −0.44281 | 1.6425 |
| timm | 59.98 | 0.0410 | 0.3196 | −0.58754 | 2.0274 |
| markov | 45.83 | 0.0112 | 0.1405 | +0.02590 | 0.8085 |
| scg22 | 27.02 | 0.0354 | 1.4313 | −4.29729 | 1.0368 |
| C1_shuffle_tokens | 63.96 | 0.0065 | 0.0645 | −0.14779 | 0.7978 |
| C2_shuffle_lines | 63.96 | 0.0056 | 0.0372 | +0.04718 | 0.8163 |
| C3_random_suffixes | 62.34 | 0.0230 | 0.1225 | −0.64702 | 1.0981 |
| C4_drop_prefixes | 67.94 | 0.0545 | 0.1294 | −0.76885 | 1.6380 |
| C5_drop_gallows | 64.90 | 0.0252 | 0.1435 | −0.78344 | 1.6902 |
| C6_random_kernels | 97.78 | 0.0181 | 0.0093 | −0.09628 | 0.9001 |
| C7_halves | 63.96 | 0.0245 | 0.1410 | −0.70689 | 1.6467 |

Key observations:

- **C7 == real** — pipeline purity confirmed.
- **CR is blind to token order** (C1) and **tautological** (C6: random kernels → CR = 97.78%).
- **V, NS, CV² capture what CR does not** (C1, C2, C3, C5).
- Removing a slot (C4, C5) **increases** CR — a structural defect of `parse_token`.

## Data sources

- **Hugging Face:** `Ched-ai/voynich-eva` (ZL3b transcription)
- **voynich.nu:** `IT2a-n.txt` (Takahashi transcription)

## Publications

| #   | Title | DOI |
| --- | --- | --- |
| 1   | Architecture and Statistical Verification of ARC-22 | 10.6084/m9.figshare.34003689 |
| 2   | Explicit Domain Translation and Morphological Parsing | 10.6084/m9.figshare.34003749 |
| 3   | Critical Analysis and Correction Plan for ARC-22 | 10.6084/m9.figshare.34013346 |
| 4   | Addendum: Reproducibility Test Results | 10.6084/m9.figshare.34016907 |
| 5   | ReenKuul/arc22 — code release (2026-09-28) | 10.6084/m9.figshare.34018395 |

## ORCID

[0009-0007-3223-5946](https://orcid.org/0009-0007-3223-5946)

## License

MIT
