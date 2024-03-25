import argparse
import itertools
from pathlib import Path
import logging

import pandas as pd
import numpy as np
from tqdm.auto import tqdm

from . import metrics
from .metrics import Metric
from .. import utils as __wl_utils

from ..processing.outputs import (
    parse_predicted_output_string,
    sanitize_args,
    infer_element_for_action,
    extract_action_from_turn,
    dict_has_keys,
    are_not_none,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# by default, we will use weblinx/_data/splits.json
# which is relative to this file, which is weblinx/eval/_iinit__.py
# so we need to go up one directory to find the _data directory

data_dir = Path(__file__).parent.parent / "_data"
default_split_file = data_dir / "splits.json"


def get_metrics_map():
    return {
        "exact-match": metrics.ExactMatchMetric,
        "intent-match": metrics.IntentMatchMetric,
        "chrf": metrics.ChrFMetric,
        "iou": metrics.IOUMetric,
        "urlf": metrics.URLFMetric,
    }


def run_evaluation(processed_results, metrics, num_turns=1):
    metrics_map = get_metrics_map()
    metrics: Metric = [metrics_map[metric]() for metric in metrics]

    scores = []

    for i, out in enumerate(processed_results):
        score_item = {
            "demo_name": out["demo_name"],
            "turn_index": out["turn_index"],
            "pred_intent": out["pred"]["intent"],
            "ref_intent": out["ref"]["intent"],
        }

        # for each prediction, compute all the applicable metrics
        pred = out["pred"]
        for metric in metrics:
            metric: Metric
            best_score = None
            # over all the future turns up to `num_turns`
            for out_next in processed_results[i : i + num_turns]:
                if out["demo_name"] != out_next["demo_name"]:
                    break

                ref = out_next["ref"]
                # skip incompatible predictions
                if metric.is_applicable(pred, ref):
                    res = metric.score(pred, ref)

                    if best_score is None or res > best_score:
                        best_score = res

            score_item[metric.name] = best_score

        scores.append(score_item)

    return scores


def validate_reference_action(ref_action, next_turn, uid_key="data-webtasks-id"):
    """
    This verifies that the reference action is valid for evaluation. This means:
    - The reference action is not None
    - The reference action has an intent
    """
    # If the reference action is None, then we cannot evaluate
    if ref_action is None:
        return False

    # If the reference action does not have an intent, then we cannot evaluate
    if ref_action.get("intent") is None:
        return False

    # If the reference ation is not one of the intent that has an element,
    # then we ignore it and assume that it is valid
    if ref_action["intent"] not in ["change", "click", "textinput", "submit"]:
        return True

    # If the reference action does not have an elemnt or an attributes field,
    # then we cannot evaluate. If it does have an attributes field, then we need
    # to check if it has a <uid> field in it
    if ref_action.get("element") is None or ref_action.get("element") is None:
        return False

    if ref_action["element"]["attributes"].get(uid_key) is None:
        return False

    if next_turn is not None and ref_action["intent"] == "click":
        # If the next turn is a copy intent, and the current turn is a change intent,
        # then the current turn is not valid (as it is an action that leads to a copy
        # intent which is not evaluated)
        if next_turn.intent == "copy":
            # print("Found a click intent that leads to a copy intent, skipping")
            return False

        # If next turn is a submit intent, then we only keep the current click
        # intent if the submit intent has a <uid> that is different
        # from the current click intent
        if next_turn.intent == "submit":
            next_uid = next_turn.element["attributes"][uid_key]
            cur_uid = ref_action["element"]["attributes"][uid_key]

            if next_uid == cur_uid:
                print(
                    "Found a click intent that leads to a submit intent with the same uid, skipping"
                )
                return False

    # If we reach this point, then the reference action is valid
    return True


def process_model_results(replays, model_results, model_name=None, verbose=True):
    """
    Processes the results for a model (i.e. the content of an entire results.json file output by a model).
    """
    processed_results = []

    if model_name is None:
        desc = "Processing results"
    else:
        desc = f"Processing results for {model_name}"
    for pred in tqdm(model_results, desc=desc, disable=not verbose):
        demo_name = pred["demo_name"]
        turn_index = pred["turn_index"]
        replay = replays[demo_name]
        turn = replay[turn_index]

        # First, we get the reference action
        ref_action = extract_action_from_turn(turn)

        # then, we get the predicted action
        out_raw = pred["output_predicted"]
        intent, args = parse_predicted_output_string(out_raw)
        args = sanitize_args(args)
        infered_element = infer_element_for_action(intent=intent, args=args, turn=turn)
        pred_action = {"intent": intent, "args": args, "element": infered_element}

        # Save both as a dictionary (with the demo name and turn index as well as the model name)
        processed_results.append(
            {
                "demo_name": demo_name,
                "turn_index": turn_index,
                "pred": pred_action,
                "ref": ref_action,
            }
        )

    processed_results_valid = []

    for i, result in enumerate(processed_results):
        ref_action = result["ref"]
        replay = replays[result["demo_name"]]

        ti = result["turn_index"]
        next_turn = replay[ti + 1] if ti + 1 < len(replay) else None

        is_valid = validate_reference_action(ref_action, next_turn=next_turn)

        if is_valid:
            processed_results_valid.append(result)

    return processed_results_valid


def load_replays(
    splits, base_dir="./wl_data/demonstrations/", split_file=default_split_file
):
    from weblinx import list_demonstrations, Replay

    all_demos = list_demonstrations(base_dir=base_dir)

    demo_map = {d.name: d for d in all_demos}
    replays = {}

    demos_by_splits = __wl_utils.auto_read_json(split_file)

    for split in splits:
        logger.info(f"Loading demonstrations for split {split}")

        replays.update(
            {
                demo_name: Replay.from_demonstration(demo_map[demo_name])
                for demo_name in demos_by_splits[split]
            }
        )
    logger.info(f"Loaded {len(replays)} demonstrations")

    return replays


def compute_overall_score(row):
    """
    Computes the overall score for a given row of the score dataframe. The overall score is:
    - for a text intent: chrf
    - for an element intent: iou
    - for a url intent: urlf
    - for an element and text intent: iou * chrf

    In practice, we simply need to see if which columns have NaN to determine the intent group.
    """
    import pandas as pd

    if pd.notna(row["iou"]) and pd.notna(row["chrf"]):
        return row["iou"] * row["chrf"]
    elif pd.notna(row["urlf"]):
        return row["urlf"]
    elif pd.notna(row["chrf"]):
        return row["chrf"]
    elif pd.notna(row["iou"]):
        return row["iou"]
    else:
        return None


def compute_aggregated_scores(
    results_dir,
    metrics=None,
    splits=None,
    project_names=None,
    score_fname="eval_scores.csv",
    split_file=default_split_file,
    verbose=True,
):
    intent_to_metrics = {
        "change": ["exact-match", "intent-match", "iou"],
        "click": ["exact-match", "intent-match", "iou"],
        "load": ["exact-match", "intent-match", "urlf"],
        "say": ["exact-match", "intent-match", "chrf"],
        "scroll": ["exact-match", "intent-match"],
        "submit": ["exact-match", "intent-match", "iou"],
        "textinput": ["exact-match", "intent-match", "chrf", "iou"],
    }
    group_to_metrics = {
        "element": ["iou"],
        "text": ["chrf", "urlf"],
    }
    results_dir = Path(results_dir)

    score_records = []

    if metrics is None:
        metrics = list(get_metrics_map().keys())

    if project_names is None:
        project_names = [d.name for d in results_dir.iterdir() if d.is_dir()]

    if splits is None:
        splits = ("valid", "test_iid", "test_web", "test_geo", "test_vis", "test_cat")

    iterator = tqdm(
        list(itertools.product(project_names, splits)),
        desc="Aggregating scores",
        disable=not verbose,
    )
    for project_name, split in iterator:
        split_dir = results_dir / project_name / split
        score_paths = list(split_dir.glob(f"**/{score_fname}"))

        for score_path in score_paths:
            model_name = str(score_path.relative_to(split_dir).parent)

            df = pd.read_csv(score_path)
            df["overall"] = df.apply(compute_overall_score, axis=1)
            unc_df = df.copy()
            # This line will fill all unmatched intent with 0 instead of
            # NaN, so when we calculate the mean, the 0's are
            # not skipped unlike NaN's
            unc_df.loc[unc_df["intent-match"] == 0, metrics] = 0
            unc_df.loc[unc_df["intent-match"] == 0, "overall"] = 0

            for intent in df["ref_intent"].unique():
                scores_by_metric = df[df["ref_intent"] == intent][metrics].mean(
                    skipna=True
                )
                unc_scores_by_metric = unc_df[unc_df["ref_intent"] == intent][
                    metrics
                ].mean(skipna=True)

                scores_by_metric = scores_by_metric.replace({np.nan: None})
                unc_scores_by_metric = unc_scores_by_metric.replace({np.nan: None})

                for metric in intent_to_metrics[intent]:
                    score_records.append(
                        {
                            "split": split,
                            "intent": intent,
                            "metric": metric,
                            "model_name": model_name,
                            "project_name": project_name,
                            "score": scores_by_metric[metric],
                            "unconditional_score": unc_scores_by_metric[metric],
                        }
                    )

            # Also compute the overall score
            overall_score = df["overall"].mean(skipna=True)
            unc_overall_score = unc_df["overall"].mean(skipna=True)

            score_records.append(
                {
                    "split": split,
                    "intent": "overall",
                    "metric": "overall",
                    "model_name": model_name,
                    "project_name": project_name,
                    "score": overall_score,
                    "unconditional_score": unc_overall_score,
                }
            )
            # Now, do the same for intent-match across all intents
            intent_match_col = df["intent-match"]
            unc_intent_match_col = unc_df["intent-match"]

            intent_match_score = intent_match_col.mean(skipna=True)
            unc_intent_match_score = unc_intent_match_col.mean(skipna=True)

            score_records.append(
                {
                    "split": split,
                    "intent": "overall",
                    "metric": "intent-match",
                    "model_name": model_name,
                    "project_name": project_name,
                    "score": intent_match_score,
                    "unconditional_score": unc_intent_match_score,
                }
            )
            # Now, compute the group score for element intents (and text intents

            # If we take the max over columns, we get a single column with the non-NaN value
            elem_col = df[group_to_metrics["element"]].max(axis=1)
            unc_elem_col = unc_df[group_to_metrics["element"]].max(axis=1)
            elem_score = elem_col.mean(skipna=True)
            unc_elem_score = unc_elem_col.mean(skipna=True)

            score_records.append(
                {
                    "split": split,
                    "intent": "element-group",
                    "metric": "-".join(group_to_metrics["element"]),
                    "model_name": model_name,
                    "project_name": project_name,
                    "score": elem_score,
                    "unconditional_score": unc_elem_score,
                }
            )

            # Now, do the same for text intents
            text_col = df[group_to_metrics["text"]].max(axis=1)
            unc_text_col = unc_df[group_to_metrics["text"]].max(axis=1)
            text_score = text_col.mean(skipna=True)
            unc_text_score = unc_text_col.mean(skipna=True)

            score_records.append(
                {
                    "split": split,
                    "intent": "text-group",
                    "metric": "-".join(group_to_metrics["text"]),
                    "model_name": model_name,
                    "project_name": project_name,
                    "score": text_score,
                    "unconditional_score": unc_text_score,
                }
            )

    return score_records


def auto_eval_and_save(
    results_dir,
    base_dir="./wl_data/demonstrations/",
    project_names=None,
    metrics=None,
    splits=None,
    future_turn_acc=1,
    res_fname="results.json",
    processed_fname="processed_results.json",
    score_fname_template="eval_scores.csv",
    split_file=default_split_file,
    check_hashes=True,
):
    """
    Unlike full_eval_and_save, this function will automatically load the replays and splits from the results_dir.

    """
    results_dir = Path(results_dir)

    if project_names is None:
        project_names = [d.name for d in results_dir.iterdir() if d.is_dir()]

    if splits is None:
        splits = ("valid", "test_iid", "test_web", "test_geo", "test_vis", "test_cat")

    if metrics is None:
        metrics = get_metrics_map().keys()

    score_fname = score_fname_template.format(future_turn_acc=future_turn_acc)

    replays = load_replays(splits=splits, base_dir=base_dir, split_file=split_file)

    # We take the cartesian product of project_names and splits
    for project, split in itertools.product(project_names, splits):
        subdir: Path = results_dir / project / split

        # Find all files in any subdir matching the results_file pattern
        result_paths = list(subdir.glob(f"**/{res_fname}"))

        if len(result_paths) == 0:
            logger.warning(f"Could not find any results files in {subdir}")
            continue

        for result_path in result_paths:
            # Infer the model name from the results file, which could be something like "google/flan-t5-base"
            # We should remove the subdir part from the results_file path
            model_name = result_path.relative_to(subdir).parent
            model_results = __wl_utils.auto_read_json(result_path)

            score_path = result_path.parent / score_fname
            processed_path = result_path.parent / processed_fname
            hash_path = result_path.parent / f"hashes.json"

            # First, check if the hash of results.json and scores-fta-<i>.csv are the same as the
            # hashes in the hashes.json file. We look at md5sum specifically
            hashes = __wl_utils.auto_read_json(hash_path) if hash_path.exists() else {}

            if "md5" not in hashes:
                hashes["md5"] = {}

            # res_md5 = hashlib.md5(ujson.dumps(model_results).encode()).hexdigest()
            res_md5 = __wl_utils.hash_json(model_results, "md5")
            score_md5 = __wl_utils.hash_file(score_path, "md5", error_on_missing=False)
            processed_md5 = __wl_utils.hash_file(
                processed_path, "md5", error_on_missing=False
            )

            if (
                check_hashes
                and dict_has_keys(
                    hashes["md5"], [res_fname, score_fname, processed_fname]
                )
                and are_not_none(res_md5, score_md5, processed_md5)
                and res_md5 == hashes["md5"][res_fname]
                and score_md5 == hashes["md5"][score_fname]
                and processed_md5 == hashes["md5"][processed_fname]
            ):
                logger.info(
                    f"Found equal hashes, skipping [{project} | {model_name} | {split}]"
                )
                continue

            # process results and save scores as csv
            logger.info(f"Computing score for [{project} | {model_name} | {split}]")
            print("model_results length:", len(model_results))
            processed_results = process_model_results(
                replays, model_results, model_name=model_name
            )
            print("processed_results length:", len(processed_results))

            scores = run_evaluation(
                processed_results,
                metrics=metrics,
                num_turns=future_turn_acc,
            )
            df = pd.DataFrame(scores).round(2)
            df.to_csv(score_path, index=False)

            # Save the processed results
            __wl_utils.auto_save_json(processed_results, processed_path, indent=2)

            if score_md5 is None:
                score_md5 = __wl_utils.hash_file(score_path, "md5")

            if processed_md5 is None:
                processed_md5 = __wl_utils.hash_file(processed_path, "md5")

            # Save the hashes
            hashes["md5"][res_fname] = res_md5
            hashes["md5"][score_fname] = score_md5
            hashes["md5"][processed_fname] = processed_md5

            __wl_utils.auto_save_json(hashes, hash_path, indent=2)
            logger.info(f"Saved hashes to {hash_path}\n")
