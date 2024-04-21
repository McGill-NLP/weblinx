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
|---------------|---------|-------|------------------|-------------|-----------|-----------------------------------|------|
| ?????         |  28.88  | 84.36 | 27.44            | 28.88       |    ✔️      | ????                               | EE   |
| Llama-2-13B   |  25.21  | 81.91 | 22.82            | 26.60       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| S-LLaMA-2.7B  |  25.02  | 84.00 | 22.60            | 27.17       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-7B    |  24.57  | 82.64 | 22.26            | 26.50       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-3B    |  23.77  | 81.14 | 20.31            | 25.75       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| S-LLaMA-1.3B  |  23.73  | 83.32 | 20.54            | 25.85       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-3.5F      |  21.22  | 77.56 | 18.64            | 22.39       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-3B    |  20.94  | 79.89 | 16.50            | 23.16       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Fuyu-8B       |  19.97  | 80.07 | 15.70            | 22.30       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-780M  |  17.27  | 80.02 | 15.36            | 14.05       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Pix2Act-1.3B  |  16.88  | 81.80 |  8.28            | 25.21       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Flan-T5-250M  |  14.99  | 79.69 | 14.86            | 9.21        |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-780M  |  15.13  | 75.87 | 13.39            | 13.58       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| MindAct-250M  |  12.63  | 74.25 | 12.05            | 7.67        |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Pix2Act-282M  |  12.51  | 79.71 |  6.20            | 16.40       |    ✔️      | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-4T        |  10.72  | 41.66 | 10.85            | 6.75        |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-4V        |  10.45  | 42.36 | 10.91            | 6.21        |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| GPT-3.5T      |   8.51  | 42.77 |  8.62            | 3.45        |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-13B   |   5.16  | 43.68 |  4.80            | 1.31        |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |
| Llama-2-7B    |   4.04  | 33.96 |  2.92            | 2.14        |    ❌     | [Code](https://github.com/mcgill-nlp/weblinx) | EE   |



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