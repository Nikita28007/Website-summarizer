"""
Playwright-based scraper for JavaScript-rendered pages.

Install once:
    pip install playwright
    playwright install chromium
"""

from bs4 import BeautifulSoup


def fetch_website_contents(url: str) -> str:
    """
    Launch a headless Chromium browser, load *url*, wait for the network to
    settle, then extract and return the visible text (up to 5 000 characters).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ImportError(
            "Playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        ) from exc

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=15_000)
        title = page.title()
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    if soup.body:
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    # Playwright can render more content, so allow a larger window
    return (title + "\n\n" + text)[:5_000]


def fetch_website_links(url: str) -> list[str]:
    """Return all absolute href values found on the JS-rendered page."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ImportError(
            "Playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        ) from exc

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=15_000)
        links: list[str] = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)"
        )
        browser.close()
    return links

