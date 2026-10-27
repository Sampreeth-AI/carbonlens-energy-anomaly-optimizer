import unittest
from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_demo_analysis(self):
        response = self.client.post("/api/v1/demo")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json["run"]["anomaly_count"], 0)
        self.assertEqual(response.json["run"]["total_rows"], 336)


if __name__ == "__main__": unittest.main()
