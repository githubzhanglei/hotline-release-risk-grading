"""Boundary tests of the independent gate using synthetic candidate files."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from quality_gate import check_candidate


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.candidate = Path(self.temporary.name) / "synthetic_candidate.csv"

    def run_gate(self, rows, columns=("q",), qid_sets=None, k=3, n_in=None, **kwargs):
        with self.candidate.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(rows)
        return check_candidate(
            self.candidate, qid_sets=qid_sets or [[columns[0]]],
            n_in=len(rows) if n_in is None else n_in,
            snapshot_id="synthetic-boundary-test", k=k, **kwargs,
        )

    def test_k_minus_one_fails_and_k_passes(self):
        fail = self.run_gate([["x"], ["x"]])
        self.assertEqual(fail["automated_decision"], "FAIL")
        self.assertEqual(fail["records_below_k"], 2)
        passed = self.run_gate([["x"], ["x"], ["x"]])
        self.assertEqual(passed["automated_decision"], "PASS")
        self.assertEqual(passed["minimum_group_size"], 3)
        self.assertIsNone(passed["human_authorization"]["decision"])

    def test_missing_values_are_not_dropped(self):
        audit = self.run_gate([[""], [" "], [""]])
        self.assertEqual(audit["n_out"], 3)
        self.assertEqual(audit["minimum_group_size"], 3)
        self.assertEqual(audit["automated_decision"], "PASS")

    def test_literal_missing_marker_does_not_merge_with_missing(self):
        audit = self.run_gate([[""], [""], ["<MISSING>"], ["<MISSING>"]])
        self.assertEqual(audit["group_count"], 2)
        self.assertEqual(audit["automated_decision"], "FAIL")

    def test_new_delivery_column_requires_review(self):
        original = self.run_gate([["x"]] * 3)
        changed = self.run_gate([["x", "y"]] * 3, columns=("q", "extra"),
                                expected_column_hash=original["column_sha256"])
        self.assertNotEqual(changed["column_sha256"], original["column_sha256"])
        self.assertTrue(changed["column_review_required"])
        self.assertEqual(changed["automated_decision"], "FAIL")

    def test_empty_fully_suppressed_delivery_fails(self):
        audit = self.run_gate([], n_in=10)
        self.assertEqual(audit["n_out"], 0)
        self.assertEqual(audit["automated_decision"], "FAIL")
        self.assertTrue(any("Insufficient coverage" in reason for reason in audit["reasons"]))

    def test_separate_sets_pass_but_their_union_fails(self):
        rows = [["a", "x"], ["a", "y"], ["b", "x"], ["b", "y"]]
        a = self.run_gate(rows, columns=("a", "b"), qid_sets=[["a"]], k=2)
        b = self.run_gate(rows, columns=("a", "b"), qid_sets=[["b"]], k=2)
        union = self.run_gate(rows, columns=("a", "b"), qid_sets=[["a"], ["b"]], k=2)
        self.assertEqual(a["automated_decision"], "PASS")
        self.assertEqual(b["automated_decision"], "PASS")
        self.assertEqual(union["automated_decision"], "FAIL")
        self.assertEqual(union["singleton_count"], 4)

    def test_missing_declared_field_fails(self):
        audit = self.run_gate([["x"]] * 3, qid_sets=[["q", "absent"]])
        self.assertEqual(audit["automated_decision"], "FAIL")
        self.assertIsNone(audit["minimum_group_size"])

    def test_retention_requirement_is_checked(self):
        audit = self.run_gate([["x"]] * 3, n_in=10, minimum_retention=0.5)
        self.assertEqual(audit["automated_decision"], "FAIL")

    def test_impossible_input_count_fails(self):
        audit = self.run_gate([["x"]] * 3, n_in=2)
        self.assertEqual(audit["automated_decision"], "FAIL")

    def test_duplicate_delivery_headers_are_rejected(self):
        with self.assertRaises(ValueError):
            self.run_gate([["x", "x"]] * 3, columns=("q", "q"))


if __name__ == "__main__":
    unittest.main()
