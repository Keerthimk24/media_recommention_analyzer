"""
tests/test_taxonomy.py

Unit tests for TaxonomyGraph and Learning Journey Progression.
"""
import os
import unittest
from backend.engine.taxonomy import (
    TaxonomyGraph,
    VALID_CATEGORIES,
    LEARNING_JOURNEY_STAGES,
    DOMAIN_ROLLUPS,
    PROGRAMMING_LANGUAGES,
    FRAMEWORKS,
    TECHNOLOGIES,
    CONCEPTS
)


class TestTaxonomyGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        csv_path = os.path.join(cls.data_dir, "technology_relationships.csv")
        cls.taxonomy = TaxonomyGraph(csv_path)

    def test_valid_categories(self):
        """Verify standard taxonomy categories exist."""
        expected = ["AI", "DSA", "Java", "HLD", "Cybersecurity", "Cloud", "Hardware", "Career", "Other"]
        self.assertEqual(VALID_CATEGORIES, expected)

    def test_learning_journey_stages(self):
        """Verify standard 7-stage learning journey."""
        self.assertEqual(len(LEARNING_JOURNEY_STAGES), 7)
        stages = [s["name"] for s in LEARNING_JOURNEY_STAGES]
        self.assertIn("Programming Basics", stages)
        self.assertIn("DSA & Problem Solving", stages)
        self.assertIn("Cloud & DevOps", stages)

    def test_domain_rollup_resolution(self):
        """Verify domain rollup mapping."""
        self.assertEqual(DOMAIN_ROLLUPS["Java"], "Software Engineering / Backend")
        self.assertEqual(DOMAIN_ROLLUPS["Python"], "AI / Data Science / Backend")
        self.assertEqual(DOMAIN_ROLLUPS["Docker"], "DevOps & Cloud Infrastructure")

    def test_category_enum_mapping(self):
        """Verify accurate mapping to Part A.9 CATEGORY enum."""
        cat_ai = self.taxonomy.map_to_category_enum("", "Python", "PyTorch", "", "How ML Engineers Deploy Models")
        self.assertEqual(cat_ai, "AI")
        cat_dsa = self.taxonomy.map_to_category_enum("DSA", "", "", "", "Binary Search Visualized")
        self.assertEqual(cat_dsa, "DSA")
        cat_hld = self.taxonomy.map_to_category_enum("HLD", "", "", "", "System Design: Consistent Hashing")
        self.assertEqual(cat_hld, "HLD")


if __name__ == "__main__":
    unittest.main()
