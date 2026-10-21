"""Print the numbers in the paper's tables and figures, recomputed from the released data.

Usage: uv run reproduce.py
"""

from collections import Counter

from analysis import (
    PACK_TABLE_ROWS,
    PROMPTS_FOR_CELL,
    Condition,
    Counts,
    arm_delta_pp,
    condition_counts,
    fail_pct,
    kappa_results,
    marker_delta_pp,
    pack_row_counts,
)
from load import ARMS, CELLS, MODELS, Trial, ValidationItem, load_trials, load_validation
from stats import wilson_ci


def _table(header: list[str], rows: list[list[str]]) -> str:
    """A markdown table with its columns padded to line up."""
    widths = [max(len(r[c]) for r in [header, *rows]) for c in range(len(header))]

    def line(cells: list[str]) -> str:
        return "| " + " | ".join(cell.ljust(w) for cell, w in zip(cells, widths, strict=True)) + " |"

    return "\n".join([line(header), line(["-" * w for w in widths]), *map(line, rows)])


def _rate(counts: Counts, key: Condition, ci: bool = True) -> str:
    k, n = counts[key]
    text = f"{k}/{n} ({100 * k / n:.1f}%)"
    if ci:
        lo, hi = wilson_ci(k, n)
        text += f" [{100 * lo:.1f}, {100 * hi:.1f}]"
    return text


def _pp(value: float) -> str:
    return f"{value:+.1f}"


def _arm_panel(counts: Counts, cell: str, prompt: str | None, delta: bool) -> str:
    """Baseline and interrupt fail rate per model, optionally with their difference."""
    rows = []
    for model in MODELS:
        row = [model, *(_rate(counts, (cell, prompt, None, model, arm)) for arm in ARMS)]
        if delta:
            row.append(_pp(arm_delta_pp(counts, cell, prompt, model)))
        rows.append(row)
    return _table(["model", "baseline", "interrupt", *(["Δpp"] if delta else [])], rows)


def _marker_panel(counts: Counts, cell: str, prompt: str | None) -> str:
    """Interrupt-arm fail rate per model with the apology marker present and absent."""
    rows = [
        [
            model,
            *(_rate(counts, (cell, prompt, marker, model, "interrupt")) for marker in ("present", "absent")),
            _pp(marker_delta_pp(counts, cell, prompt, model)),
        ]
        for model in MODELS
    ]
    return _table(["model", "marker present", "marker absent", "Δpp (present - absent)"], rows)


def _section(title: str, *blocks: str) -> str:
    return "\n\n".join([f"## {title}", *blocks])


def _table_2(counts: Counts) -> str:
    rows = []
    for cell in CELLS:
        # Gathering interrupt arms are filtered on the target question, so they get no Δpp.
        if cell.startswith("provision-"):
            rows.append([f"{cell} (Δpp)", *(_pp(arm_delta_pp(counts, cell, "standard", m)) for m in MODELS)])
        else:
            rates = (fail_pct(counts, (cell, None, None, m, "interrupt")) for m in MODELS)
            rows.append([f"{cell} (interrupt fail %)", *(f"{r:.1f}" for r in rates)])
    return _section(
        "Table 2: headline outcomes",
        _table(["", *MODELS], rows),
    )


def _figure_2(counts: Counts) -> str:
    return _section(
        "Figure 2: target-question fail rate, gathering cells",
        "Left: gathering-recognitional",
        _arm_panel(counts, "gathering-recognitional", None, delta=False),
        "Right: gathering-competitive",
        _arm_panel(counts, "gathering-competitive", None, delta=False),
    )


def _figure_3(counts: Counts) -> str:
    return _section(
        "Figure 3: provision-coverage fail rate, provision cells",
        "Left: provision-competitive",
        _arm_panel(counts, "provision-competitive", "standard", delta=True),
        "Right: provision-transitional",
        _arm_panel(counts, "provision-transitional", "standard", delta=True),
    )


def _figure_4(counts: Counts) -> str:
    return _section(
        "Figure 4: apology-marker ablation, interrupt arms",
        "Left: gathering-competitive, target-question fail rate",
        _marker_panel(counts, "gathering-competitive", None),
        "Right: provision-competitive, defensive-strong prompt, provision-coverage fail rate",
        _marker_panel(counts, "provision-competitive", "defensive-strong"),
    )


