import unittest

from stringerai.retrieval import KnowledgeBase, tokenize


class TokenizeTests(unittest.TestCase):
    def test_normalizes_punctuation_stopwords_and_plural_terms(self):
        self.assertEqual(tokenize("What are the majors?"), ["major"])


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.knowledge_base = KnowledgeBase([
            {
                "title": "Admissions deadlines",
                "text": "First-year application deadlines are published by admissions.",
            },
            {
                "title": "Campus library",
                "text": "The library offers research databases and study spaces.",
            },
        ])

    def test_retrieves_the_relevant_passage_first(self):
        results = self.knowledge_base.retrieve("admissions application deadline")
        self.assertEqual(results[0]["title"], "Admissions deadlines")

    def test_returns_empty_for_a_query_with_no_shared_terms(self):
        self.assertEqual(self.knowledge_base.retrieve("xylophone"), [])

    def test_dr_ali_query_returns_the_verified_wvsu_profile(self):
        knowledge_base = KnowledgeBase([
            {
                "title": "Dr. Ali Al-Sinayyid profile",
                "text": (
                    "Dr. Ali Al-Sinayyid is an Assistant Professor of Computer Science "
                    "and Director of the Cybersecurity Innovation Center."
                ),
            }
        ])
        answer = knowledge_base.build_answer("Who is Dr. Ali Al-Sinayyid?")
        self.assertIn("Assistant Professor", answer["answer"])
        self.assertEqual(answer["sources"], ["Dr. Ali Al-Sinayyid profile"])


if __name__ == "__main__":
    unittest.main()