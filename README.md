# Website Summarizer

Command-line tool that fetches a web page, extracts its text, and asks an LLM to produce a short summary in markdown. The summary is written in a deliberately snarky tone, and navigation text is ignored.

## Features

- Fetches a page with a browser-like `User-Agent` header.
- Extracts the title and visible body text. Scripts, styles, images, and inputs are removed.
- Truncates content to 2,000 characters to keep the prompt small.
- Summarizes the page, including news and announcements if present.
- Provides a helper that returns all links found on a page.

## Project structure

```
.
├── scraper.py     # page fetching and parsing (requests + BeautifulSoup)
└── summarize.py   # prompt construction, LLM call, CLI entry point
```

## Requirements

- Python 3.9+
- OpenAI API key

```bash
pip install openai requests beautifulsoup4
```

## Configuration

Set the API key as an environment variable:

```bash
export OPENAI_API_KEY=your_openai_key
```

On Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="your_openai_key"
```

| Parameter | File | Purpose |
|---|---|---|
| `MODEL` | `summarize.py` | OpenAI model ID used for summarization |
| `system_prompt` | `summarize.py` | Tone and output format of the summary |
| `user_prompt_prefix` | `summarize.py` | Task instruction placed before the page text |
| `headers` | `scraper.py` | HTTP headers sent with each request |
| Truncation limit | `scraper.py` | `[:2_000]` in `fetch_website_contents` |

## Usage

```bash
python summarize.py
```

```
Enter a URL to summarize: https://example.com

Fetching and summarizing...

<markdown summary>
```

As a module:

```python
from summarize import summarize

print(summarize("https://example.com"))
```

## How it works

### `scraper.py`

| Function | Input | Output |
|---|---|---|
| `fetch_website_contents(url)` | URL | Title and body text, truncated to 2,000 characters |
| `fetch_website_links(url)` | URL | List of `href` values of all `<a>` tags (raw, not normalized) |

`fetch_website_contents` removes `script`, `style`, `img`, and `input` elements from the body before extracting text. If the page has no `<title>`, the string `No title found` is used.

### `summarize.py`

1. `fetch_website_contents` retrieves the cleaned page text.
2. `messages_for` builds a system message (role and style) and a user message (task and page content).
3. `summarize` sends the messages to the chat completions API and returns the response text.
4. `main` reads a URL from stdin and prints the summary.

## Known limitations

- Only the first 2,000 characters are summarized. Long pages are summarized from their beginning only.
- Pages rendered by JavaScript return little or no content, because `requests` does not execute scripts.
- Requests have no timeout and no error handling. A failing or hanging site raises an exception or blocks.
- HTTP status codes are not checked. Error pages (403, 404) are summarized as if they were content.
- `fetch_website_links` returns raw `href` values, including relative paths and anchors. It parses the page a second time when used together with `fetch_website_contents`.
- Some sites block automated requests regardless of the `User-Agent` header.

## License

Add a license of your choice.
