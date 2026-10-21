"""The study design and the statistics the paper reports, computed from the loaded records."""

from collections import Counter

import numpy as np

from load import ARMS, CELLS, MODELS, Trial, ValidationItem
from stats import BOOTSTRAP_SEED, kappa_with_ci

# One condition of the study: (cell, agent_prompt, marker, model, arm).
Condition = tuple[str, str | None, str | None, str, str]
Counts = dict[Condition, tuple[int, int]]

# Agent prompts per cell; gathering cells have a single prompt, recorded as None.
PROMPTS_FOR_CELL = {
    "gathering-recognitional": (None,),
    "gathering-competitive": (None,),
    "provision-competitive": ("standard", "defensive-strong"),
    "provision-transitional": ("standard",),
}
# (cell, agent_prompt) of the two apology-marker ablations; their arms are interrupt only.
MARKER_ABLATIONS = (("gathering-competitive", None), ("provision-competitive", "defensive-strong"))

# Rows of the paper's Table 4: (pack, source cell, variant), in the paper's order.
PACK_TABLE_ROWS = (
    ("gathering", "gathering-recognitional", "dismissive overlap"),
    ("gathering", "gathering-competitive", "strict topic-change"),
    ("gathering", "gathering-competitive", "marker variant"),
    ("provision", "provision-transitional", "strict cooperative ack"),
    ("provision", "provision-competitive", "standard prompt"),
    ("provision", "provision-competitive", "defensive-strong prompt"),
    ("provision", "provision-competitive", "marker variant"),
)

# Comparisons in each validation pack, computed in this order from one generator per pack
# seeded with BOOTSTRAP_SEED.
KAPPA_COMPARISONS = {
    "gathering": (("judge", "resolved"), ("A", "B")),
    "provision": (("B", "judge"), ("A", "judge"), ("A", "B"), ("judge", "resolved")),
}


def expected_conditions() -> set[Condition]:
    """Every condition in the study design: 56 in total."""
    conditions = {
        (cell, prompt, None, model, arm)
        for cell in CELLS
        for prompt in PROMPTS_FOR_CELL[cell]
        for model in MODELS
        for arm in ARMS
    }
    conditions |= {
        (cell, prompt, marker, model, "interrupt")
        for cell, prompt in MARKER_ABLATIONS
        for marker in ("present", "absent")
        for model in MODELS
    }
    return conditions


def condition_counts(trials: list[Trial]) -> Counts:
    """(fails, n) for every condition; the trials must cover exactly the study design."""
    fails, n = Counter(), Counter()
    for t in trials:
        key = (t.cell, t.agent_prompt, t.marker, t.model, t.arm)
        n[key] += 1
        fails[key] += t.verdict.label == "fail"
    missing, extra = expected_conditions() - n.keys(), n.keys() - expected_conditions()
    if missing or extra:
        raise ValueError(
            f"conditions differ from the study design: "
            f"missing {sorted(missing, key=str)}, extra {sorted(extra, key=str)}"
        )
    return {k: (fails[k], n[k]) for k in n}


def fail_pct(counts: Counts, key: Condition) -> float:
    """Fail rate of one condition, in percent."""
    k, n = counts[key]
    return 100 * k / n


def arm_delta_pp(counts: Counts, cell: str, prompt: str | None, model: str) -> float:
    """Interrupt minus baseline fail rate, in percentage points."""
    interrupt = fail_pct(counts, (cell, prompt, None, model, "interrupt"))
    return interrupt - fail_pct(counts, (cell, prompt, None, model, "baseline"))


def marker_delta_pp(counts: Counts, cell: str, prompt: str | None, model: str) -> float:
    """Marker-present minus marker-absent fail rate, in percentage points."""
    present = fail_pct(counts, (cell, prompt, "present", model, "interrupt"))
    return present - fail_pct(counts, (cell, prompt, "absent", model, "interrupt"))


def kappa_results(items: list[ValidationItem]) -> dict[tuple[str, str, str], dict[str, float | int]]:
    """Kappa, bootstrap CI and agreement for every comparison in the paper's agreement tables,
    keyed by (pack, rater, rater). Each pack's items are taken in item-ID order."""
    out = {}
    for pack, comparisons in KAPPA_COMPARISONS.items():
        labels = [i.labels for i in sorted(items, key=lambda i: i.item_id) if i.pack == pack]
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        for a, b in comparisons:
            out[(pack, a, b)] = kappa_with_ci(
                [getattr(x, a) for x in labels], [getattr(x, b) for x in labels], rng
            )
    return out


def pack_variant(item: ValidationItem) -> str:
    """The item's row label in Table 4."""
    if item.marker:
        return "marker variant"
    if item.cell == "provision-competitive":
        return f"{item.agent_prompt} prompt"
    (variant,) = [v for _, cell, v in PACK_TABLE_ROWS if cell == item.cell and v != "marker variant"]
    return variant


def pack_row_counts(items: list[ValidationItem]) -> Counter:
    """Items per Table 4 row; the items must fill exactly those rows, within the study design."""
    outside = {(i.cell, i.agent_prompt, i.marker, i.model, i.arm) for i in items} - expected_conditions()
    if outside:
        raise ValueError(f"validation items outside the study design: {sorted(outside, key=str)}")
    rows = Counter((i.pack, i.cell, pack_variant(i)) for i in items)
    if set(rows) != set(PACK_TABLE_ROWS):
        raise ValueError(
            f"validation items do not match Table 4's rows: {sorted(set(rows) ^ set(PACK_TABLE_ROWS))}"
        )
    return rows
