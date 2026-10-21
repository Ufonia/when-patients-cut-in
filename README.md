# When Patients Cut In: Extending Clinical Conversational AI Safety to Interruptions

Data and analysis code for the paper (EMNLP 2026, Findings): the 1,360 simulated dialogues the results are computed on, with their judge verdicts; the human labels used to validate the two judges; the judge prompts; and code that recomputes the paper's fail rates, Wilson confidence intervals, Δpp and judge-agreement kappas from these files.

## Abstract
![Overview](overview.png)

Clinical voice agents are now deployed in routine care, where real patients do not wait their turn: they interrupt. These systems typically use a cascaded architecture (speech-to-text → LLM → text-to-speech), so when a patient cuts the agent off mid-utterance, clinically required content can be lost even when the model handles cooperative transcripts well. Yet clinical conversational-AI benchmarks almost universally assume patients wait for the agent to finish, missing interruption-induced loss of required content. We present a transcript-based evaluation of interruption recovery, adapting conversation-analytic overlap categories into three operational types (recognitional, competitive, transitional sub-unit) and testing four deployment-oriented, non-reasoning LLM configurations across four cells spanning history-taking (information gathering) and FAQ (information provision), scored on whether the agent preserves the clinically required content. In the gathering cells, target-question failure varied across models; in the provision cells, where arms are directly comparable, failure rose for every model. Rankings differ across cells, and competitive FAQ interruption produced 30/30 provision-coverage failures for all four models (Wilson 95% CI: 88.6–100.0%; baseline 0/30 for three, 4/30 for Llama). A brief apology marker (“sorry to interrupt”) shifts recovery by tens of percentage points, inconsistently across models, and for one it reduces recovery. Interruption robustness therefore cannot be a single score: evaluation must be content-grounded, reported per cell, and matched to the deployment's interruption profile.

## What's here

| Path | Contents |
|---|---|
| `data/trials/<cell>/` | The 1,360 simulated dialogues the paper reports on, one JSON file per trial (`<trial_id>.json`), each with its judge verdict. |
| `data/judge_validation/<pack>/` | The 120 dialogues, sampled from experiment runs, annotated to validate the two judges (Appendix B, Tables 4–6), one JSON file per dialogue (`<item_id>.json`). |
| `prompts/` | The target-question and provision-coverage judge prompts. |
| `reproduce.py` | Prints the paper's fail rates, Wilson 95% CIs, Δpp and Cohen's κ (Tables 2, 4–7 and Figures 2–6), recomputed from the data. |
| `analysis.py`, `stats.py`, `load.py` | The study design and the computation behind each number; the Wilson interval and bootstrap κ; reading the data files and checking each record. |
| `tests/` | `paper_numbers.yaml` lists the numbers the paper prints and where; the tests recompute each one from the data, and check the printed report. |

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run reproduce.py   # prints the paper's tables and figures as markdown tables
uv run pytest         # checks them against the paper
```

## Use notice

This dataset is for research on the safety evaluation of clinical conversational agents. All dialogues are LLM-simulated; no real patient interactions were generated, scored or modified. In each dialogue the agent is one of the four evaluated LLMs running an agent prompt from the paper's appendix; the dialogues do not come from a deployed clinical system. Many show the agent failing to convey required clinical information. The transcripts must not be used as clinical advice or as examples of recommended patient-facing behaviour. They contain outputs of GPT-5.4 mini, Claude Haiku 4.5, Gemini 2.5 Flash and Llama 3.1 8B, whose providers' terms may also apply.

## Data format

Each file holds one JSON object.

**Trials** (`data/trials/<cell>/<trial_id>.json`)

| Field | Values |
|---|---|
| `trial_id` | e.g. `provision-competitive.defensive-strong.llama-3.1-8b.baseline.004`, `gathering-competitive.claude-haiku-4.5.interrupt.003`, or `gathering-competitive.marker-present.gemini-2.5-flash.interrupt.001` in the marker ablation. |
| `cell` | `gathering-recognitional`, `gathering-competitive`, `provision-competitive`, `provision-transitional` |
| `agent_prompt` | `standard`, `defensive-strong` in provision cells; `null` in gathering cells, which have one agent prompt |
| `marker` | `present`, `absent` (apology-marker ablation), or `null` |
| `arm` | `baseline`, `interrupt` |
| `model` | `Claude Haiku 4.5`, `Gemini 2.5 Flash`, `GPT-5.4 mini`, `Llama 3.1 8B` |
| `transcript` | Utterances in order, each `{"speaker": "patient" \| "agent", "text": ...}`, starting with the patient's fixed opening line. The interrupted utterance has `intended` and `delivered` in place of `text`. |
| `interruption` | `null` for baseline trials; otherwise `utterance` (index of the interrupted utterance in `transcript`), `type` (`recognitional`, `competitive`, `transitional-sub-unit`), `cut_word_index` and `total_words` (the agent delivered the first `cut_word_index` of `total_words` words). |
| `verdict` | `judge` (`target-question` for gathering cells, `provision-coverage` for provision cells), `label` (`pass` / `fail`, the judge's `True` / `False`) and the judge's `reasoning`. |

**Judge-validation items** (`data/judge_validation/<pack>/<item_id>.json`, pack `gathering` or `provision`) have the same `cell`, `agent_prompt`, `marker`, `arm`, `model`, `transcript` and `interruption` fields, plus `item_id`, `judge`, and `labels`: `A` and `B` (the two annotators), `resolved` (the adjudicated label) and `judge` (the LLM judge), each `pass` / `fail`.

In gathering cells, an interrupt trial counts only if the agent attempted the target question, so those interrupt arms are not compared with their baselines (see Table 2).

The judge prompts in `prompts/` are as run. The simulator is not included.

## Paper

https://arxiv.org/abs/2608.29241

## Citation

```bibtex
@misc{ellis2026patientscutinextending,
      title={When Patients Cut In: Extending Clinical Conversational AI Safety to Interruptions},
      author={Zachary Ellis and Spencer Hazel and Adam Brandt and Yajie Vera He and Ernest Lim and Jared Joselowitz},
      year={2026},
      eprint={2608.29241},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2608.29241},
}
```

## Licence

Code: MIT (see `LICENSE`). Data (`data/`): [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (see `data/LICENSE`). Prompts (`prompts/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see `prompts/LICENSE`).

## Note

For gathering-recognitional, Claude Haiku 4.5, interrupt arm, the released verdicts give 36.7% (11/30); the paper reports 40.0% (Table 2, Section 4.2 and Figure 2), from one miscounted trial. The difference does not affect the paper's findings.
