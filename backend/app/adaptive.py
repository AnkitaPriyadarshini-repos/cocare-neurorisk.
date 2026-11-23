"""Rule-based adaptive difficulty engine.

Transparent by design: every decision names the rule that fired and the
numbers that triggered it, and is stored in the adaptation_log table.

Levels run from 1 (easiest) to 5 (hardest). Each game turns a level into
concrete game settings via GAME_LEVELS.
"""
from dataclasses import dataclass, asdict
from statistics import median

MIN_LEVEL, MAX_LEVEL = 1, 5

# What each level means for each game (index 0 = level 1).
GAME_LEVELS = {
    # Flip cards to find matching pairs. Cards are shown face-up first.
    "memory_match": {
        "pairs":      [3, 4, 5, 6, 8],
        "preview_ms": [5000, 4000, 3000, 2500, 2000],
    },
    # Look at some pictures, then pick them out from a larger set.
    "picture_recall": {
        "show_count": [2, 3, 4, 5, 6],
        "option_count": [4, 6, 8, 9, 12],
        "display_ms": [6000, 6000, 5000, 5000, 4000],
        "rounds": [3, 3, 3, 3, 3],
    },
    # A target picture is named; find it in a grid.
    "find_it": {
        "grid_size": [4, 6, 9, 12, 16],
        "time_limit_ms": [15000, 12000, 10000, 9000, 8000],
        "rounds": [5, 5, 5, 5, 5],
    },
}

# Thresholds per game. Memory-match accuracy is naturally lower (pairs/flips),
# so it gets lower thresholds.
THRESHOLDS = {
    "memory_match":   {"up_acc": 0.70, "down_acc": 0.40, "target_rt_ms": 4000},
    "picture_recall": {"up_acc": 0.85, "down_acc": 0.50, "target_rt_ms": 5000},
    "find_it":        {"up_acc": 0.85, "down_acc": 0.50, "target_rt_ms": 6000},
}
SLOW_FACTOR = 1.5          # "struggling" = response time this many times slower than target
STRUGGLE_ACC = 0.70        # ...combined with accuracy below this


@dataclass
class Metrics:
    n_attempts: int
    accuracy: float
    median_rt_ms: float
    completed: bool


@dataclass
class Decision:
    old_level: int
    new_level: int
    rule: str
    reason: str             # technical explanation (for caregiver / researcher)
    message_key: str        # friendly message key for the elderly user ('level_up' / 'level_down' / 'level_same')


def compute_metrics(attempts: list[dict], completed: bool) -> Metrics:
    n = len(attempts)
    if n == 0:
        return Metrics(0, 0.0, 0.0, completed)
    acc = sum(1 for a in attempts if a["correct"]) / n
    rt = median(a["response_ms"] for a in attempts)
    return Metrics(n, round(acc, 3), float(rt), completed)


def params_for(game: str, level: int) -> dict:
    table = GAME_LEVELS[game]
    return {k: v[level - 1] for k, v in table.items()}


def decide(game: str, level: int, m: Metrics, mode: str = "adaptive") -> Decision:
    """Apply the rules in order; the first rule that matches wins."""
    t = THRESHOLDS[game]
    acc_pct = f"{m.accuracy:.0%}"
    rt_s = f"{m.median_rt_ms / 1000:.1f}s"
    target_s = f"{t['target_rt_ms'] / 1000:.1f}s"

    def make(new_level: int, rule: str, reason: str) -> Decision:
        new_level = max(MIN_LEVEL, min(MAX_LEVEL, new_level))
        if new_level > level:
            key = "level_up"
        elif new_level < level:
            key = "level_down"
        else:
            key = "level_same"
        return Decision(level, new_level, rule, reason, key)

    if mode == "fixed":
        return make(level, "R0_FIXED_MODE", "Fixed-difficulty condition: level is never changed.")

    if not m.completed:
        return make(level - 1, "R1_ABANDONED",
                    f"Game was left before finishing: making it easier (level {level} -> {max(MIN_LEVEL, level - 1)}).")

    if m.n_attempts == 0:
        return make(level, "R_NO_DATA", "No responses recorded: level unchanged.")

    if m.accuracy < t["down_acc"]:
        return make(level - 1, "R2_LOW_ACCURACY",
                    f"Accuracy {acc_pct} is below {t['down_acc']:.0%}: making it easier.")

    if m.accuracy < STRUGGLE_ACC and m.median_rt_ms > SLOW_FACTOR * t["target_rt_ms"]:
        return make(level - 1, "R3_STRUGGLING",
                    f"Accuracy {acc_pct} with slow responses ({rt_s} vs target {target_s}): making it easier.")

    if m.accuracy >= t["up_acc"] and m.median_rt_ms <= t["target_rt_ms"]:
        if level == MAX_LEVEL:
            return make(level, "R4_UP_AT_MAX", f"Accuracy {acc_pct} and response {rt_s}: already at the highest level.")
        return make(level + 1, "R4_HIGH_PERFORMANCE",
                    f"Accuracy {acc_pct} (>= {t['up_acc']:.0%}) and median response {rt_s} (<= {target_s}): making it harder.")

    return make(level, "R5_KEEP",
                f"Accuracy {acc_pct}, median response {rt_s}: within the comfortable range, level unchanged.")


def decision_dict(d: Decision) -> dict:
    return asdict(d)
