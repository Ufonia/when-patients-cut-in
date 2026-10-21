import numpy as np
import pytest

from stats import BOOTSTRAP_SEED, kappa_with_ci, wilson_ci


@pytest.mark.parametrize(
    ("k", "n", "low", "high"),
    [
        (30, 30, 0.886, 1.0),
        (0, 30, 0.0, 0.114),
        (0, 10, 0.0, 0.278),
        (9, 10, 0.596, 0.982),
        (15, 30, 0.332, 0.668),
    ],
)
def test_wilson_ci(k, n, low, high):
    lo, hi = wilson_ci(k, n)
    assert (round(lo, 3), round(hi, 3)) == (low, high)


@pytest.mark.parametrize(("k", "n"), [(0, 0), (-1, 10), (11, 10)])
def test_wilson_ci_rejects_bad_counts(k, n):
    with pytest.raises(ValueError, match="need 0 <= k <= n"):
        wilson_ci(k, n)


def test_kappa_perfect_and_partial_agreement():
    a = ["pass"] * 5 + ["fail"] * 5
    r = kappa_with_ci(a, a, np.random.default_rng(BOOTSTRAP_SEED))
    assert r["kappa"] == 1.0 and r["agree"] == 10 and (r["ci_low"], r["ci_high"]) == (1.0, 1.0)
    r = kappa_with_ci(a, ["pass", "fail"] * 5, np.random.default_rng(BOOTSTRAP_SEED))
    assert r["agree"] == 6 and round(r["kappa"], 3) == 0.2


def test_kappa_rejects_bad_input():
    with pytest.raises(ValueError, match="equal length"):
        kappa_with_ci(["pass"], ["pass", "fail"], np.random.default_rng(0))


def test_kappa_rejects_constant_labels():
    """If every resample has a single-label rater, the CI is undefined."""
    with pytest.raises(ValueError, match="skipped"):
        kappa_with_ci(["pass"] * 6, ["pass", "fail"] * 3, np.random.default_rng(0))
