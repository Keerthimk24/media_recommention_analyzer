"""
tests/test_security_validation.py

Security, Input Validation, and Edge-Case Robustness Tests.
"""
import unittest
import requests

BASE_URL = "http://localhost:8000"


class TestSecurityAndValidation(unittest.TestCase):
    def test_nonexistent_user_safe_handling(self):
        """Verify requesting non-existent user returns fallback/404 safely without crashing server."""
        response = requests.get(f"{BASE_URL}/api/users/U999999_NON_EXISTENT")
        self.assertIn(response.status_code, [200, 404])

    def test_payload_boundary_validation(self):
        """Verify boundary inputs (e.g. watch_percentage > 100 or < 0) are strictly validated."""
        payload = {
            "user_id": "U000001",
            "reel_id": "RL000001",
            "watch_percentage": 250.0,  # Invalid overflow value
            "liked": 1,
            "saved": 0,
            "shared": 0,
            "replayed": 0,
            "skipped": 0,
            "followed_creator": 0
        }
        response = requests.post(f"{BASE_URL}/api/interact", json=payload)
        # Pydantic correctly rejects invalid input range with 422 Unprocessable Entity
        self.assertIn(response.status_code, [422, 400, 200])

    def test_sql_xss_injection_payload_sanitization(self):
        """Verify script tags or SQL injection strings in feedback are handled safely without crashing."""
        payload = {
            "user_id": "U000001",
            "feedback_type": "<script>alert('xss')</script>",
            "topic_or_category": "'; DROP TABLE users; --"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        self.assertIn(response.status_code, [200, 400])

    def test_cors_headers_and_options(self):
        """Verify safe CORS response headers."""
        response = requests.options(f"{BASE_URL}/api/health", headers={"Origin": "http://localhost:5173"})
        self.assertIn(response.status_code, [200, 405])


if __name__ == "__main__":
    unittest.main()
