# jev-quilt landing pages

This directory contains self-contained HTML renderings of jev-quilt's
data, produced by [quilt-trace](https://github.com/SuperInstance/quilt-trace).

## Pages

- `jev-organism.html` — 677 receipts × 3 substrates (JEV + ARENA + JEV-Experiments)

## What this shows

The visual story of jev-quilt:
- 192 unique oracle decisions
- 475 bookkeeping sessions (the substrate's heartbeat)
- ARENA Round 1 fixtures
- 6 famous experiments (dialogue_spine, echogram, elephant, exp_brew, exp_gan, rough_seas)

## How it was built

```bash
cd /workspace/repos/quilt-director
python3 spirals/16_jev_landing.py
# → site/jev-landing.html (72KB)
# Copy to jev-quilt/docs/landing/jev-organism.html
```

## Open the page

```bash
# Local
open docs/landing/jev-organism.html

# Or serve
python3 -m http.server 8000 --directory docs/landing
# → http://localhost:8000/jev-organism.html
```

The page is fully self-contained. D3.js loads from d3js.org. No build step.
