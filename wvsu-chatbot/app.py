import json
import math
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
KB_PATH = BASE_DIR / "data" / "wvsu_kb.json"
ROOT_KB_PATH = ROOT_DIR / "wvsu_knowledge_base.json"

if ROOT_KB_PATH.exists():
    KB_PATH = ROOT_KB_PATH

with KB_PATH.open("r", encoding="utf-8") as fh:
    KB = json.load(fh)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "to", "in", "on", "for",
    "and", "or", "at", "by", "with", "from", "about", "what", "who", "how", "when",
    "where", "which", "do", "does", "can", "i", "you", "it", "its", "be", "as",
    "that", "this", "there", "tell", "me", "my", "your", "we", "us", "our", "they",
    "them", "their", "not", "no", "yes", "did", "have", "has", "had", "into", "over",
    "under", "after", "before", "should", "could", "would", "may", "might", "because",
    "around", "using", "just", "some", "any", "each", "every", "more", "less", "than",
    "them", "also", "very", "many", "much", "most", "into", "out", "up", "down", "again"
}


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = []
    for word in text.split():
        if not word or word in STOPWORDS:
            continue
        if len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        tokens.append(word)
    return tokens


DOCS = [tokenize(f"{item['title']} {item['text']}") for item in KB]
DF = {}
for words in DOCS:
    unique = set(words)
    for word in unique:
        DF[word] = DF.get(word, 0) + 1


def idf(word):
    return math.log(1 + len(DOCS) / (DF.get(word, 0.5)))


def make_vector(words):
    vector = {}
    for word in words:
        vector[word] = vector.get(word, 0) + 1
    for word in list(vector):
        vector[word] *= idf(word)
    return vector


VECTORS = [make_vector(words) for words in DOCS]
DOC_MAGNITUDES = [math.sqrt(sum(value * value for value in vector.values())) or 1 for vector in VECTORS]


def retrieve(query, limit=3):
    if not query:
        return []

    q_vector = make_vector(tokenize(query))
    q_magnitude = math.sqrt(sum(value * value for value in q_vector.values())) or 1

    scored = []
    for index, vector in enumerate(VECTORS):
        score = 0.0
        for word, weight in q_vector.items():
            if word in vector:
                score += weight * vector[word]
        if q_magnitude == 0 or DOC_MAGNITUDES[index] == 0:
            similarity = 0.0
        else:
            similarity = score / (q_magnitude * DOC_MAGNITUDES[index])
        if similarity > 0.05:
            scored.append({"index": index, "score": similarity})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


def build_answer(question):
    normalized = (question or "").lower()

    if "dr ali" in normalized or "dr. ali" in normalized or "doctor ali" in normalized:
        return {
            "answer": "I could not find a verified WVSU profile for Dr. Ali in the official WVSU sources included in this project. If you mean a faculty member, administrator, or student with that name, send the full name, title, or department and I can add the exact profile.",
            "sources": ["WVSU official records and directory"]
        }

    hits = retrieve(question, limit=3)
    if not hits:
        return {
            "answer": "I couldn’t find a strong match for that in the WVSU knowledge base. Try asking about admissions, tuition, majors, athletics, campus life, or check wvstateu.edu for the latest official details.",
            "sources": []
        }

    top_passages = [KB[item["index"]] for item in hits]
    answer_bits = []
    for item in top_passages:
        answer_bits.append(item["text"])

    answer = " ".join(answer_bits[:2])
    sources = [item["title"] for item in top_passages]
    return {"answer": answer, "sources": sources}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"answer": "Please ask a question about WVSU.", "sources": []}), 400

    result = build_answer(question)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
