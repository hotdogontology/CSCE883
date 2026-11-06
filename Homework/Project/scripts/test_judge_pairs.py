"""Checks for evidence leakage and false predictions from malformed responses."""
import unittest
from judge_pairs import build_messages, pair_payload, parse_decision


class JudgmentGuards(unittest.TestCase):
    def setUp(self):
        self.row = dict(informal_theorem="claim", informal_proof="argument",
                        header="", formal_proof="theorem example : True := by trivial",
                        formal_theorem="DO NOT SEND TEMPLATE", commented_proof="LEAKED EXPLANATION",
                        review_notes="SECRET LABEL", argument_match=True)

    def test_only_mathematical_evidence_is_sent(self):
        messages = build_messages(self.row, "rubric")
        self.assertEqual(messages[0], {"role": "system", "content": "rubric"})
        for forbidden in ("DO NOT SEND TEMPLATE", "LEAKED EXPLANATION", "SECRET LABEL", "argument_match"):
            self.assertNotIn(forbidden, messages[1]["content"])

    def test_absent_or_empty_proof_is_not_labeled_no(self):
        for value in (None, "", "  "):
            with self.subTest(value=value), self.assertRaises(ValueError):
                pair_payload({**self.row, "informal_proof": value})

    def test_false_and_missing_are_distinct(self):
        self.assertIs(parse_decision("NO"), False)
        self.assertIs(parse_decision(" yes\n"), True)
        for invalid in ("", "not yes", "YES because it matches", "uncertain", "<think>NO</think>YES"):
            self.assertIsNone(parse_decision(invalid))

    def test_input_not_modified(self):
        original = self.row.copy()
        build_messages(self.row, "rubric")
        self.assertEqual(self.row, original)


if __name__ == "__main__":
    unittest.main()
