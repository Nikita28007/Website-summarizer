"""
Export utilities — append summaries to a Markdown file.
"""

from datetime import datetime, timezone
from pathlib import Path


def append_to_markdown(filepath: str, url: str, summary: str) -> None:
    """
    Append a summary block to *filepath* (creates the file if it does not exist).

    Each block looks like:

        ---

        ## https://example.com

        *2024-05-10 14:32 UTC*

        <summary text>
    """
    path = Path(filepath)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    block = f"\n---\n\n## {url}\n\n*{timestamp}*\n\n{summary}\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)

