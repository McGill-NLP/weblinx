import sys
import unittest

import weblinx as wl
from weblinx.processing import load_candidate_elements

# import llama's processing code to test
from modeling.llama.processing import (
    format_candidates,
    format_utterances,
    format_utterances_truncated,
    get_speaker,
    multi_attempt_format_prev_turns_truncated,
)


# if needed, run this function to get candidates:
def create_candidates_unittest_jsonl():
    import json
    from pathlib import Path
    from weblinx.processing import load_candidate_elements

    demo_name = "aaabtsd"  # change if needed
    candidate_path = "wl_data/candidates/test_geo.jsonl"  # change if needed
    save_path = "tests/demonstrations/candidates_unittest.jsonl"
    candidate_elements = load_candidate_elements(candidate_path, group_keys=None)
    filt_elems = [e for e in candidate_elements if e["demo_name"] == demo_name]

    with open(save_path, "w") as f:
        for elem in filt_elems:
            f.write(json.dumps(elem) + "\n")


class TestBuildPromptRecords(unittest.TestCase):
    def setUp(self):
        self.demo = wl.Demonstration("aaabtsd", base_dir="./tests/demonstrations")
        # load tests/demonstrations/candidates_unittest.jsonl
        self.candidates = load_candidate_elements(
            "tests/demonstrations/candidates_unittest.jsonl"
        )

    def test_format_candidates(self):
        """
        Tests the format_candidates function to ensure it returns the expected
        string representation of a list of candidates, including the candidate
        index and the candidate's intent.
        """


if __name__ == "__main__":
    unittest.main()
