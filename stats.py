"""Wilson confidence intervals and Cohen's kappa with a paired-bootstrap confidence interval."""

import math
from collections.abc import Sequence
from statistics import NormalDist

import numpy as np
from sklearn.metrics import cohen_kappa_score

Z_95 = NormalDist().inv_cdf(0.975)
BOOTSTRAP_SEED = 20260525
BOOTSTRAP_RESAMPLES = 1000


def wilson_ci(k: int, n: int) -> tuple[float, float]:
    """95% Wilson score interval for k successes out of n, as proportions."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f"need 0 <= k <= n and n > 0, got k={k}, n={n}")
    p = k / n
    denom = 1 + Z_95**2 / n
    centre = (p + Z_95**2 / (2 * n)) / denom
    half = Z_95 * math.sqrt(p * (1 - p) / n + Z_95**2 / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def kappa_with_ci(a: Sequence[str], b: Sequence[str], rng: np.random.Generator) -> dict[str, float | int]:
    """Cohen's kappa between two paired label sequences, with a 95% paired-bootstrap CI.

    Each of the 1,000 resamples draws len(a) pairs with replacement; resamples in which
    either rater uses only one label are skipped. The CI is the 2.5th-97.5th percentile
    (linear interpolation) of the remaining kappas.
    """
    x, y = np.asarray(a), np.asarray(b)
    if len(x) != len(y) or len(x) == 0:
        raise ValueError("label sequences must be non-empty and of equal length")
    n = len(x)
    kappas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        idx = rng.choice(n, n, replace=True)
        sx, sy = x[idx], y[idx]
        if len(set(sx)) < 2 or len(set(sy)) < 2:
            continue
        kappas.append(float(cohen_kappa_score(sx, sy)))
    if not kappas:
        raise ValueError("every bootstrap resample was skipped; the CI is undefined")
    return {
        "n": n,
        "agree": int((x == y).sum()),
        "kappa": float(cohen_kappa_score(x, y)),
        "ci_low": float(np.percentile(kappas, 2.5, method="linear")),
        "ci_high": float(np.percentile(kappas, 97.5, method="linear")),
    }
