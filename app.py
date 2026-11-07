"""
Lightweight FastAPI web interface for the Website Summarizer.

Run:
    uvicorn app:app --reload

Then open http://localhost:8000 in your browser.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI

from prompts import SYSTEM_PROMPT, USER_PREFIX
from scraper import fetch_website_contents

load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "gpt-5.4-mini")

app = FastAPI(title="Website Summarizer")
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "default_model": DEFAULT_MODEL},
    )


@app.post("/summarize/stream")
async def summarize_stream(
    url: str = Form(...),
    model: str = Form(DEFAULT_MODEL),
) -> StreamingResponse:
    """Stream the LLM summary token by token to the browser."""
    website = fetch_website_contents(url)
    client = OpenAI()

    def _generate():
        for chunk in client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PREFIX + website},
            ],
            stream=True,
        ):
            yield chunk.choices[0].delta.content or ""

    return StreamingResponse(_generate(), media_type="text/plain; charset=utf-8")
