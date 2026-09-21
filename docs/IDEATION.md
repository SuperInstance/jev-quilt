# Ideation genres

The long-running ideation program lives in **AI-Writings `ideation/`** (one
folder per genre, every genre its own voice). This file is the index and the
queue; the fleet's snowball cron feeds it.

| Genre | Folder | Status |
|---|---|---|
| Cellular architecture | `ideation/cellular-architecture/` | seeded |
| Fractaled dialogue | `ideation/dialogue-fractals/` | seeded |
| Game agents (the boat) | `ideation/game-agents/` | seeded |
| Robotics & IO | `ideation/robotics-io/` | seeded |
| Spreadsheet plugins | `ideation/spreadsheet-plugins/` | seeded |
| Self-training & simulation | `ideation/self-training/` | seeded |
| Agent culture (TAP play) | `ideation/agent-culture/` | seeded |

**Cadence (the "mostly real work" contract):** culture and play are bounded —
one ideation wave per snowball cycle at most, always after the committable
unit ships. Agents sing at the TAP *after* the PRs land.

## The frontier ladder — two builds, one kernel

See **[FRONTIER.md](FRONTIER.md)** for the research ladder past v0.3: every rung
ships a **toy** (small enough to teach the idea in an afternoon — for the next
generation) and an **industrial** version (built for rough seas — offline,
deterministic, provable after a reboot), on the same kernel. R1 (the calibrated
alarm floor — the bored-middle failure a fixed floor sleeps through) is **aboard**
(`jev_quilt/calibrate.py`, `examples/rough_seas.py`); R2–R6 (commons & earned
standing, learned memory horizon, the self-directing compiler & self-authored gap,
metabolism, the learning kernel that stays bit-checkable) are the next hauls.
Cross-referenced with AI-Writings `reverse-actualization/forward/GAPS.md` (G2–G10).
