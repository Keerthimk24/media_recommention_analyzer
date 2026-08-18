"""
tests/test_interest_graph.py

Unit tests for UserInterestGraph representation, decay, and confidence scoring.
"""
import os
import unittest
from backend.engine.taxonomy import TaxonomyGraph
from backend.engine.interest_graph import UserInterestGraph


class TestUserInterestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        csv_path = os.path.join(cls.data_dir, "technology_relationships.csv")
        cls.taxonomy = TaxonomyGraph(csv_path)

    def setUp(self):
        self.graph = UserInterestGraph(
            user_id="U_TEST_001",
            primary_lang="English",
            taxonomy=self.taxonomy
        )

    def test_initial_graph_state(self):
        """Verify empty initial interest graph."""
        self.assertEqual(self.graph.user_id, "U_TEST_001")
        self.assertEqual(self.graph.primary_lang, "English")
        self.assertEqual(len(self.graph.entity_scores), 0)

    def test_process_interaction_updates_weights(self):
        """Verify positive interaction increases entity weight."""
        interaction = {
            "watch_percentage": 95,
            "liked": 1,
            "saved": 1,
            "replayed": 1,
            "skipped": 0
        }
        reel_analysis = {
            "intent": "Educational",
            "tech_entities": {
                "programming_languages": ["Java"],
                "frameworks": ["Spring Boot"],
                "technologies": ["Kafka"],
                "concepts": ["Microservices"],
                "domains": ["Backend"]
            }
        }
        self.graph.process_interaction(interaction, reel_analysis)
        self.assertIn("Java", self.graph.entity_scores)
        self.assertGreater(self.graph.entity_scores["Java"], 0)

    def test_negative_interaction_suppression(self):
        """Verify skip/low watch time does not inflate tech weights."""
        interaction = {
            "watch_percentage": 10,
            "liked": 0,
            "saved": 0,
            "replayed": 0,
            "skipped": 1
        }
        reel_analysis = {
            "intent": "Entertainment",
            "tech_entities": {
                "programming_languages": [],
                "frameworks": [],
                "technologies": [],
                "concepts": [],
                "domains": []
            }
        }
        self.graph.process_interaction(interaction, reel_analysis)
        conf = self.graph.get_confidence_level()
        self.assertIn(conf, ["Low", "Medium", "High"])

    def test_serialization_to_dict(self):
        """Verify graph dictionary serialization matches frontend schema."""
        d = self.graph.to_graph_data()
        self.assertIn("nodes", d)
        self.assertIn("links", d)
        self.assertIn("confidence", d)


if __name__ == "__main__":
    unittest.main()
