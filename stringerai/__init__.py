"""Flask application for the StringerAI WVSU Assistant."""

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .retrieval import KnowledgeBase


PACKAGE_DIR = Path(__file__).resolve().parent


def create_app(config=None):
	app = Flask(__name__)
	app.config.from_mapping(
		KNOWLEDGE_BASE_PATH=PACKAGE_DIR / "data" / "wvsu_knowledge_base.json",
	)
	if config:
		app.config.update(config)

	knowledge_path = Path(app.config["KNOWLEDGE_BASE_PATH"])
	with knowledge_path.open("r", encoding="utf-8") as source_file:
		entries = json.load(source_file)
	knowledge_base = KnowledgeBase(entries)
	app.extensions["knowledge_base"] = knowledge_base

	@app.get("/")
	def index():
		return render_template("index.html")

	@app.post("/api/chat")
	def chat():
		data = request.get_json(silent=True) or {}
		if not isinstance(data, dict):
			data = {}
		question = (data.get("question") or "").strip()
		if not question:
			return jsonify({"answer": "Please ask a question about WVSU.", "sources": []}), 400
		return jsonify(knowledge_base.build_answer(question))

	return app


app = create_app()