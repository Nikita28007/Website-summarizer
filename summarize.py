"""
Website summarizer — fetches a page and produces a short, snarky markdown summary
using the OpenAI Chat Completions API.

Usage:
    python summarize.py https://example.com
    python summarize.py https://example.com --model gpt-4o --stream
    python summarize.py https://example.com --playwright --save-db --save-md summaries.md
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from prompts import SYSTEM_PROMPT, USER_PREFIX

# Load .env automatically so the project works right after `git clone`
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "gpt-5.4-mini")


def messages_for(website: str) -> list[dict]:
    """Build the message list sent to the LLM."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PREFIX + website},
    ]


def summarize(
    url: str,
    model: str = DEFAULT_MODEL,
    stream: bool = False,
    use_playwright: bool = False,
) -> str:
    """
    Fetch *url* and return a markdown summary from the LLM.

    Args:
        url:            Page to summarize.
        model:          OpenAI model ID to use.
        stream:         If True, tokens are printed as they arrive and the full
                        string is still returned.
        use_playwright: If True, use the Playwright-based scraper instead of
                        requests (handles JS-rendered pages).
    """
    if use_playwright:
        from scraper_pw import fetch_website_contents
    else:
        from scraper import fetch_website_contents

    client = OpenAI()
    website = fetch_website_contents(url)

    if stream:
        response = client.chat.completions.create(
            model=model,
            messages=messages_for(website),
            stream=True,
        )
        chunks: list[str] = []
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            chunks.append(delta)
        print()  # trailing newline after stream ends
        return "".join(chunks)

    response = client.chat.completions.create(
        model=model,
        messages=messages_for(website),
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="summarize",
        description="Summarize a webpage with a snarky LLM summary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python summarize.py https://news.ycombinator.com
  python summarize.py https://example.com --model gpt-4o --stream
  python summarize.py https://react.dev --playwright
  python summarize.py https://openai.com --save-db --save-md output.md
        """,
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL to summarize. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        metavar="MODEL",
        help=f"OpenAI model ID (default: {DEFAULT_MODEL}). Overrides the MODEL env var.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream tokens to stdout as they arrive instead of waiting for the full response.",
    )
    parser.add_argument(
        "--playwright",
        action="store_true",
        help=(
            "Use a headless Chromium browser (Playwright) to fetch the page. "
            "Required for JavaScript-rendered sites. "
            "Needs: pip install playwright && playwright install chromium"
        ),
    )
    parser.add_argument(
        "--save-db",
        action="store_true",
        help="Persist the summary to summaries.db (SQLite).",
    )
    parser.add_argument(
        "--save-md",
        metavar="FILE",
        help="Append the summary to FILE as a Markdown section.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    url = args.url or input("Enter a URL to summarize: ").strip()
    if not url:
        parser.print_help()
        sys.exit(1)

    print(f"\nFetching and summarizing with {args.model}...\n")

    summary = summarize(
        url,
        model=args.model,
        stream=args.stream,
        use_playwright=args.playwright,
    )

    if not args.stream:
        print(summary)

    if args.save_db:
        from db import save_summary
        row_id = save_summary(url=url, summary=summary, model=args.model)
        print(f"\n✓ Saved to summaries.db (id={row_id})")

    if args.save_md:
        from exporter import append_to_markdown
        append_to_markdown(filepath=args.save_md, url=url, summary=summary)
        print(f"\n✓ Appended to {args.save_md}")


if __name__ == "__main__":
    main()
