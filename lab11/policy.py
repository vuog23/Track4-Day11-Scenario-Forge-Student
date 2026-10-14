"""Part E: choose a policy honestly. TODO 10."""
from __future__ import annotations


def choose_policy(table: list[dict], baseline_progress: float, max_loss: float = 0.05):
    """Choose the lowest-failure-bound policy that retains enough baseline progress."""
    minimum_progress = (1.0 - max_loss) * baseline_progress
    eligible = [row for row in table if row["progress"] >= minimum_progress]
    if not eligible:
        return None
    return min(eligible, key=lambda row: (row["fail_hi"], -row["progress"]))