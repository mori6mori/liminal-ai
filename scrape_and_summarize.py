#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-
"""scrape_and_summarize.py

End‑to‑end helper for the hackathon demo:
1. Fetch an article URL (e.g. https://arxiv.org/abs/1706.03762).
2. Extract the readable main text (Readability + BeautifulSoup).
3. Send that text to the OpenAI ChatCompletion endpoint with a prompt that
   returns JSON containing a section map and bite‑sized video transcripts.
4. Print the JSON (and optionally save it).

Works with **openai‑python ≥ 1.0.0** (new SDK). If you’re on an older version,
`pip install --upgrade openai`.

Dependencies:
    pip install requests readability-lxml beautifulsoup4 openai

Usage:
    export OPENAI_API_KEY="sk-..."
    python scrape_and_summarize.py https://arxiv.org/abs/1706.03762 -o transformer.json
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from readability import Document

# OpenAI ≥ 1.0.0 interface ---------------------------------------------
from openai import OpenAI  # pip install openai>=1.0.0

client = OpenAI()  # uses OPENAI_API_KEY env var

# -----------------------------------------------------------------------------
# 1.  Scrape & clean the article text
# -----------------------------------------------------------------------------

def fetch_article_text(url: str, max_chars: int = 12000) -> str:
    """Download *url* and return a cleaned, readable plain‑text body."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # --- arXiv shortcut (title + abstract) -----------------------------------
    if "arxiv.org" in url:
        soup = BeautifulSoup(html, "html.parser")
        abstract_block = soup.find("blockquote", class_="abstract")
        title_tag = soup.find("h1", class_="title")
        title = title_tag.get_text(strip=True).replace("Title:", "") if title_tag else ""
        if abstract_block:
            abstract = (
                abstract_block.get_text(" ", strip=True)
                .replace("Abstract:", "")
            )
            return f"{title}\n\n{abstract}"[:max_chars]

    # --- Generic websites via Readability ------------------------------------
    doc = Document(html)
    summary_html = doc.summary()
    title = doc.title() or ""

    soup = BeautifulSoup(summary_html, "html.parser")
    main_text = soup.get_text("\n", strip=True)
    return f"{title}\n\n{main_text}"[:max_chars]


# -----------------------------------------------------------------------------
# 2.  Build the LLM prompt & call OpenAI
# -----------------------------------------------------------------------------

SYSTEM_MSG = (
    "You are an expert explainer who turns dense academic papers into short, "
    "high‑engagement vertical‑video scripts for Gen‑Z."
)

# Escape braces in the JSON example by doubling them so str.format() ignores them
USER_TEMPLATE = textwrap.dedent(
    """
    Your task has two stages:\n\n
    **Stage A – Section map**\n
    Read the article text (between ```...```). Identify its 3-6 major conceptual sections.\n
    Return them as an ordered JSON array called "structure".\n\n
    **Stage B – Video transcripts**\n
    For each section you found:\n
    - Compress it into an ~100-130 word script for a 35-60 s video.\n
    - Hook the viewer in the first line, use clear metaphors, avoid jargon, second-person voice.\n
    - End with either a teaser or a punchy takeaway.\n\n
    Return exactly this JSON schema (minified, one line):\n
    {{\n      "structure": ["Section 1", "Section 2", "..."],\n      "transcripts": {{\n        "Section 1": "script ...",\n        ...\n      }}\n    }}\n\n
    ARTICLE\n    ```\n    {article_text}\n    ```
    """
)


def build_prompt(article_text: str) -> List[Dict[str, str]]:
    """Return a list of messages ready for chat.completions.create."""
    return [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": USER_TEMPLATE.format(article_text=article_text)},
    ]


def call_openai(prompt_messages: List[Dict[str, str]]) -> Dict:
    """Call OpenAI (new SDK) and return parsed JSON."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4o
        messages=prompt_messages,
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content.strip())


# -----------------------------------------------------------------------------
# 3.  CLI helper
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Generate bite‑sized video scripts from an article URL.")
    parser.add_argument("url", help="Article URL (e.g. https://arxiv.org/abs/1706.03762)")
    parser.add_argument("-o", "--out", type=Path, help="Save JSON output to file")
    args = parser.parse_args()

    print("[1/3] Fetching and cleaning article…", flush=True)
    article_text = fetch_article_text(args.url)

    print("[2/3] Building prompt and calling OpenAI…", flush=True)
    messages = build_prompt(article_text)

    try:
        result_json = call_openai(messages)
    except Exception as exc:
        print("⚠️  OpenAI API call failed:", exc)
        return

    pretty = json.dumps(result_json, indent=2, ensure_ascii=False)
    print("\n[3/3] LLM output:\n", pretty)

    if args.out:
        args.out.write_text(pretty, encoding="utf-8")
        print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()

