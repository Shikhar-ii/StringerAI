# StringerJPT

StringerJPT is a local West Virginia State University (WVSU) question-answering chatbot. It combines a Flask API, a browser-based chat interface, and a small curated knowledge base.

## What it does
You submit a question in the chat UI. The browser sends it to Flask at `/api/chat`; Flask ranks the stored WVSU passages and returns an answer with matching passage titles. The interface displays the conversation and lets you switch between light and dark themes.

This project does **not** train or fine-tune an AI model and does not call an external LLM. “Knowledge base” or “retrieval corpus” is more accurate than “training data.”

## Current knowledge-base size
Measured from the active `wvsu_knowledge_base.json` in this workspace:

- 25 retrieval passages
- 1,021 whitespace-separated words across passage text (approximate size; changes when entries change)
- 7,267 characters across passage text
- 25 passages include a source field
- 16 distinct source URLs

These are curated text records, not 25 documents or model-training examples. The count describes the current checked-out data and will change as the corpus is edited. Records are grouped as follows:

| Category | Passages |
| --- | ---: |
| General | 9 |
| Admissions | 2 |
| Costs | 3 |
| Housing | 2 |
| Academics | 2 |
| Library | 5 |
| Athletics | 2 |

The knowledge base is a starting point, not comprehensive coverage of every WVSU page, person, department, or policy. Some facts are year-specific or may come from older or third-party references. Confirm time-sensitive information with WVSU.

## How answering works
1. `app.py` loads the JSON knowledge base once when the Flask process starts.
2. The question and each entry's title and text are lowercased, punctuation is removed, common stopwords are filtered, and some trailing plural `s` characters are trimmed.
3. The app builds TF-IDF-style term vectors. In this implementation, inverse document frequency is calculated as `log(1 + number_of_passages / document_frequency)`.
4. It calculates cosine similarity between the question vector and each passage vector, keeps scores above `0.05`, and selects at most the three highest-scoring passages.
5. The answer text joins the text of the top two passages. The response's `sources` list contains the titles of the matched passages (up to three).
6. The browser renders the response. The backend does not generate new facts or paraphrase with an LLM; the answer is assembled from stored passage text.

There is a specific fallback response for “Dr. Ali” queries. Other questions without a match receive a general no-match response.

### What the retrieval system does not do
- It does not learn from chat messages or retain conversation history.
- It does not crawl or automatically refresh WVSU pages.
- It does not create embeddings or use a vector database.
- It does not currently return clickable source URLs in the chat response; it returns matching passage titles.
- It does not understand facts that are absent from its loaded JSON corpus.

## Add more WVSU knowledge
The active corpus is the root-level `wvsu_knowledge_base.json`. Add each fact as a focused passage, preferably one subject per entry. Use official WVSU pages first, especially for tuition, deadlines, programs, contacts, and policies. Keep the text self-contained, preserve the exact source URL, and note the relevant academic year in the title or text for changing facts.

Each active record uses this schema:

```json
{
  "id": 26,
  "category": "Admissions",
  "title": "Example admissions topic",
  "text": "A concise, factual passage that directly answers likely questions.",
  "source": "https://wvstateu.edu/example-page/"
}
```

To add entries:
1. Open `wvsu_knowledge_base.json` in the repository root.
2. Add a comma after the previous record, then add a new object before the closing `]`.
3. Assign a unique integer `id`; use a useful category and specific title.
4. Write a focused `text` passage containing enough context to make it understandable on its own.
5. Set `source` to the page or document URL used to verify the fact. Do not invent a URL. For information from a provided document without a public URL, use an accurate document name and location only if the schema or code is later extended to support that; currently `source` is treated as a string.
6. Save and validate the JSON. Restart Flask so it reloads the corpus, then test questions using the wording people are likely to ask.

Example validation and app run, from the `wvsu-chatbot` directory:

```bash
python3 -m json.tool ../wvsu_knowledge_base.json > /dev/null
python3 app.py
```

Try the app at `http://localhost:5000`. You can also test the chat endpoint:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"What are the undergraduate tuition costs?"}'
```

After adding data, verify that the answer is relevant, its passage title appears in `sources`, and old questions still work. If the record is not retrieved, revise the title/text to include the key terms in the question. This implementation uses simple token overlap and is sensitive to wording.

### Adding larger source collections
For a long webpage, handbook, or PDF, do not paste an entire document into one entry. Extract the relevant factual sections and split them into concise, independently useful passages. Keep a source reference for every passage. Review dates, fees, deadlines, and policies before adding them. This repository does not currently provide document parsing, web scraping, automatic synchronization, or duplicate detection; those capabilities would require additional implementation.

### Which knowledge file is active?
At startup, `app.py` prefers the root file `wvsu_knowledge_base.json`. Only if that file does not exist does it load `wvsu-chatbot/data/wvsu_kb.json` as a fallback. The root file currently has 25 records; the fallback has 26 records with a simpler `title`/`text` schema. The two files are not combined, and their record counts must not be added together. The Markdown file `wvsu_knowledge_base.md` is reference documentation and is not loaded by the application.

Add new material to the root JSON file to change the data the running app uses. If you intentionally remove or rename the root file, check that the fallback data has the content and fields you want before starting the app.

## Run locally
Requirements: Python 3 and the packages in `wvsu-chatbot/requirements.txt`.

```bash
cd wvsu-chatbot
python3 -m pip install -r requirements.txt
python3 app.py
```

Open `http://localhost:5000`. To stop the server, press `Ctrl+C` in its terminal. Flask runs in debug mode as configured in `app.py`; use an appropriate production server and deployment configuration before exposing this prototype publicly.

## Project files
- `wvsu-chatbot/app.py`: Flask routes, knowledge-base loading, tokenization, TF-IDF-style ranking, and response assembly.
- `wvsu-chatbot/templates/index.html`: chat page structure and existing UI controls.
- `wvsu-chatbot/static/styles.css`: layout, responsive styling, and light/dark theme colors.
- `wvsu-chatbot/static/app.js`: browser-side chat submission, message rendering, quick prompts, and theme persistence.
- `wvsu_knowledge_base.json`: active runtime data, including categories and source URLs.
- `wvsu-chatbot/data/wvsu_kb.json`: fallback corpus used only when the root JSON file is absent.
- `wvsu_knowledge_base.md`: human-readable reference material; not loaded at runtime.
- `wvsu-chatbot/requirements.txt`: Python dependencies (Flask).
- `wvsu-chatbot/README.md`: app-folder setup notes and link to this guide.

## Data quality and responsible use
Prefer current primary sources and include the exact URL for each fact. Separate facts with different dates or qualifications into clear passages so retrieval does not combine incompatible details. Review the corpus periodically, especially costs, deadlines, program offerings, staff directories, and policies. Do not treat generated-looking answers as official advice; verify important decisions with WVSU.
