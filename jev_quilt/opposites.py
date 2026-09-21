"""Canonical opposites: the substrate's polarity table (spring from
SuperInstance/substrate-opposites, Mavis 2026-09-20), plus the quilt's
own pairs. Opposite(name) is exact and total: unknown names map to
GAP — the honest opposite of an unnamed thing is a named absence.

Notable: the substrate counts JEV <-> JEPA as a canonical pair. Our two
mirrors (readings/imagine) are that pair in operational form.
"""

TABLE: dict[str, str] = {
    # substrate-native (verbatim from substrate-opposites)
    "witness": "forget", "forget": "witness",
    "proof": "gap", "gap": "proof",
    "bind": "fork", "fork": "bind",
    "tick": "break", "break": "tick",
    "jev": "jepa", "jepa": "jev",
    "link": "sever", "sever": "link",
    # quilt-native pairs, same law
    "sense": "act", "act": "sense",
    "wake": "sleep", "sleep": "wake",
    "calm": "alarm", "alarm": "calm",
    "predict": "surprise", "surprise": "predict",
    "commit": "refuse", "refuse": "commit",
    "memory": "imagination", "imagination": "memory",
    "ensemble": "monad", "monad": "ensemble",
}

GAP = "gap"


def opposite(name: str) -> str:
    """Total function: known names invert, unknown names become GAP."""
    return TABLE.get(name.strip().lower(), GAP)


def is_canonical(name: str) -> bool:
    return name.strip().lower() in TABLE
