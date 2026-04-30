#!/usr/bin/env python3
"""Fetch recent papers from multiple public sources and create Jekyll posts.

Sources:
- arXiv metadata via the arxiv Python package
- bioRxiv metadata via the public bioRxiv API
- journal article metadata via the Crossref REST API
- alphaXiv links are added for arXiv papers as an additional discussion layer

The script uses metadata and abstracts only. It does not download or summarize PDFs.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import arxiv
from slugify import slugify

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
DATA_DIR = ROOT / "data"
SEEN_FILE = DATA_DIR / "seen_papers.json"

MAX_RESULTS = int(os.getenv("MAX_RESULTS", "25"))
MAX_NEW_POSTS = int(os.getenv("MAX_NEW_POSTS", "8"))
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "14"))
CROSSREF_MAILTO = os.getenv("CROSSREF_MAILTO", "")

KEYWORDS = [
    "peptide design",
    "cyclic peptide",
    "protein-protein interaction",
    "binding affinity prediction",
    "molecular docking",
    "molecular dynamics",
    "LC3",
    "LIR motif",
    "tetherin",
    "BST-2",
    "computational drug design",
    "protein binder design",
    "cell permeability peptide",
    "macrocyclic peptide",
]

ARXIV_QUERY = os.getenv(
    "ARXIV_QUERY",
    " OR ".join(f'all:"{keyword}"' for keyword in KEYWORDS),
)

# Journals that frequently publish papers relevant to computational biology,
# protein design, peptide/drug discovery, docking, MD, and chemical biology.
JOURNALS = [
    "Nature Biotechnology",
    "Nature Methods",
    "Nature Chemical Biology",
    "Nature Communications",
    "Communications Biology",
    "Science Advances",
    "Journal of Chemical Information and Modeling",
    "Journal of Medicinal Chemistry",
    "ACS Central Science",
    "ACS Chemical Biology",
    "Bioinformatics",
    "Briefings in Bioinformatics",
    "PLOS Computational Biology",
    "Nucleic Acids Research",
    "Structure",
    "Journal of Molecular Biology",
    "Protein Science",
    "Biophysical Journal",
    "Cell Systems",
]


@dataclass
class Paper:
    source: str
    uid: str
    title: str
    authors: list[str]
    published: date
    abstract: str = ""
    paper_url: str = ""
    pdf_url: str = ""
    journal: str = ""
    primary_category: str = ""
    tags: list[str] = field(default_factory=list)
    extra_links: dict[str, str] = field(default_factory=dict)


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
    escaped = clean_text(text).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_array(items: Iterable[str]) -> str:
    safe_items = []
    for item in items:
        item = clean_text(str(item))
        if item:
            safe_items.append(yaml_string(item))
    return "[" + ", ".join(safe_items) + "]"


def markdown_list(items: Iterable[str]) -> str:
    clean_items = [clean_text(str(item)) for item in items if clean_text(str(item))]
    return "\n".join(f"- {item}" for item in clean_items) if clean_items else "- None"


def http_json(url: str, *, timeout: int = 30) -> dict:
    headers = {
        "User-Agent": "min0210.github.io paper bot"
        + (f" (mailto:{CROSSREF_MAILTO})" if CROSSREF_MAILTO else ""),
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_arxiv_id(entry_id: str) -> str:
    return entry_id.rstrip("/").split("/")[-1]


def keyword_match(*texts: str) -> bool:
    haystack = " ".join(clean_text(text).lower() for text in texts)
    return any(keyword.lower() in haystack for keyword in KEYWORDS)


def fetch_arxiv_papers() -> list[Paper]:
    client = arxiv.Client(page_size=MAX_RESULTS, delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=ARXIV_QUERY,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers: list[Paper] = []
    for result in client.results(search):
        arxiv_id = parse_arxiv_id(result.entry_id)
        categories = result.categories or []
        tags = ["papers", "arxiv"] + [cat.replace(".", "-") for cat in categories[:4]]
        papers.append(
            Paper(
                source="arXiv",
                uid=f"arxiv:{arxiv_id}",
                title=clean_text(result.title),
                authors=[author.name for author in result.authors],
                published=result.published.astimezone(timezone.utc).date(),
                abstract=clean_text(result.summary),
                paper_url=result.entry_id,
                pdf_url=result.pdf_url or "",
                primary_category=result.primary_category or (categories[0] if categories else "arxiv"),
                tags=tags,
                extra_links={"alphaXiv": f"https://www.alphaxiv.org/abs/{arxiv_id}"},
            )
        )
    return papers


def fetch_biorxiv_papers() -> list[Paper]:
    # Official endpoint shape: /details/biorxiv/{N}d/0/json
    url = f"https://api.biorxiv.org/details/biorxiv/{LOOKBACK_DAYS}d/0/json"
    try:
        data = http_json(url)
    except Exception as exc:
        print(f"bioRxiv fetch failed: {exc}")
        return []

    papers: list[Paper] = []
    for item in data.get("collection", []):
        title = clean_text(item.get("title", ""))
        abstract = clean_text(item.get("abstract", ""))
        if not keyword_match(title, abstract, item.get("category", "")):
            continue

        doi = clean_text(item.get("doi", ""))
        paper_url = f"https://doi.org/{doi}" if doi else ""
        pdf_url = f"https://www.biorxiv.org/content/{doi}v{item.get('version', '1')}.full.pdf" if doi else ""
        try:
            published = datetime.strptime(item.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            published = datetime.now(timezone.utc).date()

        authors = [
            clean_text(author)
            for author in re.split(r";|,", item.get("authors", ""))
            if clean_text(author)
        ]

        papers.append(
            Paper(
                source="bioRxiv",
                uid=f"biorxiv:{doi or slugify(title)}",
                title=title,
                authors=authors,
                published=published,
                abstract=abstract,
                paper_url=paper_url,
                pdf_url=pdf_url,
                journal="bioRxiv",
                primary_category=clean_text(item.get("category", "bioRxiv")),
                tags=["papers", "biorxiv", slugify(item.get("category", "preprint"))],
            )
        )
    return papers


def crossref_date_parts_to_date(parts: list[list[int]] | None) -> date:
    if not parts or not parts[0]:
        return datetime.now(timezone.utc).date()
    values = parts[0]
    year = values[0]
    month = values[1] if len(values) > 1 else 1
    day = values[2] if len(values) > 2 else 1
    return date(year, month, day)


def fetch_crossref_journal_papers() -> list[Paper]:
    until = datetime.now(timezone.utc).date()
    since = until - timedelta(days=LOOKBACK_DAYS)
    rows_per_journal = max(3, min(10, MAX_RESULTS // 2))
    papers: list[Paper] = []

    for journal in JOURNALS:
        query = " OR ".join(KEYWORDS[:8])
        params = {
            "query.container-title": journal,
            "query.bibliographic": query,
            "filter": f"type:journal-article,from-pub-date:{since.isoformat()},until-pub-date:{until.isoformat()}",
            "select": "DOI,title,author,container-title,published-print,published-online,published,URL,abstract",
            "rows": str(rows_per_journal),
            "sort": "published",
            "order": "desc",
        }
        if CROSSREF_MAILTO:
            params["mailto"] = CROSSREF_MAILTO

        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        try:
            data = http_json(url)
        except Exception as exc:
            print(f"Crossref fetch failed for {journal}: {exc}")
            continue

        for item in data.get("message", {}).get("items", []):
            titles = item.get("title") or []
            title = clean_text(titles[0] if titles else "")
            abstract = clean_text(re.sub("<[^>]+>", " ", item.get("abstract", "")))
            if not title or not keyword_match(title, abstract):
                continue

            doi = clean_text(item.get("DOI", ""))
            container = item.get("container-title") or [journal]
            journal_name = clean_text(container[0] if container else journal)
            published = crossref_date_parts_to_date(
                item.get("published-online", {}).get("date-parts")
                or item.get("published-print", {}).get("date-parts")
                or item.get("published", {}).get("date-parts")
            )

            authors = []
            for author in item.get("author", [])[:12]:
                given = clean_text(author.get("given", ""))
                family = clean_text(author.get("family", ""))
                name = clean_text(f"{given} {family}")
                if name:
                    authors.append(name)

            papers.append(
                Paper(
                    source="Journal",
                    uid=f"doi:{doi or slugify(journal_name + '-' + title)}",
                    title=title,
                    authors=authors,
                    published=published,
                    abstract=abstract or "Abstract not available from Crossref metadata.",
                    paper_url=item.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
                    pdf_url="",
                    journal=journal_name,
                    primary_category="journal-article",
                    tags=["papers", "journal", slugify(journal_name)],
                )
            )

        time.sleep(1)

    return papers


def build_post(paper: Paper) -> tuple[str, str]:
    title = clean_text(paper.title)
    slug = slugify(title)[:90] or "paper"
    filename = f"{paper.published.isoformat()}-{slug}.md"

    tags = list(dict.fromkeys([tag for tag in paper.tags if tag]))
    front_matter = "\n".join(
        [
            "---",
            "layout: post",
            f"title: {yaml_string(title)}",
            f"date: {paper.published.isoformat()}",
            "categories: [papers]",
            f"tags: {yaml_array(tags)}",
            f"source: {yaml_string(paper.source)}",
            f"journal: {yaml_string(paper.journal)}",
            f"paper_url: {yaml_string(paper.paper_url)}",
            f"pdf_url: {yaml_string(paper.pdf_url)}",
            f"primary_category: {yaml_string(paper.primary_category)}",
            "---",
        ]
    )

    extra_link_lines = "\n".join(
        f"- **{name}:** [{url}]({url})" for name, url in paper.extra_links.items() if url
    )

    body = f"""{front_matter}

