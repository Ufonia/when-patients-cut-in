Trials: 1,360. Fail rates as fails/n (%) [Wilson 95% CI]. One value differs from the paper; see the README.

## Table 2: headline outcomes

|                                            | Claude Haiku 4.5 | Gemini 2.5 Flash | GPT-5.4 mini | Llama 3.1 8B |
| ------------------------------------------ | ---------------- | ---------------- | ------------ | ------------ |
| gathering-recognitional (interrupt fail %) | 36.7             | 83.3             | 76.7         | 36.7         |
| gathering-competitive (interrupt fail %)   | 0.0              | 23.3             | 50.0         | 30.0         |
| provision-competitive (Δpp)                | +100.0           | +100.0           | +100.0       | +86.7        |
| provision-transitional (Δpp)               | +23.3            | +73.3            | +100.0       | +73.3        |

## Figure 2: target-question fail rate, gathering cells

Left: gathering-recognitional

| model            | baseline                 | interrupt                  |
| ---------------- | ------------------------ | -------------------------- |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4]  | 11/30 (36.7%) [21.9, 54.5] |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4]  | 25/30 (83.3%) [66.4, 92.7] |
| GPT-5.4 mini     | 3/30 (10.0%) [3.5, 25.6] | 23/30 (76.7%) [59.1, 88.2] |
| Llama 3.1 8B     | 1/30 (3.3%) [0.6, 16.7]  | 11/30 (36.7%) [21.9, 54.5] |

Right: gathering-competitive

| model            | baseline                | interrupt                  |
| ---------------- | ----------------------- | -------------------------- |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4] | 0/30 (0.0%) [0.0, 11.4]    |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4] | 7/30 (23.3%) [11.8, 40.9]  |
| GPT-5.4 mini     | 0/30 (0.0%) [0.0, 11.4] | 15/30 (50.0%) [33.2, 66.8] |
| Llama 3.1 8B     | 0/30 (0.0%) [0.0, 11.4] | 9/30 (30.0%) [16.7, 47.9]  |

## Figure 3: provision-coverage fail rate, provision cells

Left: provision-competitive

| model            | baseline                 | interrupt                    | Δpp    |
| ---------------- | ------------------------ | ---------------------------- | ------ |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| GPT-5.4 mini     | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| Llama 3.1 8B     | 4/30 (13.3%) [5.3, 29.7] | 30/30 (100.0%) [88.6, 100.0] | +86.7  |

Right: provision-transitional

| model            | baseline                 | interrupt                    | Δpp    |
| ---------------- | ------------------------ | ---------------------------- | ------ |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4]  | 7/30 (23.3%) [11.8, 40.9]    | +23.3  |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4]  | 22/30 (73.3%) [55.6, 85.8]   | +73.3  |
| GPT-5.4 mini     | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| Llama 3.1 8B     | 3/30 (10.0%) [3.5, 25.6] | 25/30 (83.3%) [66.4, 92.7]   | +73.3  |

## Figure 4: apology-marker ablation, interrupt arms

Left: gathering-competitive, target-question fail rate

| model            | marker present             | marker absent              | Δpp (present - absent) |
| ---------------- | -------------------------- | -------------------------- | ---------------------- |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4]    | 0/30 (0.0%) [0.0, 11.4]    | +0.0                   |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4]    | 20/30 (66.7%) [48.8, 80.8] | -66.7                  |
| GPT-5.4 mini     | 23/30 (76.7%) [59.1, 88.2] | 18/30 (60.0%) [42.3, 75.4] | +16.7                  |
| Llama 3.1 8B     | 6/30 (20.0%) [9.5, 37.3]   | 7/30 (23.3%) [11.8, 40.9]  | -3.3                   |

Right: provision-competitive, defensive-strong prompt, provision-coverage fail rate

| model            | marker present            | marker absent                | Δpp (present - absent) |
| ---------------- | ------------------------- | ---------------------------- | ---------------------- |
| Claude Haiku 4.5 | 4/10 (40.0%) [16.8, 68.7] | 10/10 (100.0%) [72.2, 100.0] | -60.0                  |
| Gemini 2.5 Flash | 5/10 (50.0%) [23.7, 76.3] | 10/10 (100.0%) [72.2, 100.0] | -50.0                  |
| GPT-5.4 mini     | 9/10 (90.0%) [59.6, 98.2] | 10/10 (100.0%) [72.2, 100.0] | -10.0                  |
| Llama 3.1 8B     | 9/10 (90.0%) [59.6, 98.2] | 9/10 (90.0%) [59.6, 98.2]    | +0.0                   |

## Table 4: judge-validation packs

| pack            | source cell             | variant                    | n  |
| --------------- | ----------------------- | -------------------------- | -- |
| gathering       | gathering-recognitional | dismissive overlap         | 30 |
| gathering       | gathering-competitive   | strict topic-change        | 22 |
| gathering       | gathering-competitive   | marker variant             | 8  |
| gathering total |                         | 30 baseline + 30 interrupt | 60 |
| provision       | provision-transitional  | strict cooperative ack     | 28 |
| provision       | provision-competitive   | standard prompt            | 9  |
| provision       | provision-competitive   | defensive-strong prompt    | 11 |
| provision       | provision-competitive   | marker variant             | 12 |
| provision total |                         | 16 baseline + 44 interrupt | 60 |

