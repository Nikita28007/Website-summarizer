# 🌐 Website Summarizer

> A CLI + web tool that scrapes any public webpage and produces a **short, snarky markdown summary** powered by the OpenAI API — built to explore LLM-driven content pipelines.

---

## ✨ What it does

1. Sends a real browser `User-Agent` header to fetch the target page (or uses a headless Chromium via **Playwright** for JS-heavy sites).
2. Parses the HTML with **BeautifulSoup**, strips all noise (`<script>`, `<style>`, `<img>`, `<input>`), and extracts clean visible text.
3. Truncates content to keep API costs low (2 000 chars for `requests`, 5 000 for Playwright).
4. Streams the response from **GPT-5.4-mini** (swappable via `--model` or `.env`) token-by-token.
5. Optionally persists summaries to **SQLite** or a **Markdown file**.
6. Ships a **FastAPI web UI** that streams the summary live in the browser.

---

## 🛠️ Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| HTTP client | `requests` / `playwright` (headless Chromium) |
| HTML parsing | `BeautifulSoup4` |
| LLM provider | OpenAI Chat Completions API (streaming) |
| Persistence | SQLite (stdlib `sqlite3`) |
| Web framework | FastAPI + Uvicorn |
| Config | `python-dotenv` |

---

## 📁 Project structure

```
website-summarizer/
├── scraper.py      # requests-based HTML fetcher (default, fast)
├── scraper_pw.py   # Playwright-based fetcher (JS-rendered pages)
├── summarize.py    # CLI — argparse, streaming, --model flag, export options
├── db.py           # SQLite persistence layer (save / list / get summaries)
├── exporter.py     # Markdown file export utility
├── app.py          # FastAPI web UI with live streaming
├── requirements.txt
├── .env.example    # Environment variable template (safe to commit)
├── .gitignore
└── README.md
```

---

## 🚀 Quick start

### 1 — Clone

```bash
git clone https://github.com/<your-username>/website-summarizer.git
cd website-summarizer
```

### 2 — Create a virtual environment

```bash
# macOS / Linux
python -m venv .venv && source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure your API key

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Open `.env` and paste your key:

```
OPENAI_API_KEY=sk-...
```

> **Never commit `.env`.** It is already listed in `.gitignore`.

---

## 💻 CLI usage

### Basic

```bash
python summarize.py https://news.ycombinator.com
```

### Pass URL as argument (no prompt)

```bash
python summarize.py https://example.com
```

### Stream tokens as they arrive

```bash
python summarize.py https://example.com --stream
```

### Override the model at runtime

```bash
python summarize.py https://example.com --model gpt-4o
```

### Use Playwright for JS-heavy pages

```bash
# Install browser once
playwright install chromium

python summarize.py https://react.dev --playwright
```

### Save to SQLite database

```bash
python summarize.py https://example.com --save-db
# → summaries.db is created automatically
```

### Append to a Markdown file

```bash
python summarize.py https://example.com --save-md summaries.md
```

### Combine flags

```bash
python summarize.py https://example.com \
  --model gpt-4o \
  --stream \
  --playwright \
  --save-db \
  --save-md output.md
```

### Full help

```bash
python summarize.py --help
```

```
usage: summarize [-h] [--model MODEL] [--stream] [--playwright]
                 [--save-db] [--save-md FILE]
                 [url]

positional arguments:
  url            URL to summarize. If omitted, you will be prompted.

options:
  --model MODEL  OpenAI model ID (default: gpt-5.4-mini)
  --stream       Stream tokens to stdout as they arrive
  --playwright   Use headless Chromium for JS-rendered pages
  --save-db      Persist the summary to summaries.db (SQLite)
  --save-md FILE Append the summary to FILE as a Markdown section
```

---

## 🌍 Web UI

```bash
uvicorn app:app --reload
```

Open **http://localhost:8000** — paste a URL, pick a model, and watch the summary stream live.

---

## 🔌 Use as a module

```python
from summarize import summarize

# Basic
summary = summarize("https://openai.com")

# With options
summary = summarize(
    "https://react.dev",
    model="gpt-4o",
    stream=True,
    use_playwright=True,
)
```

```python
from scraper import fetch_website_contents, fetch_website_links
from scraper_pw import fetch_website_contents as fetch_pw   # JS pages

from db import save_summary, list_summaries
from exporter import append_to_markdown
```

---

## ⚙️ Configuration

| Variable | Where | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | `.env` | — | **Required.** Your OpenAI secret key. |
| `MODEL` | `.env` | `gpt-5.4-mini` | Default model (overridden by `--model` flag). |
| `system_prompt` | `summarize.py` | snarky tone | LLM personality and output format. |
| `user_prompt_prefix` | `summarize.py` | see file | Task instruction prepended to page text. |
| Truncation limit | `scraper.py` | `2_000` chars | Raise to send more context. |
| Truncation limit | `scraper_pw.py` | `5_000` chars | Playwright renders more content. |

---

## 🗺️ Architecture

```
CLI / Web UI
     │
     ▼
summarize(url, model, stream, use_playwright)
     │
     ├─── scraper.py          requests + BeautifulSoup  (default)
     │    └─── scraper_pw.py  Playwright + BeautifulSoup (--playwright)
     │
     ▼
messages_for(website_text)
  ├─ system: snarky assistant prompt
  └─ user:   task + page text
     │
     ▼
openai.chat.completions.create(model, messages, stream=True/False)
     │
     ├──► stdout (CLI)
     ├──► StreamingResponse (FastAPI)
     ├──► db.save_summary()   → summaries.db
     └──► exporter.append_to_markdown() → *.md
```

---

## ⚠️ Known limitations

- **JavaScript-rendered pages** return little content with the default `requests` scraper — use `--playwright` for SPAs.
- **Only the first 2 000–5 000 characters** are summarized; long pages are summarized from their top only.
- **No timeout or retry logic** in `scraper.py` — a slow site will block indefinitely.
- **HTTP errors are not checked** — a 403 or 404 page is summarized as-is.
- **Some sites block** automated requests regardless of the `User-Agent` header.

---

## 📄 License

MIT — see [LICENSE](LICENSE) or add one of your choice.
