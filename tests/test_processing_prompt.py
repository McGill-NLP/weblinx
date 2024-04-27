import unittest
from weblinx.processing.prompt import find_turns_with_instructor_chat
import weblinx as wl


class TestProcessingPrompt(unittest.TestCase):
    def setUp(self):
        self.demo = wl.Demonstration("aaabtsd", base_dir="./tests/demonstrations")

    def test_find_turns_with_instructor_chat(self):
        """
        Test the find_turns_with_instructor_chat function to ensure it correctly
        filters out turns that contain instructor chat. It checks that the output
        list contains only turns with instructor chat.
        """
        replay = wl.Replay.from_demonstration(self.demo)
        turn = replay[15]

        result = find_turns_with_instructor_chat(
            replay, turn, speaker="instructor", num_prev_turns=5
        )

        # In this demo, we checked that there are 3 turns with instructor chat
        # so it should return a list of 3 turns
        self.assertEqual(len(result), 3)

        # now, compare this with filter() function which should return the same
        start_index = max(0, turn.index - 5)
        result_filter = filter(
            lambda turn: turn.get("speaker") == "instructor"
            and turn.index < start_index,
            replay,
        )
        result_filter = list(result_filter)
        self.assertEqual(len(result_filter), 3)
        self.assertEqual(result, result_filter)
