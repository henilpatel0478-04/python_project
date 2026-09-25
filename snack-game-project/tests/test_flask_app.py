"""
Unit tests for Snack Attack Flask Web Application & REST API endpoints.
"""
import os
import sys
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, load_high_score, save_high_score


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_check(self):
        """Verify API health check endpoint."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")

    def test_index_page(self):
        """Verify the main web portal HTML renders correctly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("SNACK ATTACK!", html)
        self.assertIn("gameCanvas", html)
        self.assertIn("FLASK REST API", html)

    def test_get_high_score(self):
        """Verify highscore retrieval endpoint."""
        response = self.client.get("/api/highscore")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIsInstance(data.get("high_score"), int)

    def test_get_snacks_endpoint(self):
        """Verify snack metadata endpoint returns all snack types."""
        response = self.client.get("/api/snacks")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        snacks = data.get("snacks")
        self.assertIsInstance(snacks, list)
        self.assertGreaterEqual(len(snacks), 5)
        # Check Apple and Chili presence
        snack_names = [s["name"] for s in snacks]
        self.assertTrue(any("Apple" in n for n in snack_names))
        self.assertTrue(any("Chili" in n for n in snack_names))

    def test_get_leaderboard(self):
        """Verify leaderboard endpoint returns top rankings."""
        response = self.client.get("/api/leaderboard")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        leaderboard = data.get("leaderboard")
        self.assertIsInstance(leaderboard, list)

    def test_submit_score(self):
        """Verify score submission and leaderboard update."""
        payload = {
            "player": "TestChampion",
            "score": 450,
            "difficulty": "Speedy",
            "snacks": 12
        }
        response = self.client.post("/api/score", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("rank", data)
        self.assertIn("leaderboard", data)
        self.assertTrue(any(e["name"] == "TestChampion" for e in data["leaderboard"]))


if __name__ == "__main__":
    unittest.main()
