"""Read the released data files and check each record's fields and their consistency."""

import json
from collections import Counter
from pathlib import Path
from typing import Any, Literal, Self, get_args

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

DATA = Path(__file__).resolve().parent / "data"

# Cells and models are listed in the row and column order of the paper's Table 2.
Cell = Literal[
    "gathering-recognitional", "gathering-competitive", "provision-competitive", "provision-transitional"
]
ModelName = Literal["Claude Haiku 4.5", "Gemini 2.5 Flash", "GPT-5.4 mini", "Llama 3.1 8B"]
AgentPrompt = Literal["standard", "defensive-strong"]
Marker = Literal["present", "absent"]
Arm = Literal["baseline", "interrupt"]
Judge = Literal["target-question", "provision-coverage"]
InterruptionType = Literal["recognitional", "competitive", "transitional-sub-unit"]
Label = Literal["pass", "fail"]

CELLS: tuple[Cell, ...] = get_args(Cell)
MODELS: tuple[ModelName, ...] = get_args(ModelName)
ARMS: tuple[Arm, ...] = get_args(Arm)
JUDGE_FOR_CELL: dict[Cell, Judge] = {
    "gathering-recognitional": "target-question",
    "gathering-competitive": "target-question",
    "provision-competitive": "provision-coverage",
    "provision-transitional": "provision-coverage",
}
INTERRUPTION_TYPE_FOR_CELL: dict[Cell, InterruptionType] = {
    "gathering-recognitional": "recognitional",
    "gathering-competitive": "competitive",
    "provision-competitive": "competitive",
    "provision-transitional": "transitional-sub-unit",
}
PACK_FOR_JUDGE: dict[Judge, str] = {"target-question": "gathering", "provision-coverage": "provision"}


class _Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Utterance(_Record):
    speaker: Literal["agent", "patient"]
    text: str


class InterruptedUtterance(_Record):
    """The agent utterance the patient cut off: what the agent meant to say and what it said."""

    speaker: Literal["agent"]
    intended: str
    delivered: str


class Interruption(_Record):
    utterance: int
    type: InterruptionType
    cut_word_index: int
    total_words: int


class Verdict(_Record):
    judge: Judge
    label: Label
    reasoning: str


class Labels(_Record):
    A: Label
    B: Label
    resolved: Label
    judge: Label


class Dialogue(_Record):
    """The fields shared by trials and judge-validation items."""

    cell: Cell
    agent_prompt: AgentPrompt | None
    marker: Marker | None
    arm: Arm
    model: ModelName
    transcript: list[Utterance | InterruptedUtterance] = Field(min_length=1)
    interruption: Interruption | None

    @model_validator(mode="after")
    def _check_dialogue(self) -> Self:
        if (self.agent_prompt is None) != self.cell.startswith("gathering-"):
            raise ValueError("agent_prompt is null for gathering cells and set for provision cells")
        positions = [k for k, u in enumerate(self.transcript) if isinstance(u, InterruptedUtterance)]
        interruption = self.interruption
        if self.arm == "baseline":
            if interruption is not None or positions:
                raise ValueError("a baseline dialogue has no interruption and no interrupted utterance")
            return self
        if interruption is None:
            raise ValueError("an interrupt dialogue must have an interruption")
        if positions != [interruption.utterance]:
            raise ValueError("interruption.utterance must point at the one interrupted utterance")
        u = self.transcript[interruption.utterance]
        delivered, intended = u.delivered.split(), u.intended.split()
        if (interruption.cut_word_index, interruption.total_words) != (len(delivered), len(intended)) or (
            delivered != intended[: len(delivered)]
        ):
            raise ValueError("delivered must be the first cut_word_index of the total_words intended words")
        if interruption.type != INTERRUPTION_TYPE_FOR_CELL[self.cell]:
            raise ValueError(f"interruption type {interruption.type!r} does not belong to {self.cell}")
        return self


class Trial(Dialogue):
    trial_id: str
    verdict: Verdict

    @model_validator(mode="after")
    def _check_judge(self) -> Self:
        if self.verdict.judge != JUDGE_FOR_CELL[self.cell]:
            raise ValueError(f"judge {self.verdict.judge!r} does not score {self.cell}")
        return self


class ValidationItem(Dialogue):
    item_id: str
    judge: Judge
    labels: Labels

    @model_validator(mode="after")
    def _check_judge(self) -> Self:
        if self.judge != JUDGE_FOR_CELL[self.cell]:
            raise ValueError(f"judge {self.judge!r} does not score {self.cell}")
        if not self.item_id.startswith(f"{self.pack}."):
            raise ValueError(f"item_id {self.item_id!r} is not in the {self.pack} pack")
        return self

    @property
    def pack(self) -> str:
        return PACK_FOR_JUDGE[self.judge]


def read_records(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Read every `root/<group>/<id>.json` file, in path order; errors name the file.

    Hidden files (names starting with ".") are ignored; any other file under `root` is an error.
    """
    records = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part.startswith(".") for part in rel.parts) or path.is_dir():
            continue
        if len(rel.parts) != 2 or path.suffix != ".json":
            raise ValueError(f"{path}: not a <group>/<id>.json record file")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"{path}: {e}") from None
        if not isinstance(record, dict):
            raise ValueError(f"{path}: expected a JSON object")
        records.append((path, record))
    if not records:
        raise ValueError(f"{root}: no record files")
    return records


def _load[R: Trial | ValidationItem](
    root: Path, record_type: type[R], id_field: str, folder_field: str
) -> list[R]:
    """Check every record under `root` against `record_type` and against its file's folder and name."""
    records = []
    for path, raw in read_records(root):
        where = f"{path.parent.name}/{path.name}"
        try:
            record = record_type.model_validate(raw)
        except ValidationError as e:
            raise ValueError(f"{where}: {e}") from None
        expected = f"{getattr(record, folder_field)}/{getattr(record, id_field)}.json"
        if where != expected:
            raise ValueError(f"{path}: this record belongs in {expected}")
        records.append(record)
    duplicates = sorted(i for i, n in Counter(getattr(r, id_field) for r in records).items() if n > 1)
    if duplicates:
        raise ValueError(f"{root}: duplicate IDs {duplicates}")
    return records


def load_trials(root: Path = DATA / "trials") -> list[Trial]:
    """The trials under `root` (by default the 1,360 reported trials), checked."""
    return _load(root, Trial, "trial_id", "cell")


def load_validation(root: Path = DATA / "judge_validation") -> list[ValidationItem]:
    """The judge-validation items under `root` (by default the 120 annotated dialogues), checked."""
    return _load(root, ValidationItem, "item_id", "pack")
