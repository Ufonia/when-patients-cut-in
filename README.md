# When Patients Cut In: Extending Clinical Conversational AI Safety to Interruptions

This repository will host the code and data accompanying the paper (EMNLP 2026, Findings). The work studies a safety-critical failure mode in cascaded clinical voice agents: **interruption**. When a patient cuts the agent off mid-utterance, clinically required content can be lost even when the model handles cooperative transcripts well. We introduce a transcript-based evaluation of interruption recovery, adapting conversation-analytic overlap categories into three operational interruption types and scoring whether agents preserve the clinically required content across the interruption.

## Abstract
![Overview](overview.png)

Clinical voice agents are now deployed in routine care, where real patients do not wait their turn, they interrupt. These systems typically use a cascaded architecture (speech-to-text → LLM → text-to-speech), so when a patient cuts the agent off mid-utterance, clinically required content can be lost even when the model handles cooperative transcripts well. Yet clinical conversational-AI benchmarks almost universally assume patients wait for the agent to finish, missing interruption-induced loss of required content. We present a transcript-based evaluation of interruption recovery, adapting conversation-analytic overlap categories into three operational types (recognitional, competitive, transitional sub-unit) and testing four deployment-oriented, non-reasoning LLM configurations across four cells spanning history-taking (gathering) and FAQ (provision), scored on whether the agent preserves the clinically required content. In the gathering cells, target-question failure varied across models; in the provision cells, where arms are directly comparable, failure rose for every model. Rankings differ across cells, and competitive FAQ interruption produced 30/30 provision-coverage failures for all four models (Wilson 95% CI: 88.6–100.0%; baseline 0/30 for three, 4/30 for Llama). A brief apology marker (“sorry to interrupt”) shifts recovery by tens of percentage points, inconsistently across models, and for one it reduces recovery. Interruption robustness therefore cannot be a single score: evaluation must be content-grounded, reported per cell, and matched to the deployment's interruption profile.

## 🚧 To do — release for camera-ready

Committed in our author responses (reproducibility follow-up) and the meta-review, and targeted for release on publication so that every reported failure rate and confidence interval is reproducible from the released dialogues:

- [ ] **Generated-dialogue dataset** — the full set of generated dialogues across all cells, each trial with the intended vs delivered agent utterance, cut position, interruption type, and judge verdict.
- [ ] **Scoring and analysis code** — the LLM judges and the aggregation that produce the reported failure rates and Wilson confidence intervals.

Already released with the paper: the prompt suite and anonymised per-cell configurations (see the paper appendices).

## 📄 Paper

https://arxiv.org/abs/2608.29241

## 📚 Citation

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
