# StringerAI: WVSU Assistant

A local, retrieval-based chatbot for West Virginia State University (WVSU). StringerAI pairs a small Flask API with a responsive chat interface and a source-attributed WVSU knowledge base.

## Table of Contents

- [Project Status](#project-status)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Request Flow](#request-flow)
- [API Reference](#api-reference)
- [Managing the Knowledge Base](#managing-the-knowledge-base)
- [Development and Testing](#development-and-testing)
- [Data Quality](#data-quality)

## Project Status

| Item | Details |
|---|---|
| Product name | StringerAI: WVSU Assistant |
| Runtime | Python 3.10+ and Flask |
| Answer method | Local TF-IDF-style passage retrieval |
| Model training | None; no external LLM or API key is required |
| Current corpus | 33 passages, approximately 1,538 passage-text words, and 20 distinct source URLs |

The corpus is curated retrieval content, not model-training data. Current counts are measured from `stringerai/data/wvsu_knowledge_base.json` and change when records change.

**Coverage:** general university information, admissions, costs, housing, academics, the library, athletics, the Cybersecurity Innovation Center (CIC), and cybersecurity research.

> **Note:** This is not a complete WVSU directory. Some entries are date-bound or refer to older or third-party information. Verify critical details with WVSU.

## Quick Start

**Requirements:** Python 3.10 or newer.

```bash
git clone https://github.com/Shikhar-ii/StringerAI.git
cd StringerAI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m stringerai
```

Open <http://127.0.0.1:5000> in your browser. The local server binds to loopback and runs with Flask debug mode disabled. Stop it with `Ctrl+C`.

**Windows PowerShell:** activate the environment with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

## Architecture

```text
.
├── app.py                         # WSGI-compatible entry point
├── pyproject.toml                 # Package metadata and dependencies
├── stringerai/
│   ├── __init__.py                # Flask app factory and HTTP routes
│   ├── __main__.py                # `python -m stringerai` launcher
│   ├── retrieval.py               # Tokenization, ranking, answer assembly
│   ├── data/wvsu_knowledge_base.json
│   ├── templates/index.html       # Page structure
│   └── static/                    # Browser behavior and visual theme
├── tests/                         # API and retrieval unit tests
└── docs/
    ├── knowledge-base.md          # Human-readable reference notes
    └── wvsu-source-directory.md   # 114 official pages grouped by topic
```

## Request Flow

1. `stringerai.create_app()` loads the canonical JSON corpus once during startup and builds a `KnowledgeBase` index.
2. The browser sends `{ "question": "..." }` to `POST /api/chat`.
3. `KnowledgeBase` lowercases and tokenizes the question and the passage titles/text, removes stopwords, and applies a simple plural suffix rule.
4. It computes TF-IDF-style weighted vectors and cosine similarity, discards scores at or below 0.05, and selects up to three passages.
5. The API joins the text from the two highest matches and returns their titles in `sources`. No generative model rewrites the response.
6. The frontend renders the answer and persists the light/dark theme preference in browser local storage.

The corpus includes a WVSU-verified profile for Dr. Ali Al-Sinayyid, so faculty questions are answered through normal retrieval. Empty or malformed question payloads return HTTP 400. Unmatched questions receive a helpful no-match answer.

## API Reference

### `POST /api/chat`

**Request**

```http
POST /api/chat
Content-Type: application/json

{"question": "When was WVSU founded?"}
```

**Response**

```json
{
  "answer": "Founded in 1891 ...",
  "sources": ["Founding and name changes", "Mission"]
}
```

### `GET /`

Serves the chat interface.

> **Note:** In its current form, the API returns passage titles, not source URLs.

## Managing the Knowledge Base

The single active data source is `stringerai/data/wvsu_knowledge_base.json`.

The Markdown notes in `docs/knowledge-base.md` and the categorized WVSU source directory are for humans and are **not** loaded at runtime. The directory catalogs 114 unique official WVSU pages supplied for future expansion; listing a URL does not mean its contents are indexed.

**Not currently supported:** crawler, automatic refresh, duplicate merge, embedding index, conversation learning, and chat-history persistence.

### Record Format

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

### Adding Information

1. Prefer a current official WVSU page or document. Use third-party sources only when clearly labeled and necessary.
2. Split a long page or handbook into short, independent passages, one subject per record.
3. Add a unique integer `id`, a stable `category`, a specific `title`, factual `text`, and the exact `source` URL.
4. Include dates and qualifications for tuition, deadlines, programs, and policies. Avoid blending facts from different years.
5. Validate the JSON and run the test suite:

   ```bash
   python -m json.tool stringerai/data/wvsu_knowledge_base.json > /dev/null
   python -m unittest discover -s tests -v
   ```

6. Restart the Flask app, since data is loaded at process startup. Ask realistic questions and confirm the answer and sources are relevant.

The matcher relies on keyword overlap, so a useful title and wording that includes likely query terms materially improve retrieval. It does not read PDFs, scrape pages, or accept arbitrary documents automatically. Extract and fact-check passages before adding them.

## Development and Testing

Run the app in development:

```bash
python -m stringerai
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same test suite on pushes and pull requests. The package can also be hosted by a WSGI server using `stringerai:app`. Configure the platform's bind address and worker settings there rather than enabling Flask debug mode.

## Data Quality

The corpus currently spans 10 categories:

| Category | Entries |
|---|---|
| General | 9 |
| Library | 5 |
| Research | 4 |
| Costs | 3 |
| Academics | 3 |
| Admissions | 2 |
| Housing | 2 |
| Athletics | 2 |
| Faculty | 2 |
| Centers | 1 |
| **Total** | **33** |

All 33 entries have a `source` field, with 20 distinct URLs. These figures describe records currently checked into this repository. They are not a claim that the assistant has trained on or indexed every WVSU source.

Review high-impact and time-sensitive details regularly. For enrollment, financial, housing, deadline, and policy decisions, use the linked official WVSU source as the authority.

## Project Summary in 10 Points

1. **Purpose:** StringerAI is a local chatbot that answers questions about West Virginia State University (WVSU), covering general information, admissions, costs, housing, academics, the library, athletics, the CIC, faculty, and cybersecurity research.

2. **No model training:** The project does not train a model. There is no fine-tuning, no neural network, no external LLM, and no API key. The corpus is curated retrieval content, not training data.

3. **Inspired by RAG:** It follows the retrieval half of Retrieval-Augmented Generation. It finds relevant passages and returns them directly, with no generative model rewriting the response.

4. **Retrieval method:** Questions and passages are lowercased and tokenized, stopwords are removed, and a simple plural suffix rule is applied. Passages are ranked with TF-IDF-style weighted vectors and cosine similarity.

5. **Answer assembly:** Scores at or below 0.05 are discarded, and up to three passages are selected. The text of the two best matches forms the answer, and their titles are returned as `sources`.

6. **Knowledge base:** A single JSON file (`stringerai/data/wvsu_knowledge_base.json`) holds 33 passages across 10 categories, with about 1,538 words and 20 distinct official source URLs. Every record has an id, category, title, text, and source.

7. **Backend:** Python 3.10+ and Flask, with an app factory (`create_app()`) and a `POST /api/chat` endpoint. Invalid or empty payloads return HTTP 400, and unmatched questions get a helpful no-match answer.

8. **Frontend:** A responsive chat interface built with HTML, CSS, and JavaScript, with a light/dark theme saved in browser local storage. Languages by share: Python 43.9%, CSS 34.5%, JavaScript 11.1%, HTML 10.5%.

9. **Quality and tooling:** Unit tests (`unittest`) cover the API and retrieval, and GitHub Actions runs them on every push and pull request. Packaging uses `pyproject.toml`, and a WSGI entry point (`app.py`) supports hosting.

10. **Limitations and future work:** There is no crawler, auto-refresh, embeddings, conversation learning, or chat-history storage. The 114 cataloged official WVSU pages are listed for future expansion but are not yet indexed. Verify critical details with the linked official WVSU sources.
