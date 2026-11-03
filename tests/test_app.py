import unittest

from stringerai import create_app


class ChatApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app({"TESTING": True})
        cls.client = cls.app.test_client()

    def test_homepage_renders_the_assistant(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"StringerAI", response.data)

    def test_frontend_assets_are_served(self):
        for asset_path in ("/static/styles.css", "/static/app.js"):
            with self.subTest(asset_path=asset_path):
                response = self.client.get(asset_path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_known_question_returns_answer_and_sources(self):
        response = self.client.post("/api/chat", json={"question": "When was WVSU founded?"})
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("1891", payload["answer"])
        self.assertIn("Founding and name changes", payload["sources"])

    def test_dr_ali_question_returns_verified_faculty_details(self):
        response = self.client.post(
            "/api/chat", json={"question": "Who is Dr. Ali Al-Sinayyid?"}
        )
        payload = response.get_json()
        self.assertIn("Assistant Professor of Computer Science", payload["answer"])
        self.assertIn("Dr. Ali Al-Sinayyid profile", payload["sources"])

    def test_cic_question_returns_lab_details(self):
        response = self.client.post(
            "/api/chat", json={"question": "What hands-on labs are at the CIC?"}
        )
        payload = response.get_json()
        self.assertIn("CyberHive", payload["answer"])
        self.assertIn("CIC hands-on cybersecurity labs", payload["sources"])

    def test_kail_question_returns_verified_contact_and_attributed_note(self):
        response = self.client.post(
            "/api/chat", json={"question": "Who is Ms. Kail?"}
        )
        payload = response.get_json()
        self.assertIn("Instructor in Mathematics and Computer Science", payload["answer"])
        self.assertIn("kkail@wvstateu.edu", payload["answer"])
        self.assertIn("304-766-4135", payload["answer"])
        self.assertIn("not an official WVSU statement", payload["answer"])
        self.assertIn("Ms. Karen Kail faculty listing", payload["sources"])

    def test_empty_question_returns_bad_request(self):
        response = self.client.post("/api/chat", json={"question": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["sources"], [])

    def test_non_object_json_returns_bad_request(self):
        response = self.client.post("/api/chat", json=["not", "an", "object"])
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()