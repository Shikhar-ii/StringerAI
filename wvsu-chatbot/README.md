# StringerJPT – WVSU Assistant

StringerJPT is a Flask-based chatbot that searches a curated collection of WVSU facts and displays the best matches in a web chat interface.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Run these commands from this directory, then open `http://localhost:5000`.

## Current data size
The active root knowledge base currently contains 25 passages, approximately 1,021 words of passage text, and 16 distinct source URLs. This is retrieval content, not model-training data: the project does not train a model or call an external LLM.

## Add or update knowledge
Edit `../wvsu_knowledge_base.json`, which is the active data file. Add a JSON object with a unique `id`, `category`, `title`, `text`, and verified `source` URL. Keep each passage focused on one topic. Validate it with:

```bash
python3 -m json.tool ../wvsu_knowledge_base.json > /dev/null
```

Restart the Flask process after changing the file. The app loads data at startup and does not crawl or refresh source pages automatically. The `data/wvsu_kb.json` file is a fallback used only when the root knowledge base is missing; the two files are not merged.

## Complete documentation
See the [project README](../README.md) for the retrieval algorithm, measured dataset details, schema example, instructions for expanding the corpus, source-quality guidance, file responsibilities, and known limitations.
