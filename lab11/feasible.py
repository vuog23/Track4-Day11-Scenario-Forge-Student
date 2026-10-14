"""Part B: physics check. TODO 3."""
from __future__ import annotations

import math

G = 9.81


def is_feasible(p: dict) -> bool:
    """Reject scenarios that violate the simulator's physical feasibility limits."""
    mu = float(p["mu"])
    cut_dur = float(p["cutDur"])
    lateral_accel = (math.pi / cut_dur) ** 2 * 3.5 / 2.0
    grip = mu * G
    return bool(
        lateral_accel <= grip
        and float(p["cutBrake"]) <= grip
        and float(p["pedV"]) <= 2.5
        and 0.0 < float(p["cutV"]) <= 22.0
    )