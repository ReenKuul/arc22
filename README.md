# ARC-22

ARC-22 (Algorithmic Register Compiler) — parser for the Voynich Manuscript (MS 408), based on EVA/ZL transcription.

## Model

A token is parsed as a four-slot matrix:

[Prefix] → [Gallows] → [Kernel] → [Suffix]

- **DIGRAPHS:** ckh, cph, cfh, cth, ch, sh, th, tch, kch, pch, fch

- **PREFIXES:** qo, o, d, y, cth, ch, sh

- **GALLOWS:** k, t, p, f, T

- **KERNELS:** sho, chor, shol, chol, shor, kai, tai, ar, or, ol, al, ed, ain, ai, a, o, e, ach, at, ckh, cth, cph, cfh, kch, tch, pch, fch, lk, ld, lt, ii, ee, y, ch, eo, i, sh, eeo, eee

- **SUFFIXES:** aiiin, iin, edy, dy, in, y, l, r, n, s, m, ol, am, ys, ee, eee, eo, eedy, eeedy

**Errors:**
- **E3** — no kernel.
- **E6** — kernel not in KERNELS.

**Metrics:**
- **CR** — compliance rate: (total − E3 − E6) / total.
- **H₂ (BPC)** — bigram entropy divided by mean token length.
- **LZ77** — compression ratio via `zlib`.

## Usage

python arc22.py --voynich voynich_zl3b.txt --generated generated_text.txt

## Results (current implementation, version 1.0)

| Metric | Voynich | Generated |
|--------|---------|-----------|
| Tokens | 33 206 | 10 809 |
| COMPLIANT | 21 239 | 6 483 |
| CR | 63.96% | 59.98% |
| E3 | 0.00% | 0.00% |
| E6 | 36.04% | 40.02% |
| H₂ (BPC) | 1.1133 | 1.1625 |
| LZ77 | 0.3107 | 0.3068 |

**Reproducibility:** two independent runs produced identical numbers.

## Status

This implementation was used to test the reproducibility of the ARC-22 model as published in the critical paper. The reported CR values (44.38% on Voynich, 50.50% on generated text) **were not reproduced** from the published specification. See the Addendum:

- Kuul, R. (2026). *Addendum to «Critical Analysis and Correction Plan for the ARC-22 Model»: Reproducibility Test Results*. Figshare. DOI: [10.6084/m9.figshare.34016907](https://doi.org/10.6084/m9.figshare.34016907)

**The model requires substantial revision and rebuilding.**

## Related publications

1. Kuul, R. (2026). *Architecture and Statistical Verification of the ARC-22 Model*. Figshare. DOI: [10.6084/m9.figshare.34003689](https://doi.org/10.6084/m9.figshare.34003689)
2. Kuul, R. (2026). *Explicit Domain Translation and Morphological Parsing*. Figshare. DOI: [10.6084/m9.figshare.34003749](https://doi.org/10.6084/m9.figshare.34003749)
3. Kuul, R. (2026). *Critical Analysis and Correction Plan for the ARC-22 Model*. Figshare. DOI: [10.6084/m9.figshare.34013346](https://doi.org/10.6084/m9.figshare.34013346)
4. Kuul, R. (2026). *Addendum to «Critical Analysis...»: Reproducibility Test Results*. Figshare. DOI: [10.6084/m9.figshare.34016907](https://doi.org/10.6084/m9.figshare.34016907)

## Author

Reen Kuul — ORCID [0009-0007-3223-5946](https://orcid.org/0009-0007-3223-5946)

## License

MIT

