#!/usr/bin/env python3
"""Fetch recent arXiv papers and create Jekyll Markdown posts.

This script intentionally uses only public arXiv metadata and abstracts.
It does not download or summarize full PDFs.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import arxiv
from slugify import slugify

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
DATA_DIR = ROOT / "data"
SEEN_FILE = DATA_DIR / "seen_papers.json"

DEFAULT_QUERY = os.getenv(
    "ARXIV_QUERY",
    " OR ".join(
        [
            'all:"peptide design"',
            'all:"cyclic peptide"',
            'all:"protein protein interaction"',
            'all:"binding affinity prediction"',
            'all:"molecular docking"',
            'all:"molecular dynamics"',
            'all:"LC3"',
            'all:"LIR motif"',
            'all:"tetherin"',
            'all:"BST-2"',
            'all:"computational drug design"',
        ]
    ),
)

MAX_RESULTS = int(os.getenv("MAX_RESULTS", "15"))
MAX_NEW_POSTS = int(os.getenv("MAX_NEW_POSTS", "5"))


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    if isinstance(data, list):
        return set(str(item) for item in data)
    return set()


def save_seen(seen: Iterable[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(set(seen)), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def yaml_string(text: str) -> str:
    escaped = clean_text(text).replace('"', '\\"')
    return f'"{escaped}"'


def markdown_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_post(result: arxiv.Result) -> tuple[str, str]:
    published = result.published.astimezone(timezone.utc)
    date = published.date().isoformat()
    title = clean_text(result.title)
    slug = slugify(title)[:90] or "paper"
    filename = f"{date}-{slug}.md"

    authors = [author.name for author in result.authors]
    abstract = clean_text(result.summary)
    categories = result.categories or []
    tags = ["papers", "arxiv"] + [cat.replace(".", "-") for cat in categories[:4]]

    paper_url = result.entry_id
    pdf_url = result.pdf_url or ""
    primary_category = result.primary_category or (categories[0] if categories else "arxiv")

    front_matter = "\n".join(
        [
            "---",
            "layout: post",
            f"title: {yaml_string(title)}",
            f"date: {date}",
            "categories: [papers]",
            "tags: [" + ", ".join(tags) + "]",
            f"paper_url: {yaml_string(paper_url)}",
            f"pdf_url: {yaml_string(pdf_url)}",
            f"primary_category: {yaml_string(primary_category)}",
            "---",
        ]
    )

    body = f"""{front_matter}

## Paper

- **Title:** {title}
- **Authors:** {', '.join(authors) if authors else 'Unknown'}
- **Published:** {date}
- **Primary category:** {primary_category}
- **arXiv:** [{paper_url}]({paper_url})
- **PDF:** [{pdf_url}]({pdf_url})

## Abstract

{abstract}

## Structured note

### Problem

- What biological or computational problem does this paper address?

### Method

- What model, experiment, simulation, or dataset is used?

### Key result

- What is the main result or claim?

### Relevance to my research

- How could this connect to peptide design, binding prediction, docking, molecular dynamics, LC3/LIR, or tetherin projects?

## Tags

{markdown_list(tags)}
"""
    return filename, body


def fetch_papers() -> list[arxiv.Result]:
    client = arxiv.Client(page_size=MAX_RESULTS, delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=DEFAULT_QUERY,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    return list(client.results(search))


def main() -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    seen = load_seen()
    new_count = 0

    for result in fetch_papers():
        paper_id = result.entry_id
        if paper_id in seen:
            continue

        filename, content = build_post(result)
        post_path = POSTS_DIR / filename
        if post_path.exists():
            seen.add(paper_id)
            continue

        post_path.write_text(content, encoding="utf-8")
        seen.add(paper_id)
        new_count += 1

        if new_count >= MAX_NEW_POSTS:
            break

    save_seen(seen)
    print(f"Created {new_count} new paper post(s) at {datetime.now(timezone.utc).isoformat()}.")


if __name__ == "__main__":
    main()
