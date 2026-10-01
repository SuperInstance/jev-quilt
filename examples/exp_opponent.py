"""E3: Opponent cell — tendency reading vs a switching adversary.

Spring from substrate-videogame-ml OpponentAI: "learns player tendency,
plays opposite; confidence grows with observations." Exact version: a
TendencyReading counts symbols (rock/paper/scissors); the opponent cell
predicts your mode and plays the counter. Adversary switches strategy
mid-game (fixed -> mixed). Measure: prediction accuracy per window,
confidence as exact modal share, detection of the switch from accuracy drop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Q16, TendencyReading, WitnessRng, seed_from_state

RPS = ["rock", "paper", "scissors"]
BEATS = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
BEATEN_BY = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


def adversary(t: int, rng: WitnessRng) -> str:
    if t < 60:
        return "rock"                      # fixed tendency
    return rng.pick(RPS)                   # then mixed


def main(ticks: int = 120):
    obs = TendencyReading()
    rng = WitnessRng(seed_from_state({"exp": "opponent"}))
    correct, window = 0, []
    switch_seen_at = None
    for t in range(1, ticks + 1):
        their = adversary(t, rng)
        pred = obs.predict_symbol()
        play = BEATS[pred] if pred in BEATS else rng.pick(RPS)
        won = (play == BEATS[their])
        if pred is not None and their == pred:
            correct += 1
        obs.update_symbol(their)
        window.append(won)
        if t >= 60 and switch_seen_at is None and len(window) >= 20:
            recent = sum(window[-10:])
            if recent <= 3 and sum(window[-20:-10]) >= 6:
                switch_seen_at = t
    acc_pre = Q16(sum(1 for t in range(59) if True), 1)  # placeholder no
    print(f"E3 opponent: {ticks} ticks, adversary fixed->mixed at t=60")
    print(f"   tendency predictions correct (whole game): {correct}/{ticks} "
          f"= {Q16(correct, ticks)}")
    print(f"   modal confidence at end: {obs.confidence()} "
          f"counts={dict(sorted(obs.counts.items()))}")
    print(f"   switch flagged at t={switch_seen_at} "
          f"(win-rate drop detection)")


if __name__ == "__main__":
    main()
