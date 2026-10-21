"""Every entry in tests/paper_numbers.yaml, recomputed from data/ at the paper's printed precision."""

from collections import Counter
from pathlib import Path

import pytest
import yaml

from analysis import arm_delta_pp, condition_counts, fail_pct, kappa_results, marker_delta_pp, pack_row_counts
from load import load_trials, load_validation
from stats import wilson_ci

PAPER = yaml.safe_load(Path(__file__).with_name("paper_numbers.yaml").read_text(encoding="utf-8"))
TRIALS = load_trials()
ITEMS = load_validation()
COUNTS = condition_counts(TRIALS)
KAPPAS = {(pack, frozenset((a, b))): r for (pack, a, b), r in kappa_results(ITEMS).items()}


def entries(section):
    def name(e):
        return " / ".join(str(v) for k, v in e.items() if k not in ("where", "reproduced", "note"))

    return pytest.mark.parametrize("e", PAPER[section], ids=name)


def _condition(e):
    return (e["cell"], e["agent_prompt"], e["marker"], e["model"], e["arm"])


def _kappa(e):
    return KAPPAS[(e["pack"], frozenset(e["comparison"]))]


def _expected(e):
    return e.get("reproduced", e["value"])


def test_total_trials():
    assert len(TRIALS) == PAPER["total_trials"][0]["value"]


@entries("trials_per_arm")
def test_trials_per_arm(e):
    assert {n for (_, prompt, *_), (_, n) in COUNTS.items() if prompt == e["agent_prompt"]} == {e["value"]}


@entries("fail_counts")
def test_fail_count(e):
    assert COUNTS[_condition(e)] == (e["fails"], e["n"])


@entries("fail_rates")
def test_fail_rate(e):
    assert round(fail_pct(COUNTS, _condition(e)), e["decimals"]) == _expected(e)


@entries("wilson_cis")
def test_wilson_ci(e):
    lo, hi = wilson_ci(*COUNTS[_condition(e)])
    assert (round(100 * lo, e["decimals"]), round(100 * hi, e["decimals"])) == (e["low"], e["high"])


@entries("arm_deltas")
def test_arm_delta(e):
    got = arm_delta_pp(COUNTS, e["cell"], e["agent_prompt"], e["model"])
    assert round(got, e["decimals"]) == e["value"]


@entries("marker_deltas")
def test_marker_delta(e):
    got = marker_delta_pp(COUNTS, e["cell"], e["agent_prompt"], e["model"])
    assert round(got, e["decimals"]) == e["value"]


@entries("gathering_changes")
def test_gathering_change(e):
    competitive, recognitional = (
        fail_pct(COUNTS, (cell, None, None, e["model"], "interrupt"))
        for cell in ("gathering-competitive", "gathering-recognitional")
    )
    assert round(competitive - recognitional, e["decimals"]) == e["value"]


@entries("kappas")
def test_kappa(e):
    assert round(_kappa(e)["kappa"], e["decimals"]) == e["value"]


@entries("kappa_cis")
def test_kappa_ci(e):
    r = _kappa(e)
    assert (round(r["ci_low"], e["decimals"]), round(r["ci_high"], e["decimals"])) == (e["low"], e["high"])


@entries("agreement_counts")
def test_agreement_count(e):
    r = _kappa(e)
    assert (r["agree"], r["n"]) == (e["agree"], e["n"])


@entries("agreement_rates")
def test_agreement_rate(e):
    r = _kappa(e)
    assert round(100 * r["agree"] / r["n"], e["decimals"]) == e["value"]


@entries("validation_pack_rows")
def test_validation_pack_row(e):
    assert pack_row_counts(ITEMS)[(e["pack"], e["cell"], e["variant"])] == e["value"]


@entries("validation_pack_arms")
def test_validation_pack_arm(e):
    assert Counter((i.pack, i.arm) for i in ITEMS)[(e["pack"], e["arm"])] == e["value"]


@entries("validation_pack_sizes")
def test_validation_pack_size(e):
    assert Counter(i.pack for i in ITEMS)[e["pack"]] == e["value"]


def test_one_value_differs_from_the_paper():
    (difference,) = [e for section in PAPER.values() for e in section if "reproduced" in e]
    assert difference in PAPER["fail_rates"] and difference["note"]
    assert (difference["cell"], difference["model"]) == ("gathering-recognitional", "Claude Haiku 4.5")
    assert difference["reproduced"] != difference["value"]
