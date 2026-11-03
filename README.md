# StringerAI: WVSU Assistant

A local, retrieval-based chatbot for West Virginia State University (WVSU). StringerAI pairs a small Flask API with a responsive chat interface and a source-attributed WVSU knowledge base.

## Project status
- Product name: **StringerAI: WVSU Assistant**
- Runtime: Python 3.10+ and Flask
- Answer method: local TF-IDF-style passage retrieval
- Model training: none; no external LLM or API key is required
- Current corpus: 32 passages, approximately 1,506 passage-text words, and 19 distinct source URLs

The corpus is curated retrieval content, not model-training data. Current counts are measured from `stringerai/data/wvsu_knowledge_base.json` and change when records change. It covers general university information, admissions, costs, housing, academics, the library, athletics, the Cybersecurity Innovation Center (CIC), and cybersecurity research. It is not a complete WVSU directory. Some entries are date-bound or refer to older/third-party information; verify critical details with WVSU.

## Quick start
Requires Python 3.10 or newer.

```bash
git clone https://github.com/Shikhar-ii/StringerAI.git
cd StringerAI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m stringerai
```

Open `http://127.0.0.1:5000`. The local server binds to loopback and runs with Flask debug mode disabled. Stop it with `Ctrl+C`.

Windows PowerShell activation uses `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

## Architecture
```text
.
├── app.py                         # WSGI-compatible entry point
├── pyproject.toml                 # package metadata and dependencies
├── stringerai/
│   ├── __init__.py                # Flask app factory and HTTP routes
│   ├── __main__.py                # python -m stringerai launcher
│   ├── retrieval.py               # tokenization, ranking, answer assembly
│   ├── data/wvsu_knowledge_base.json
│   ├── templates/index.html       # page structure
│   └── static/                    # browser behavior and visual theme
├── tests/                         # API and retrieval unit tests
└── docs/
  ├── knowledge-base.md          # human-readable reference notes
  └── wvsu-source-directory.md   # 113 official pages grouped by topic
```

### Request flow
1. `stringerai.create_app()` loads the canonical JSON corpus once during startup and builds a `KnowledgeBase` index.
2. The browser sends `{ "question": "..." }` to `POST /api/chat`.
3. `KnowledgeBase` lowercases and tokenizes the question and passage titles/text, removes stopwords, and applies a simple plural suffix rule.
4. It computes TF-IDF-style weighted vectors and cosine similarity, discards scores at or below `0.05`, and selects up to three passages.
5. The API joins the text from the two highest matches and returns their titles in `sources`. No generative model rewrites the response.
6. The frontend renders the answer and persists the light/dark preference in browser local storage.

The corpus includes a WVSU-verified profile for Dr. Ali Al-Sinayyid, so faculty questions are answered through normal retrieval. Empty or malformed question payloads return HTTP 400; unmatched questions receive a helpful no-match answer.

### API contract
Request:

```http
POST /api/chat
Content-Type: application/json

{"question":"When was WVSU founded?"}
```

Response:

```json
{
  "answer": "Founded in 1891 ...",
  "sources": ["Founding and name changes", "Mission"]
}
```

`GET /` serves the chat interface. The API returns passage titles, not source URLs, in its current form.

## Manage the knowledge base
The single active data source is `stringerai/data/wvsu_knowledge_base.json`. The Markdown notes in `docs/knowledge-base.md` and the categorized [WVSU source directory](docs/wvsu-source-directory.md) are for humans and are not loaded at runtime. The directory catalogs 113 unique official WVSU pages supplied for future expansion; listing a URL does not mean its contents are indexed. There is no crawler, automatic refresh, duplicate merge, embedding index, conversation learning, or chat-history persistence.

Each JSON record has this shape:

```json
{
  "id": 26,
  "category": "Admissions",
  "title": "Application deadlines",
  "text": "A focused, self-contained fact with relevant dates and qualifications.",
  "source": "https://wvstateu.edu/example-page/"
}
```

To add information:
1. Prefer a current official WVSU page or document; use third-party sources only when clearly labeled and necessary.
2. Split a long page or handbook into short, independent passages, one subject per record.
3. Add a unique integer `id`, a stable category, a specific title, factual text, and the exact source URL.
4. Include dates and qualifications for tuition, deadlines, programs, and policies. Avoid blending facts from different years.
5. Validate JSON and run the test suite:

```bash
python -m json.tool stringerai/data/wvsu_knowledge_base.json > /dev/null
python -m unittest discover -s tests -v
```

6. Restart the Flask app; data is loaded at process startup. Ask realistic questions and confirm the answer and `sources` are relevant.

The matcher relies on keyword overlap, so a useful title and wording that includes likely query terms materially improve retrieval. It does not read PDFs, scrape pages, or accept arbitrary documents automatically; extract and fact-check passages before adding them.

## Development and tests
Run the app in development with `python -m stringerai`. Run tests with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same test suite on pushes and pull requests. The package can also be hosted by a WSGI server using `stringerai:app`; configure the platform's bind address and worker settings there rather than enabling Flask debug mode.

## Data quality
The corpus currently spans 10 categories: General (9), Admissions (2), Costs (3), Housing (2), Academics (3), Library (5), Athletics (2), Centers (1), Faculty (1), and Research (4). All 32 entries have a source field, with 19 distinct URLs. These figures describe records currently checked into this repository; they are not a claim that the assistant has trained on or indexed every WVSU source.

Review high-impact and time-sensitive details regularly. For enrollment, financial, housing, deadline, and policy decisions, use the linked official WVSU source as the authority.

## Run in VS Code anytime
1. In VS Code, choose **File → Open Folder...** and open the `StringerAI` repository folder.
2. The first time only, open **Terminal → New Terminal** and create/install the project environment:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -e .
  ```

  In Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of the `source` command.
3. In VS Code, run **Python: Select Interpreter** from the Command Palette and choose the interpreter inside `.venv`.
4. Whenever you want to run the chatbot, open a new integrated terminal, activate `.venv` if it is not already active, and run:

  ```bash
  python -m stringerai
  ```

5. Open `http://127.0.0.1:5000` in your browser. Leave the terminal running while you use the app; press `Ctrl+C` there to stop it.
