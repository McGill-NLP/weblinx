import argparse
from pathlib import Path
import logging

from . import auto_eval_and_save, compute_aggregated_scores
from .. import utils as __wl_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--results-dir",
        type=str,
        default="./results",
        help="Directory containing the results.json files.",
    )
    parser.add_argument(
        "-s",
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
    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    if not args.skip_eval:
        auto_eval_and_save(results_dir=results_dir, check_hashes=not args.skip_hashes)

    # Re-compute the aggregated scores
    score_records = compute_aggregated_scores(results_dir=results_dir)
    save_path = results_dir / "aggregated_scores.json"
    __wl_utils.auto_save_json(score_records, save_path, indent=2, backend="json")
    logger.info(f"\n\nSaved aggregated scores to {save_path}")

if __name__ == '__main__':
    main()