## Table 5: target-question judge agreement, gathering pack

A, B: the annotators; resolved: the adjudicated label; judge: the LLM judge.

| comparison        | Cohen's κ (95% bootstrap CI) | agreement      |
| ----------------- | ---------------------------- | -------------- |
| A vs B            | 1.000 (1.000, 1.000)         | 60/60 (100.0%) |
| judge vs resolved | 0.942 (0.795, 1.000)         | 59/60 (98.3%)  |

## Table 6: provision-coverage judge agreement, provision pack

| comparison        | Cohen's κ (95% bootstrap CI) | agreement     |
| ----------------- | ---------------------------- | ------------- |
| A vs B            | 0.831 (0.667, 0.966)         | 55/60 (91.7%) |
| A vs judge        | 0.966 (0.883, 1.000)         | 59/60 (98.3%) |
| B vs judge        | 0.865 (0.730, 0.967)         | 56/60 (93.3%) |
| judge vs resolved | 0.933 (0.831, 1.000)         | 58/60 (96.7%) |

## Table 7: provision-competitive prompt variants

| agent prompt     | model            | baseline     | interrupt      | Δpp    |
| ---------------- | ---------------- | ------------ | -------------- | ------ |
| standard         | Claude Haiku 4.5 | 0/30 (0.0%)  | 30/30 (100.0%) | +100.0 |
| standard         | Gemini 2.5 Flash | 0/30 (0.0%)  | 30/30 (100.0%) | +100.0 |
| standard         | GPT-5.4 mini     | 0/30 (0.0%)  | 30/30 (100.0%) | +100.0 |
| standard         | Llama 3.1 8B     | 4/30 (13.3%) | 30/30 (100.0%) | +86.7  |
| defensive-strong | Claude Haiku 4.5 | 0/10 (0.0%)  | 10/10 (100.0%) | +100.0 |
| defensive-strong | Gemini 2.5 Flash | 0/10 (0.0%)  | 9/10 (90.0%)   | +90.0  |
| defensive-strong | GPT-5.4 mini     | 0/10 (0.0%)  | 10/10 (100.0%) | +100.0 |
| defensive-strong | Llama 3.1 8B     | 0/10 (0.0%)  | 10/10 (100.0%) | +100.0 |

## Figure 5: provision-competitive prompt variants

Left: standard prompt

| model            | baseline                 | interrupt                    | Δpp    |
| ---------------- | ------------------------ | ---------------------------- | ------ |
| Claude Haiku 4.5 | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| Gemini 2.5 Flash | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| GPT-5.4 mini     | 0/30 (0.0%) [0.0, 11.4]  | 30/30 (100.0%) [88.6, 100.0] | +100.0 |
| Llama 3.1 8B     | 4/30 (13.3%) [5.3, 29.7] | 30/30 (100.0%) [88.6, 100.0] | +86.7  |

Right: defensive-strong prompt

| model            | baseline                | interrupt                    | Δpp    |
| ---------------- | ----------------------- | ---------------------------- | ------ |
| Claude Haiku 4.5 | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |
| Gemini 2.5 Flash | 0/10 (0.0%) [0.0, 27.8] | 9/10 (90.0%) [59.6, 98.2]    | +90.0  |
| GPT-5.4 mini     | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |
| Llama 3.1 8B     | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |

## Figure 6: provision-competitive, defensive-strong prompt, with and without the marker

Left: baseline and interrupt

| model            | baseline                | interrupt                    | Δpp    |
| ---------------- | ----------------------- | ---------------------------- | ------ |
| Claude Haiku 4.5 | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |
| Gemini 2.5 Flash | 0/10 (0.0%) [0.0, 27.8] | 9/10 (90.0%) [59.6, 98.2]    | +90.0  |
| GPT-5.4 mini     | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |
| Llama 3.1 8B     | 0/10 (0.0%) [0.0, 27.8] | 10/10 (100.0%) [72.2, 100.0] | +100.0 |

Right: apology-marker ablation, interrupt arms

| model            | marker present            | marker absent                | Δpp (present - absent) |
| ---------------- | ------------------------- | ---------------------------- | ---------------------- |
| Claude Haiku 4.5 | 4/10 (40.0%) [16.8, 68.7] | 10/10 (100.0%) [72.2, 100.0] | -60.0                  |
| Gemini 2.5 Flash | 5/10 (50.0%) [23.7, 76.3] | 10/10 (100.0%) [72.2, 100.0] | -50.0                  |
| GPT-5.4 mini     | 9/10 (90.0%) [59.6, 98.2] | 10/10 (100.0%) [72.2, 100.0] | -10.0                  |
| Llama 3.1 8B     | 9/10 (90.0%) [59.6, 98.2] | 9/10 (90.0%) [59.6, 98.2]    | +0.0                   |
