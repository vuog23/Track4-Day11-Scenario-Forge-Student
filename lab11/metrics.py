"""Part A: read a rollout. TODO 1, 2 and 9 live here; the helpers below them are given."""
from __future__ import annotations

import numpy as np

from avsim import core

G = 9.81
HALF_EGO = core.CAR[0] / 2


def ego_events(R: core.Rollout, k: int) -> list[dict]:
    """Failure events involving the ego in scenario k, earliest first."""
    return [e for e in R.events[k] if e["a"] == "ego" or e["b"] == "ego"]


def min_ttc(R: core.Rollout, cap: float = 10.0) -> np.ndarray:
    """Return each scenario's minimum TTC to its current leader, capped at cap."""
    F = R.F
    ego = F[:, :, core.IX["ego"]]
    leader_idx = R.EGO[:, :, 3].astype(int)
    has_leader = leader_idx >= 0
    safe_idx = np.clip(leader_idx, 0, F.shape[2] - 1)
    gather_idx = np.broadcast_to(safe_idx[..., None, None],
                                 (*safe_idx.shape, 1, F.shape[-1]))
    leader = np.take_along_axis(F, gather_idx, axis=2)[:, :, 0, :]

    rx = leader[..., 0] - ego[..., 0]
    rz = leader[..., 1] - ego[..., 1]
    lon = rx * ego[..., 2] + rz * ego[..., 3]
    gap = np.maximum(lon - HALF_EGO - np.where(
        core.PEDS[safe_idx], 0.3, core.LEN[safe_idx] / 2.0
    ), 0.0)
    closing_speed = ego[..., 4] - leader[..., 4]
    closing = has_leader & (closing_speed > 0.1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ttc = np.where(closing, gap / np.maximum(closing_speed, 1e-12), cap)
    result = np.minimum(cap, np.min(ttc, axis=1))
    for k in range(R.K):
        if ego_events(R, k):
            result[k] = 0.0
    return result


def contact_type(R: core.Rollout, k: int, event: dict) -> str:
    """Classify contact in the ego's forward/lateral coordinate frame."""
    f = int(event["f"])
    other = event["b"] if event["a"] == "ego" else event["a"]
    j = core.IX[other]
    ego = R.F[k, f, core.IX["ego"]]
    actor = R.F[k, f, j]
    rx, rz = actor[0] - ego[0], actor[1] - ego[1]
    lon = rx * ego[2] + rz * ego[3]
    lat = -rx * ego[3] + rz * ego[2]
    if lon > HALF_EGO and abs(lat) < 1.6:
        return "front"
    if lon < -HALF_EGO and abs(lat) < 1.6:
        return "rear"
    return "side"


def progress_metrics(R: core.Rollout) -> tuple[np.ndarray, np.ndarray]:
    """Return ego travel distance and the number of harsh-braking frames per scenario."""
    ego = R.F[:, :, core.IX["ego"]]
    dx = np.diff(ego[..., 0], axis=1)
    dz = np.diff(ego[..., 1], axis=1)
    distance = np.hypot(dx, dz).sum(axis=1)
    harsh_braking = np.count_nonzero(ego[..., 5] < -3.0, axis=1)
    return distance, harsh_braking


# ---------------------------------------------------------------- given helpers

def pair_min_ttc(R, follower, leader, cap=10.0, lat_max=2.2, leader_vmin=-1.0):
    """(K,) smallest TTC of follower running into leader while they share a corridor."""
    F = R.F
    a, b = F[:, :, core.IX[follower]], F[:, :, core.IX[leader]]
    rx, rz = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
    lon = rx * a[..., 2] + rz * a[..., 3]
    lat = -rx * a[..., 3] + rz * a[..., 2]
    gap = np.maximum(lon - core.LEN[core.IX[follower]] / 2 - core.LEN[core.IX[leader]] / 2, 0.0)
    dv = a[..., 4] - b[..., 4]
    ok = (lon > 0) & (np.abs(lat) < lat_max) & (dv > 0.1) & (b[..., 4] >= leader_vmin)
    ttc = np.where(ok, gap / np.maximum(dv, 1e-6), np.inf)
    return np.minimum(cap, ttc.min(1))


def ped_room(R, cap=30.0):
    """(K,) smallest stopping room [m] left while the crossing pedestrian is in the ego's lane."""
    e, p = R.F[:, :, core.IX["ego"]], R.F[:, :, core.IX["P1"]]
    mu = np.asarray(R.params["mu"])[:, None]
    inlane = np.abs(p[..., 1] - e[..., 1]) < 1.9
    ahead = p[..., 0] - e[..., 0] - HALF_EGO
    room = np.where(inlane & (ahead > -1.0), ahead - e[..., 4] ** 2 / (2 * mu * G), cap)
    return np.clip(room.min(1), -cap, cap)