import json

import pytest

from load import load_trials, load_validation, read_records

TRIALS = load_trials()
ITEMS = load_validation()
INTERRUPT = next(t for t in TRIALS if t.cell == "provision-competitive" and t.arm == "interrupt").model_dump()
BASELINE = next(t for t in TRIALS if t.cell == "gathering-competitive" and t.arm == "baseline").model_dump()
ITEM = next(i for i in ITEMS if i.pack == "gathering").model_dump()


def _write(root, record, group, record_id):
    """Write one record at `root/<group>/<id>.json`, as the release lays them out."""
    path = root / group / f"{record_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record), encoding="utf-8")
    return root


def _trial(root, record):
    return _write(root, record, record["cell"], record["trial_id"])


def _item(root, record):
    return _write(root, record, record["item_id"].split(".")[0], record["item_id"])


def _changed(record, change):
    r = json.loads(json.dumps(record))
    change(r)
    return r


def test_read_records_names_the_bad_file(tmp_path):
    with pytest.raises(ValueError, match="no record files"):
        read_records(tmp_path)
    (tmp_path / "cell").mkdir()
    (tmp_path / "cell" / "bad.json").write_text('{"a": ', encoding="utf-8")
    with pytest.raises(ValueError, match=r"cell/bad\.json: "):
        read_records(tmp_path)
    (tmp_path / "cell" / "bad.json").write_text("null", encoding="utf-8")
    with pytest.raises(ValueError, match=r"cell/bad\.json: expected a JSON object"):
        read_records(tmp_path)


def _uncut(r):
    """An interrupt record with its interruption removed from the transcript and the interruption field."""
    k = r["interruption"]["utterance"]
    r["transcript"][k] = {"speaker": "agent", "text": r["transcript"][k]["delivered"]}
    r["interruption"] = None


def _second_cut(r):
    """An interrupt record with one more agent utterance marked as interrupted."""
    k = next(k for k, u in enumerate(r["transcript"]) if u["speaker"] == "agent" and "text" in u)
    text = r["transcript"][k]["text"]
    r["transcript"][k] = {"speaker": "agent", "intended": text, "delivered": text}


def _swap_delivered_word(r):
    """The interrupted utterance's delivered text with its first word replaced."""
    u = r["transcript"][r["interruption"]["utterance"]]
    u["delivered"] = " ".join(["Elsewhere", *u["delivered"].split()[1:]])


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r.update(model="GPT-4"), r"\nmodel\n  Input should be"),
        (lambda r: r.update(notes=""), r"\nnotes\n  Extra inputs are not permitted"),
        (lambda r: r.pop("verdict"), r"\nverdict\n  Field required"),
        (
            lambda r: r["verdict"].update(label="Fail"),
            r"\nverdict\.label\n  Input should be 'pass' or 'fail'",
        ),
        (lambda r: r["verdict"].update(judge="target-question"), "does not score"),
        (lambda r: r["transcript"][0].update(speaker="doctor"), r"\ntranscript\.0\.Utterance\.speaker\n"),
        (lambda r: r.update(transcript=[]), r"\ntranscript\n  List should have at least 1 item"),
        (_uncut, "an interrupt dialogue must have an interruption"),
        (
            lambda r: r["interruption"].update(utterance=r["interruption"]["utterance"] + 1),
            "must point at the one interrupted utterance",
        ),
        (_second_cut, "must point at the one interrupted utterance"),
        (
            lambda r: r["interruption"].update(cut_word_index=r["interruption"]["cut_word_index"] + 1),
            "must be the first cut_word_index of the total_words intended words",
        ),
        (
            lambda r: r["interruption"].update(total_words=r["interruption"]["total_words"] + 1),
            "must be the first cut_word_index of the total_words intended words",
        ),
        (_swap_delivered_word, "must be the first cut_word_index of the total_words intended words"),
        (
            lambda r: r["interruption"].update(cut_word_index=str(r["interruption"]["cut_word_index"])),
            r"\ninterruption\.cut_word_index\n  Input should be a valid integer",
        ),
        (lambda r: r["interruption"].update(type="recognitional"), "does not belong to"),
    ],
)
def test_trial_checks(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        load_trials(_trial(tmp_path, _changed(INTERRUPT, change)))


@pytest.mark.parametrize(
    "change",
    [_second_cut, lambda r: r.update(interruption=INTERRUPT["interruption"])],
    ids=["cut", "interruption"],
)
def test_baseline_with_an_interruption_is_rejected(tmp_path, change):
    with pytest.raises(ValueError, match="a baseline dialogue has no interruption"):
        load_trials(_trial(tmp_path, _changed(BASELINE, change)))


@pytest.mark.parametrize(("record", "prompt"), [(BASELINE, "standard"), (INTERRUPT, None)])
def test_agent_prompt_is_null_exactly_for_gathering_cells(tmp_path, record, prompt):
    with pytest.raises(ValueError, match="agent_prompt is null for gathering cells"):
        load_trials(_trial(tmp_path, _changed(record, lambda r: r.update(agent_prompt=prompt))))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r["labels"].update(A="Pass"), r"\nlabels\.A\n  Input should be 'pass' or 'fail'"),
        (lambda r: r["labels"].pop("resolved"), r"\nlabels\.resolved\n  Field required"),
        (lambda r: r.update(judge="provision-coverage"), "does not score"),
    ],
)
def test_validation_checks(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        load_validation(_item(tmp_path, _changed(ITEM, change)))


def test_misplaced_file_is_rejected(tmp_path):
    _write(tmp_path / "trials", BASELINE, "provision-transitional", BASELINE["trial_id"])
    with pytest.raises(ValueError, match=f"belongs in {BASELINE['cell']}/{BASELINE['trial_id']}.json"):
        load_trials(tmp_path / "trials")
    _write(tmp_path / "items", ITEM, "gathering", "renamed")
    with pytest.raises(ValueError, match=f"belongs in gathering/{ITEM['item_id']}.json"):
        load_validation(tmp_path / "items")


@pytest.mark.parametrize(
    ("rel", "rejected"),
    [
        ("record.json", True),
        ("cell/sub/record.json", True),
        ("cell/record.JSON", True),
        ("cell/notes.txt", True),
        ("cell/.hidden.json", False),
    ],
)
def test_only_record_files_are_read(tmp_path, rel, rejected):
    _trial(tmp_path, BASELINE)
    path = tmp_path / rel.replace("cell", BASELINE["cell"], 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(BASELINE), encoding="utf-8")
    if rejected:
        with pytest.raises(ValueError, match="not a <group>/<id>.json record file"):
            load_trials(tmp_path)
    else:
        assert [t.model_dump() for t in load_trials(tmp_path)] == [BASELINE]


def test_item_must_sit_in_its_judges_pack(tmp_path):
    renamed = _changed(ITEM, lambda r: r.update(item_id="provision" + r["item_id"].removeprefix("gathering")))
    with pytest.raises(ValueError, match="is not in the gathering pack"):
        load_validation(_write(tmp_path, renamed, "gathering", renamed["item_id"]))


def test_duplicate_id_across_folders_is_rejected(tmp_path):
    elsewhere = _changed(BASELINE, lambda r: r.update(cell="provision-transitional", agent_prompt="standard"))
    elsewhere["verdict"]["judge"] = "provision-coverage"
    _trial(tmp_path, BASELINE)
    _trial(tmp_path, elsewhere)
    with pytest.raises(ValueError, match="duplicate IDs"):
        load_trials(tmp_path)