def _table_4(items: list[ValidationItem]) -> str:
    counts, arms = pack_row_counts(items), Counter((i.pack, i.arm) for i in items)
    rows = []
    for pack in dict.fromkeys(pack for pack, _, _ in PACK_TABLE_ROWS):
        rows += [
            [p, cell, variant, str(counts[(p, cell, variant)])]
            for p, cell, variant in PACK_TABLE_ROWS
            if p == pack
        ]
        baseline, interrupt = arms[(pack, "baseline")], arms[(pack, "interrupt")]
        rows.append(
            [f"{pack} total", "", f"{baseline} baseline + {interrupt} interrupt", str(baseline + interrupt)]
        )
    return _section("Table 4: judge-validation packs", _table(["pack", "source cell", "variant", "n"], rows))


def _kappa_table(kappas: dict, pack: str, comparisons: tuple[tuple[str, str], ...]) -> str:
    rows = []
    for a, b in comparisons:
        r = kappas[(pack, a, b)]
        rows.append(
            [
                f"{a} vs {b}",
                f"{r['kappa']:.3f} ({r['ci_low']:.3f}, {r['ci_high']:.3f})",
                f"{r['agree']}/{r['n']} ({100 * r['agree'] / r['n']:.1f}%)",
            ]
        )
    return _table(["comparison", "Cohen's κ (95% bootstrap CI)", "agreement"], rows)


def _table_5(kappas: dict) -> str:
    return _section(
        "Table 5: target-question judge agreement, gathering pack",
        "A, B: the annotators; resolved: the adjudicated label; judge: the LLM judge.",
        _kappa_table(kappas, "gathering", (("A", "B"), ("judge", "resolved"))),
    )


def _table_6(kappas: dict) -> str:
    return _section(
        "Table 6: provision-coverage judge agreement, provision pack",
        _kappa_table(
            kappas, "provision", (("A", "B"), ("A", "judge"), ("B", "judge"), ("judge", "resolved"))
        ),
    )


def _table_7(counts: Counts) -> str:
    cell = "provision-competitive"
    rows = [
        [
            prompt,
            model,
            *(_rate(counts, (cell, prompt, None, model, arm), ci=False) for arm in ARMS),
            _pp(arm_delta_pp(counts, cell, prompt, model)),
        ]
        for prompt in PROMPTS_FOR_CELL[cell]
        for model in MODELS
    ]
    return _section(
        "Table 7: provision-competitive prompt variants",
        _table(["agent prompt", "model", "baseline", "interrupt", "Δpp"], rows),
    )


def _figure_5(counts: Counts) -> str:
    return _section(
        "Figure 5: provision-competitive prompt variants",
        "Left: standard prompt",
        _arm_panel(counts, "provision-competitive", "standard", delta=True),
        "Right: defensive-strong prompt",
        _arm_panel(counts, "provision-competitive", "defensive-strong", delta=True),
    )


def _figure_6(counts: Counts) -> str:
    return _section(
        "Figure 6: provision-competitive, defensive-strong prompt, with and without the marker",
        "Left: baseline and interrupt",
        _arm_panel(counts, "provision-competitive", "defensive-strong", delta=True),
        "Right: apology-marker ablation, interrupt arms",
        _marker_panel(counts, "provision-competitive", "defensive-strong"),
    )


def report(trials: list[Trial], items: list[ValidationItem]) -> str:
    """The paper's tables and figures, in the paper's order, as markdown."""
    counts, kappas = condition_counts(trials), kappa_results(items)
    parts = [
        f"Trials: {len(trials):,}. Fail rates as fails/n (%) [Wilson 95% CI]. "
        "One value differs from the paper; see the README.",
        _table_2(counts),
        _figure_2(counts),
        _figure_3(counts),
        _figure_4(counts),
        _table_4(items),
        _table_5(kappas),
        _table_6(kappas),
        _table_7(counts),
        _figure_5(counts),
        _figure_6(counts),
    ]
    return "\n\n".join(parts) + "\n"


if __name__ == "__main__":
    print(report(load_trials(), load_validation()), end="")
