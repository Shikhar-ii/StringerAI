import math
import re


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "to", "in", "on", "for",
    "and", "or", "at", "by", "with", "from", "about", "what", "who", "how", "when",
    "where", "which", "do", "does", "can", "i", "you", "it", "its", "be", "as",
    "that", "this", "there", "tell", "me", "my", "your", "we", "us", "our", "they",
    "them", "their", "not", "no", "yes", "did", "have", "has", "had", "into", "over",
    "under", "after", "before", "should", "could", "would", "may", "might", "because",
    "around", "using", "just", "some", "any", "each", "every", "more", "less", "than",
    "also", "very", "many", "much", "most", "out", "up", "down", "again",
}


def tokenize(text):
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    tokens = []
    for word in words:
        if word in STOPWORDS:
            continue
        if len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        tokens.append(word)
    return tokens


class KnowledgeBase:
    def __init__(self, entries):
        self.entries = entries
        self.documents = [
            tokenize(f"{entry['title']} {entry['text']}") for entry in entries
        ]
        self.document_frequency = {}
        for words in self.documents:
            for word in set(words):
                self.document_frequency[word] = self.document_frequency.get(word, 0) + 1
        self.vectors = [self._make_vector(words) for words in self.documents]
        self.magnitudes = [
            math.sqrt(sum(weight * weight for weight in vector.values())) or 1
            for vector in self.vectors
        ]

    def _idf(self, word):
        return math.log(1 + len(self.documents) / self.document_frequency.get(word, 0.5))

    def _make_vector(self, words):
        vector = {}
        for word in words:
            vector[word] = vector.get(word, 0) + 1
        for word in vector:
            vector[word] *= self._idf(word)
        return vector

    def retrieve(self, query, limit=3):
        if not query:
            return []

        query_vector = self._make_vector(tokenize(query))
        query_magnitude = math.sqrt(
            sum(weight * weight for weight in query_vector.values())
        ) or 1
        scored = []

        for index, vector in enumerate(self.vectors):
            dot_product = sum(
                weight * vector.get(word, 0)
                for word, weight in query_vector.items()
            )
            similarity = dot_product / (query_magnitude * self.magnitudes[index])
            if similarity > 0.05:
                scored.append((index, similarity))

        scored.sort(key=lambda result: result[1], reverse=True)
        return [self.entries[index] for index, _ in scored[:limit]]

    def build_answer(self, question):
        matches = self.retrieve(question)
        if not matches:
            return {
                "answer": (
                    "I couldn’t find a strong match for that in the WVSU knowledge base. "
                    "Try asking about admissions, tuition, majors, athletics, campus life, "
                    "or check wvstateu.edu for the latest official details."
                ),
                "sources": [],
            }

        answer = " ".join(entry["text"] for entry in matches[:2])
        if re.search(r"\b(?:karen|kail)\b", question or "", re.IGNORECASE):
            answer += (
                " Playful note from the project owner, Shikhar (not an official "
                "WVSU statement): Karen is the best professor."
            )

        return {
            "answer": answer,
            "sources": [entry["title"] for entry in matches],
        }