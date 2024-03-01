import argparse
from pathlib import Path
import logging

from . import auto_eval_and_save, compute_aggregated_scores
from .. import utils as __wl_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        "Evaluate the results of the WeblinX benchmark and compute the aggregated scores.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--results-dir",
        type=str,
        default="./results",
        help="Directory containing the results.json files.",
    )
    parser.add_argument(
        "-b",
        "--base_dir",
        type=str,
        default="./wl_data/demonstrations/",
        help="Base directory where the demonstrations are stored.",
    )
    parser.add_argument(
        "-se",
        "--skip-eval",
        action="store_true",
        help="Whether to skip evaluation and only compute the aggregated scores.",
    )
    parser.add_argument(
        "-sh",
        "--skip-hashes",
        action="store_true",
        help="Whether to skip checking the hashes.",
    )
    parser.add_argument(
        "--splits",
        type=str,
        default="valid,test_iid,test_vis,test_geo,test_web,test_cat",
        help="Comma-separated list of splits to evaluate.",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    splits = args.splits.split(",")

    if not args.skip_eval:
        auto_eval_and_save(
            results_dir=results_dir,
            check_hashes=not args.skip_hashes,
            base_dir=args.base_dir,
            splits=splits,
        )

    # Re-compute the aggregated scores
    score_records = compute_aggregated_scores(results_dir=results_dir, splits=splits)
    save_path = results_dir / "aggregated_scores.json"
    __wl_utils.auto_save_json(score_records, save_path, indent=2, backend="json")
    logger.info(f"\n\nSaved aggregated scores to {save_path}")


if __name__ == "__main__":
    main()
