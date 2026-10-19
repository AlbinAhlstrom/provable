"""How close one run comes to the goal: a fully working app from one kickstart and its rule tests, at 1 SEK in 120 s.

That is 100%. An app whose rules do not all pass scores 0%, whatever it cost. Over the goal, the score falls in
proportion: twice the cost halves it, and so does twice the time; under the goal counts as the goal.

    score = 100% x min(1, GOAL_SEK / cost) x min(1, GOAL_S / wall time)

The rule tests that run after a kickstart record the score of both in their summary (`goal`), since only they can
tell whether the app works. A run that replayed recorded answers paid nothing for those, so its score is not that of a
live run (`replayed` says so).
"""

from typing import Any, Dict, Optional

GOAL_SEK = 1.0
GOAL_S = 120.0
AFTER_KICKSTART = "after kickstart"  # the label of the rule tests a kickstart starts by itself


def score(valid: bool, cost_sek: Optional[float], wall_s: float) -> Optional[float]:
    """The run's share of the goal in percent; None when its cost is unknown."""
    if not valid:
        return 0.0
    if cost_sek is None:
        return None
    cost_factor = min(1.0, GOAL_SEK / cost_sek) if cost_sek > 0 else 1.0
    time_factor = min(1.0, GOAL_S / wall_s) if wall_s > 0 else 1.0
    return round(100.0 * cost_factor * time_factor, 1)


def goal(kickstart: Dict[str, Any], rule_tests: Dict[str, Any]) -> Dict[str, Any]:
    """The goal score of a kickstart and the rule tests after it, from their two summaries."""
    costs = [(s.get("llm") or {}).get("cost_sek") for s in (kickstart, rule_tests)]
    cost = None if None in costs else round(sum(costs), 4)
    wall = round(kickstart["duration_s"] + rule_tests["duration_s"], 2)
    valid = kickstart.get("status") == "ok" and rule_tests.get("status") == "ok"
    return {"kickstart": kickstart["id"], "valid": valid, "cost_sek": cost, "wall_s": wall,
            "score_pct": score(valid, cost, wall), "goal": {"cost_sek": GOAL_SEK, "wall_s": GOAL_S},
            "replayed": any((s.get("llm") or {}).get("replayed") for s in (kickstart, rule_tests))}
