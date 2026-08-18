"""
tests/test_api_server.py

Integration tests for FastAPI REST API endpoints using live test client.
"""
import unittest
import requests

BASE_URL = "http://localhost:8000"


class TestApiServer(unittest.TestCase):
    def test_health_endpoint(self):
        """Test GET /api/health."""
        response = requests.get(f"{BASE_URL}/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("total_reels", data)
        self.assertIn("total_users", data)

    def test_users_list_endpoint(self):
        """Test GET /api/users."""
        response = requests.get(f"{BASE_URL}/api/users")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
        self.assertGreater(len(data["users"]), 0)

    def test_user_profile_endpoint(self):
        """Test GET /api/users/{user_id}."""
        response = requests.get(f"{BASE_URL}/api/users/U000001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("progression_stage", data)

    def test_user_feed_endpoint(self):
        """Test GET /api/users/{user_id}/feed."""
        response = requests.get(f"{BASE_URL}/api/users/U000001/feed")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("history_reels", data)
        self.assertIn("feed_reels", data)

    def test_user_graph_endpoint(self):
        """Test GET /api/users/{user_id}/graph."""
        response = requests.get(f"{BASE_URL}/api/users/U000001/graph")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)

    def test_recommendation_endpoint(self):
        """Test POST /api/recommend."""
        payload = {
            "user_id": "U000001",
            "current_reel_id": "RL000001"
        }
        response = requests.post(f"{BASE_URL}/api/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("interest_detected", data)
        self.assertIn("recommended_title", data)

    def test_record_interaction_endpoint(self):
        """Test POST /api/interact."""
        payload = {
            "user_id": "U000001",
            "reel_id": "RL000001",
            "watch_percentage": 90,
            "liked": 1,
            "saved": 1,
            "shared": 0,
            "replayed": 0,
            "skipped": 0,
            "followed_creator": 0
        }
        response = requests.post(f"{BASE_URL}/api/interact", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_feedback_endpoint(self):
        """Test POST /api/feedback."""
        payload = {
            "user_id": "U000001",
            "feedback_type": "useful",
            "topic_or_category": "Backend"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "feedback_applied")

    def test_benchmark_traps_endpoint(self):
        """Test GET /api/benchmark/traps."""
        response = requests.get(f"{BASE_URL}/api/benchmark/traps")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(data["traps_passed"], 3)

    def test_taxonomy_stages_endpoint(self):
        """Test GET /api/taxonomy/stages."""
        response = requests.get(f"{BASE_URL}/api/taxonomy/stages")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stages", data)


if __name__ == "__main__":
    unittest.main()
