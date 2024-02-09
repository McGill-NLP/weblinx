---
title: "Leaderboard"
permalink: /leaderboard/
---

You can find below the leaderboard for the WebLINX benchmark. It computes the overall score and the group-level scores for the action model. Both are computed on the test splits.

* Jump to the [Information](#information) section for more details on how to add your results.
* The [Action Model](#leaderboard-action-model) section contains the leaderboard for the action model, which predicts the action to be taken.
* The [Dense Markup Ranker](#leaderboard-dense-markup-ranker) section contains the leaderboard for the ranker used to select HTML candidate elements.
* To understand how the scores are computed, please refer to the [Scoring](#scoring) section.

## Leaderboard: Action Model

| Model         | Overall |   IM  |  Element (IoU)   | Text (F1)   | Finetuned | Links                             | Tags |
|---------------|-----------|-------|-------|--------|-----------|------------------------------------------------|------|
| Llama-2-13B   |  27.86    | 83.07 | 25.79 | 28.77  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| S-LLaMA-2.7B  |  27.61    | 84.74 | 25.33 | 29.27  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-7B    |  27.51    | 83.73 | 25.46 | 28.91  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| S-LLaMA-1.3B  |  25.94    | 84.22 | 23.11 | 27.62  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-3B    |  25.25    | 81.61 | 22.18 | 26.41  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-3.5F      |  23.35    | 78.52 | 21.19 | 23.84  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Fuyu-8B       |  22.29    | 80.96 | 17.85 | 24.57  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-3B    |  21.90    | 80.11 | 17.70 | 23.43  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-780M  |  18.56    | 80.40 | 17.36 | 14.47  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Pix2Act-1.3B  |  18.44    | 82.12 |  9.36 | 26.69  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-250M  |  16.18    | 79.81 | 16.62 |  9.27  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-780M  |  16.03    | 76.31 | 14.75 | 13.68  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-250M  |  13.48    | 74.71 | 13.24 |  7.83  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Pix2Act-282M  |  12.47    | 79.87 |  5.93 | 16.58  |    ✔️     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-4T        |  11.05    | 41.87 | 11.21 |  6.97  |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-4V        |  10.98    | 42.38 | 11.49 |  6.43  |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-3.5T      |   8.89    | 42.70 |  9.05 |  3.56  |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-13B   |   5.28    | 43.51 |  4.93 |  1.44  |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-7B    |   4.33    | 33.92 |  3.17 |  2.33  |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |


## Leaderboard: Dense Markup Ranker

| Model   | Test-Vis   | Test-Geo   | Test-Cat   | Test-Web   | Test-OOD  | Links                                            | Tags |
|---------|------------|------------|------------|------------|-----------|--------------------------------------------------|------|
| BGE     | 60.07      | 48.82      | 43.61      | 47.55      | 50.01     | [Code](https://github.com/mcgill-nlp/weblinx)    | EE |
| MiniLM  | 59.73      | 50.95      | 44.05      | 52.75      | 51.87     | [Code](https://github.com/mcgill-nlp/weblinx)    | EE |
| GTE     | 56.91      | 44.46      | 42.74      | 48.39      | 48.16     | [Code](https://github.com/mcgill-nlp/weblinx)    | EE |

## Scoring

You can learn more about the evaluation metrics and splits in our paper. The ranker uses recall@10, whereas action model is more complex:

- We compute a intent match (IM) score that measures how well the predicted intent matches the ground truth intent.
- We have different intents which are evaluated separately, at the turn-level. This means we get a score for each turn. There are two groups:
  - Element Group: `click`, `textinput`, `submit` use the IoU metric.
  - Text Group: `say`, `textinput`, `load` use the F1 metric.
- We compute the overall score by averaging the scores for each turn in a given split. The score for element and text groups are the average for turns with one of the intents in the group.
- We have 4 out-of-domain test splits (Test-vis, test-geo, test-cat, test-web) testing different generalization capabilities of the model. 
- The score reported for action model is the average of the overall score, group score, and IM for each split, which we call test-ood.
- For the ranker, scores on all splits are reported.

## Information

Information about the information in the leaderboard can be found below.

### Adding results

To add your results, please fork the repository, add your results to the leaderboard.md file and submit a pull request to the main branch with the subject line “Add results for [your team name]”.
DatePermalink

Please use the YYYY-MM-DD format. If you are submitting multiple results, please use the date of the most recent result.


### Links

In the `Links` column, you can provide links to your code, paper, and/or blog post. Rather than giving the full URL, please use the following format:

```
[Code](https://github.com); [Paper](https://arxiv.org/abs/1234.5678); [Blog](https://medium.com)
```

Please do not exceed 5 links.

## Tags

The following tags are allowed:

- SR: Self-reported
- EE: Externally evaluated (must provide link to evaluation script)
- RI: Inference was reproduced by a third party following given instructions (must provide link to instructions and third party’s results)
- TR: Training process was independently reproduced by a third party following given instructions (must provide link to training scripts and third party’s results).

Since EE supersedes SR, please only use the most appropriate tag, or update results if an existing tag exists. If there are multiple tags, please separate them with a comma:

```
[EE](https://github.com/some-repo/eval.py), [TR](https://github.com/another-repo/train.py)
```