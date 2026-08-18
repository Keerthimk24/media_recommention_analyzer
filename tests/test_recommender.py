"""
tests/test_recommender.py

Unit tests for RecommenderEngine, Schema Part A.9 explainability, and individual 89-student profiles.
"""
import os
import unittest
from backend.engine.taxonomy import TaxonomyGraph
from backend.engine.multimodal_analyzer import MultimodalAnalyzer
from backend.engine.interest_graph import UserInterestGraph
from backend.engine.recommender import RecommenderEngine
from backend.engine.user_recommendation_profiles import get_user_curated_recommendation


class TestRecommenderEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        csv_path = os.path.join(cls.data_dir, "technology_relationships.csv")
        cls.taxonomy = TaxonomyGraph(csv_path)
        cls.analyzer = MultimodalAnalyzer(cls.taxonomy)
        cls.recommender = RecommenderEngine(cls.analyzer, cls.taxonomy)

    def test_schema_part_a9_keys(self):
        """Verify generated recommendation adheres strictly to Part A.9 schema."""
        graph = UserInterestGraph("U000001", "English", self.taxonomy)
        rec = self.recommender.generate_recommendation(graph, current_reel={})
        
        required_fields = [
            "current_reel_title",
            "interest_detected",
            "why_evidence",
            "recommended_title",
            "category",
            "why_recommendation",
            "difficulty",
            "confidence"
        ]
        for field in required_fields:
            self.assertIn(field, rec, f"Missing required field {field} in recommendation output")

    def test_all_89_student_profiles_exist(self):
        """Verify all 89 individual student profiles are registered."""
        for i in range(1, 90):
            uid_short = f"U{i:03d}"
            uid_long = f"U{i:06d}"
            profile = get_user_curated_recommendation(uid_short)
            self.assertIsNotNone(profile, f"Profile for {uid_short} should exist")
            self.assertIsNotNone(get_user_curated_recommendation(uid_long), f"Profile for {uid_long} should exist")
            self.assertIn("primary", profile)
            self.assertIn("alternatives", profile)
            self.assertEqual(len(profile["alternatives"]), 4)


if __name__ == "__main__":
    unittest.main()
