import unittest
import json
import sys
import os

from .agent_test_version import evaluate

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestJSONFeedback(unittest.TestCase):
    def setUp(self):
        self.func = evaluate

    def test_normal_feedback(self):
        expected_result = {
            "filename": "filename.ext",
            "density": 0.0,
            "methods_pct": 0.0,
            "readability": 0.0,
            "meaningless_pct": 0.0,
            "issues": {
                "missing": {"info": "<b>Missing comments for complex code snippets:</b><br>Lines: ",
                            "lines": [1, 2, 3]},
                "incorrect": {"info": "<b>Comments that do not match the code:</b><br>Lines: ",
                              "lines": [4, 5, 6]},
                "useless": {"info": "<b>Redundant comments that just repeat the code:</b><br>Lines: ",
                            "lines": [7, 8, 9]},
                "vague": {"info": "<b>Comments that do not explain the code:<\b><br>Lines: ", "lines": [10, 11]},
                "jargon": {"info": "<b>Comments that use specific jargon w/o explanation:</b><br>Lines: ",
                           "lines": [12]},
                "garbage": {"info": "<b>Completely nonsensical comments:</b><br>Lines: ", "lines": []}
            }
        }

        input_json_feedback = {
            "MEANINGLESS_COMMENTS_PERCENTAGE": 0.0,
            "MISSING_COMMENTS": [{"LINE": 1}, {"LINE": 2}, {"LINE": 3}],
            "BAD_COMMENTS": [
                {"TYPE": "INCORRECT", "LINE": 4},
                {"TYPE": "INCORRECT", "LINE": 5},
                {"TYPE": "INCORRECT", "LINE": 6},
                {"TYPE": "USELESS", "LINE": 7},
                {"TYPE": "USELESS", "LINE": 8},
                {"TYPE": "USELESS", "LINE": 9},
                {"TYPE": "VAGUE", "LINE": 10},
                {"TYPE": "VAGUE", "LINE": 11},
                {"TYPE": "JARGON", "LINE": 12},
            ]
        }

        self.assertEqual(self.func(input_json_feedback), expected_result)

    def test_incorrect_feedback(self):
        with self.assertRaises(json.JSONDecodeError):
            self.func({"somekey": "somevalue"})
