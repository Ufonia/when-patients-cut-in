from pathlib import Path

import pytest

from analysis import condition_counts, kappa_results
from load import load_trials, load_validation
from reproduce import report

TRIALS = load_trials()
ITEMS = load_validation()


def test_report_matches_expected_output():
    """`uv run reproduce.py` prints exactly the committed report."""
    expected = Path(__file__).with_name("expected_report.md").read_text(encoding="utf-8")
    assert report(TRIALS, ITEMS) == expected


def test_missing_condition_is_rejected():
    trials = [t for t in TRIALS if not (t.model == "GPT-5.4 mini" and t.arm == "baseline")]
    with pytest.raises(ValueError, match=r"conditions differ from the study design: missing \[\("):
        condition_counts(trials)


def test_extra_condition_is_rejected():
    stray = next(t for t in TRIALS if t.arm == "baseline")
    with pytest.raises(ValueError, match=r"extra \[\("):
        condition_counts([*TRIALS, stray.model_copy(update={"marker": "present"})])


def test_validation_items_outside_the_design_are_rejected():
    stray = next(i for i in ITEMS if i.arm == "baseline").model_copy(update={"marker": "present"})
    with pytest.raises(ValueError, match="validation items outside the study design"):
        report(TRIALS, [*ITEMS, stray])


def test_validation_items_must_fill_every_table_4_row():
    items = [i for i in ITEMS if i.cell != "provision-transitional"]
    with pytest.raises(ValueError, match="do not match Table 4's rows"):
        report(TRIALS, items)


def test_kappas_do_not_depend_on_item_order():
    assert kappa_results(ITEMS[::-1]) == kappa_results(ITEMS)
