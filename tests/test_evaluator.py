"""
tests/test_evaluator.py

Unit tests for 3/3 Adversarial Trap Benchmarks in BenchmarkEvaluator.
"""
import os
import unittest
from backend.engine.evaluator import BenchmarkEvaluator


class TestBenchmarkEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        cls.evaluator = BenchmarkEvaluator(cls.data_dir)

    def test_trap_benchmarks_all_pass(self):
        """Verify 100% (3/3) adversarial trap benchmarks pass."""
        summary = self.evaluator.run_all_traps()
        self.assertEqual(summary["traps_passed"], 3)
        self.assertTrue(summary["all_passed"])
        for trap_id, r in summary["results"].items():
            self.assertTrue(r["passed"], f"Trap test failed: {trap_id} - Output: {r.get('recommended_title')}")

    def test_trap_names_presence(self):
        """Verify all three trap benchmark IDs are evaluated."""
        summary = self.evaluator.run_all_traps()
        trap_names = set(summary["results"].keys())
        self.assertIn("TRAP_JAVA_BACKEND", trap_names)
        self.assertIn("TRAP_MULTILINGUAL", trap_names)
        self.assertIn("TRAP_ENTERTAINMENT_HEAVY", trap_names)


if __name__ == "__main__":
    unittest.main()