## Paper

- **Title:** {title}
- **Source:** {paper.source}
- **Journal / server:** {paper.journal or paper.source}
- **Authors:** {', '.join(paper.authors) if paper.authors else 'Unknown'}
- **Published:** {paper.published.isoformat()}
- **Category:** {paper.primary_category or 'N/A'}
- **Paper URL:** [{paper.paper_url}]({paper.paper_url})
"""

    if paper.pdf_url:
        body += f"- **PDF:** [{paper.pdf_url}]({paper.pdf_url})\n"

    if extra_link_lines:
        body += f"\n## Extra links\n\n{extra_link_lines}\n"

    body += f"""
## Abstract

{paper.abstract or 'Abstract not available from metadata.'}

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


def deduplicate_papers(papers: Iterable[Paper]) -> list[Paper]:
    seen: set[str] = set()
    unique: list[Paper] = []
    for paper in papers:
        key = paper.uid.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(paper)
    return sorted(unique, key=lambda paper: paper.published, reverse=True)


def main() -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    seen = load_seen()
    all_papers = deduplicate_papers(
        fetch_arxiv_papers()
        + fetch_biorxiv_papers()
        + fetch_crossref_journal_papers()
    )

    new_count = 0
    for paper in all_papers:
        if paper.uid in seen:
            continue

        filename, content = build_post(paper)
        post_path = POSTS_DIR / filename
        if post_path.exists():
            seen.add(paper.uid)
            continue

        post_path.write_text(content, encoding="utf-8")
        seen.add(paper.uid)
        new_count += 1

        if new_count >= MAX_NEW_POSTS:
            break

    save_seen(seen)
    print(f"Created {new_count} new paper post(s) at {datetime.now(timezone.utc).isoformat()}.")


if __name__ == "__main__":
    main()
