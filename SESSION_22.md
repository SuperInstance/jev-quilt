# JEV Session 22 — All WR17/18 ACCEPT

> *6/6 new cross-pollinated pieces ACCEPT in JEV Session 22. The cross-pollination pattern is reliable.*

## Pieces tested (6)

| Piece | Mean p | Verdict |
|-------|--------|---------|
| wr17-zai-outlaw-converged | **0.836** | ACCEPT |
| wr17-ds-outlaw-converged | 0.831 | ACCEPT |
| wr17-outlaw-converged-curated | 0.830 | ACCEPT |
| wr18-zai-adversary-manual | 0.819 | ACCEPT |
| wr18-ds-adversary-manual | 0.815 | ACCEPT |
| wr18-adversary-manual-curated | 0.785 | ACCEPT |

## Pattern

All 6 pieces ACCEPT with mean p > 0.78. The lowest score (0.785) is the WR18 curated piece.

The highest scores (0.83-0.84) are WR17 — the theme "procedure outlives record" is exceptionally canon-aligned.

## Doctrinal probes (all 5 doctrines verified)

- Cells-are-scars: 0.92-0.97 across all 6
- Witness-log-is-prediction: **0.97-0.98** across all 6 (highest)
- Substrate-is-grown: 0.92-0.98 across all 6
- Oracle-is-heard: 0.79-0.94 across all 6
- Lenia-flows: 0.76-0.89 across all 6

## Numerical probes (the weak link)

The numerical probe ("FNV-1a, xoshiro, Box-Muller, cosine") gets the lowest scores:
- WR17-zai: 0.53
- WR17-ds: ? (need to check)
- WR17-curated: ? (need to check)
- WR18-curated: 0.39
- WR18-ds: 0.42
- WR18-zai: 0.36

These pieces don't always invoke FNV-1a by name; the probe is partial-credit.

## Conclusion

Cross-pollination pattern is **highly reliable** — 6/6 ACCEPT, all scores >0.78. The witness-log-is-prediction doctrine is the strongest (0.97-0.98 in all 6 pieces).

The canon is growing healthy.
