"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    """Log importance weights p(u)/[(1-beta)q_CEM(u) + beta p(u)]."""
    if not 0.0 <= beta <= 1.0:
        raise ValueError("beta must be between 0 and 1")
    log_p = nat.logpdf(Z, Bn)
    log_proposal = proposal_logpdf(prop, Z, Bn)
    log_beta = math.log(beta) if beta > 0.0 else -math.inf
    log_one_minus_beta = math.log1p(-beta) if beta < 1.0 else -math.inf
    log_q = np.logaddexp(log_one_minus_beta + log_proposal, log_beta + log_p)
    return log_p - log_q


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    """Estimate a natural-distribution probability from importance samples."""
    logw = np.asarray(logw, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    if logw.shape != y.shape:
        raise ValueError("logw and y must have the same number of samples")
    n = y.size
    if n == 0:
        return dict(p=0.0, lo=0.0, hi=0.0, se=0.0, ess=0.0, n=0)

    w = np.exp(logw)
    wy = w * y
    p = float(np.mean(wy))
    se = float(np.std(wy, ddof=1) / math.sqrt(n)) if n > 1 else 0.0
    lo = max(0.0, p - z * se)
    hi = p + z * se

    finite = np.isfinite(logw)
    if finite.any():
        scaled = np.exp(logw[finite] - np.max(logw[finite]))
        sum_scaled = float(np.sum(scaled))
        ess = sum_scaled * sum_scaled / float(np.sum(scaled * scaled))
    else:
        ess = 0.0
    return dict(p=p, lo=lo, hi=hi, se=se, ess=float(ess), n=int(n))


def rule_of_three(n_eff: float) -> float:
    """Given: 95% upper bound on a probability when 0 events were seen in n_eff independent tries."""
    return 3.0 / max(n_eff, 1.0)