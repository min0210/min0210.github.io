#!/usr/bin/env python3
"""Fetch recent papers from curated sources and create Jekyll posts.

Default sources:
- arXiv metadata via the arxiv Python package
- bioRxiv metadata via the public bioRxiv API
- alphaXiv links are added for arXiv papers as an additional discussion layer

Crossref journal metadata is disabled by default because it can be noisy for this blog.
Enable it only when needed with ENABLE_CROSSREF=1.

The script uses metadata and abstracts only. It does not download or summarize PDFs.
Generated posts are explanatory abstract-based paper notes, not empty protocol placeholders.
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
MAX_NEW_POSTS = int(os.getenv("MAX_NEW_POSTS", "3"))
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "14"))
MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", "6"))
ENABLE_CROSSREF = os.getenv("ENABLE_CROSSREF", "0") == "1"
CROSSREF_MAILTO = os.getenv("CROSSREF_MAILTO", "")

INTERACTION_GROUPS = {
    "protein-ligand": {
        "weight": 3,
        "keywords": [
            "protein-ligand",
            "protein ligand",
            "small molecule",
            "ligand binding",
            "binding pose",
            "pose prediction",
            "molecular docking",
            "docking score",
            "virtual screening",
            "hit discovery",
            "lead optimization",
            "binding free energy",
            "free energy perturbation",
            "alchemical free energy",
            "FEP",
            "MM-PBSA",
            "MM-GBSA",
            "structure-based drug design",
            "ligand-based drug design",
            "fragment-based drug discovery",
            "covalent inhibitor",
        ],
    },
    "protein-protein": {
        "weight": 4,
        "keywords": [
            "protein-protein interaction",
            "protein protein interaction",
            "PPI",
            "protein interface",
            "interface design",
            "protein binder",
            "protein binder design",
            "de novo protein binder",
            "protein complex",
            "protein-protein docking",
            "protein interaction modulation",
            "binder design",
        ],
    },
    "protein-peptide": {
        "weight": 5,
        "keywords": [
            "protein-peptide",
            "protein peptide",
            "peptide binding",
            "peptide design",
            "cyclic peptide",
            "macrocyclic peptide",
            "peptide binder",
            "peptide-protein interaction",
            "cell permeability peptide",
            "peptide permeability",
            "N-methylation",
            "non-canonical amino acid",
            "LIR motif",
            "LC3",
            "autophagy receptor",
            "tetherin",
            "BST-2",
        ],
    },
}

METHOD_KEYWORDS = {
    "weight": 1,
    "keywords": [
        "molecular dynamics",
        "enhanced sampling",
        "diffusion model",
        "flow matching",
        "generative model",
        "generative molecular design",
        "molecular generation",
        "molecular representation learning",
        "active learning",
        "retrosynthesis",
        "synthesis-aware design",
        "computer-aided drug design",
        "CADD",
        "AI drug discovery",
    ],
}

IMPORTANT_TARGET_KEYWORDS = {
    "weight": 6,
    "keywords": ["LC3", "LIR motif", "tetherin", "BST-2", "autophagy"],
}

# Protein-ligand papers are accepted only when at least one anchor term is also present.
# This avoids generic small-molecule posts that merely mention docking/MD.
PROTEIN_LIGAND_ANCHORS = [
    "benchmark",
    "method",
    "model",
    "deep learning",
    "machine learning",
    "pose prediction",
    "virtual screening",
    "binding free energy",
    "free energy perturbation",
    "generative",
    "diffusion",
    "flow matching",
    "ADMET",
    "permeability",
    "prospective",
]

KEYWORDS = (
    INTERACTION_GROUPS["protein-ligand"]["keywords"]
    + INTERACTION_GROUPS["protein-protein"]["keywords"]
    + INTERACTION_GROUPS["protein-peptide"]["keywords"]
    + METHOD_KEYWORDS["keywords"]
    + IMPORTANT_TARGET_KEYWORDS["keywords"]
)

ARXIV_QUERY = os.getenv("ARXIV_QUERY", " OR ".join(f'all:"{keyword}"' for keyword in KEYWORDS))

JOURNALS = [
    "Nature Biotechnology",
    "Nature Methods",
    "Nature Chemical Biology",
    "Nature Communications",
    "Science Advances",
    "PLOS Computational Biology",
    "Bioinformatics",
    "Journal of Chemical Information and Modeling",
    "Journal of Medicinal Chemistry",
    "ACS Chemical Biology",
    "Journal of Computer-Aided Molecular Design",
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
    matched_keywords: list[str] = field(default_factory=list)
    interaction_type: str = "uncategorized"
    relevance_score: int = 0


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
    SEEN_FILE.write_text(json.dumps(sorted(set(seen)), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def http_json(url: str, *, timeout: int = 30) -> dict:
    headers = {
        "User-Agent": "min0210.github.io paper bot" + (f" (mailto:{CROSSREF_MAILTO})" if CROSSREF_MAILTO else ""),
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_arxiv_id(entry_id: str) -> str:
    return entry_id.rstrip("/").split("/")[-1]


def contains_keyword(haystack: str, keyword: str) -> bool:
    return keyword.lower() in haystack


def has_anchor(haystack: str, anchors: Iterable[str]) -> bool:
    return any(anchor.lower() in haystack for anchor in anchors)


def analyze_relevance(title: str, abstract: str, category: str = "") -> tuple[str, int, list[str]]:
    haystack = clean_text(f"{title} {abstract} {category}").lower()
    matched: list[str] = []
    scores: dict[str, int] = {name: 0 for name in INTERACTION_GROUPS}

    for group_name, group in INTERACTION_GROUPS.items():
        for keyword in group["keywords"]:
            if contains_keyword(haystack, keyword):
                matched.append(keyword)
                scores[group_name] += int(group["weight"])

    for keyword in METHOD_KEYWORDS["keywords"]:
        if contains_keyword(haystack, keyword):
            matched.append(keyword)
            for group_name in scores:
                if scores[group_name] > 0:
                    scores[group_name] += int(METHOD_KEYWORDS["weight"])

    for keyword in IMPORTANT_TARGET_KEYWORDS["keywords"]:
        if contains_keyword(haystack, keyword):
            matched.append(keyword)
            scores["protein-peptide"] += int(IMPORTANT_TARGET_KEYWORDS["weight"])
            scores["protein-protein"] += 2

    best_group = max(scores, key=scores.get)
    best_score = scores[best_group]
    if best_score == 0:
        return "uncategorized", 0, []

    if best_group == "protein-ligand" and not has_anchor(haystack, PROTEIN_LIGAND_ANCHORS):
        return "uncategorized", 0, []

    return best_group, best_score, list(dict.fromkeys(matched))


def accepted_paper(title: str, abstract: str, category: str = "") -> tuple[bool, str, int, list[str]]:
    interaction_type, score, matches = analyze_relevance(title, abstract, category)
    return score >= MIN_RELEVANCE_SCORE, interaction_type, score, matches


def topic_tags(interaction_type: str, matches: Iterable[str]) -> list[str]:
    tags = [interaction_type]
    for keyword in matches:
        tag = slugify(keyword)
        if tag:
            tags.append(tag)
    if interaction_type == "protein-ligand":
        tags.append("cadd")
    if interaction_type in {"protein-protein", "protein-peptide"}:
        tags.append("core-research")
    return list(dict.fromkeys(tags))


def infer_problem_statement(paper: Paper) -> str:
    if paper.interaction_type == "protein-ligand":
        return "This paper is relevant to protein-ligand CADD because it appears to address ligand docking, pose prediction, screening, binding free energy, ADMET, or lead optimization with a method-level contribution."
    if paper.interaction_type == "protein-protein":
        return "This paper is relevant to protein-protein interaction modeling or modulation, especially interface representation, binder design, complex modeling, or ranking."
    if paper.interaction_type == "protein-peptide":
        return "This paper is relevant to protein-peptide or peptide-based modulation, including peptide conformation, motif recognition, cyclic peptide design, permeability, LC3/LIR-like targeting, or tetherin-related interfaces."
    return "This paper was collected because its metadata matched the configured relevance filters."


def infer_relevance_note(paper: Paper) -> str:
    return {
        "protein-ligand": "Useful mainly for CADD components such as docking, virtual screening, binding free energy, ADMET, or lead optimization.",
        "protein-protein": "Potentially useful for protein binder design, PPI modulation, interface scoring, and complex-level ranking.",
        "protein-peptide": "Potentially useful for peptide binder design, LC3/LIR-like motif targeting, tetherin-interface reasoning, cyclic peptides, and permeability-aware peptide optimization.",
    }.get(paper.interaction_type, "Useful only if the full paper shows a concrete connection to your design workflow.")


def short_abstract_summary(abstract: str, max_sentences: int = 3) -> str:
    abstract = clean_text(abstract)
    if not abstract or abstract == "Abstract not available from Crossref metadata.":
        return "No reliable abstract was available from metadata, so the full paper should be checked before keeping this post."
    sentences = re.split(r"(?<=[.!?])\s+", abstract)
    selected = [sentence for sentence in sentences if sentence][:max_sentences]
    return " ".join(selected)


def fetch_arxiv_papers() -> list[Paper]:
    client = arxiv.Client(page_size=MAX_RESULTS, delay_seconds=3, num_retries=3)
    search = arxiv.Search(query=ARXIV_QUERY, max_results=MAX_RESULTS, sort_by=arxiv.SortCriterion.SubmittedDate, sort_order=arxiv.SortOrder.Descending)
    papers: list[Paper] = []
    for result in client.results(search):
        title = clean_text(result.title)
        abstract = clean_text(result.summary)
        categories = result.categories or []
        accepted, interaction_type, score, matches = accepted_paper(title, abstract, " ".join(categories))
        if not accepted:
            continue
        arxiv_id = parse_arxiv_id(result.entry_id)
        tags = ["papers", "arxiv"] + [cat.replace(".", "-") for cat in categories[:4]] + topic_tags(interaction_type, matches)
        papers.append(
            Paper(
                source="arXiv",
                uid=f"arxiv:{arxiv_id}",
                title=title,
                authors=[author.name for author in result.authors],
                published=result.published.astimezone(timezone.utc).date(),
                abstract=abstract,
                paper_url=result.entry_id,
                pdf_url=result.pdf_url or "",
                primary_category=result.primary_category or (categories[0] if categories else "arxiv"),
                tags=list(dict.fromkeys(tags)),
                extra_links={"alphaXiv": f"https://www.alphaxiv.org/abs/{arxiv_id}"},
                matched_keywords=matches,
                interaction_type=interaction_type,
                relevance_score=score,
            )
        )
    return papers


def fetch_biorxiv_papers() -> list[Paper]:
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
        category = clean_text(item.get("category", ""))
        accepted, interaction_type, score, matches = accepted_paper(title, abstract, category)
        if not accepted:
            continue
        doi = clean_text(item.get("doi", ""))
        paper_url = f"https://doi.org/{doi}" if doi else ""
        pdf_url = f"https://www.biorxiv.org/content/{doi}v{item.get('version', '1')}.full.pdf" if doi else ""
        try:
            published = datetime.strptime(item.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            published = datetime.now(timezone.utc).date()
        authors = [clean_text(author) for author in re.split(r";|,", item.get("authors", "")) if clean_text(author)]
        tags = ["papers", "biorxiv", slugify(category or "preprint")] + topic_tags(interaction_type, matches)
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
                primary_category=category or "bioRxiv",
                tags=list(dict.fromkeys(tags)),
                matched_keywords=matches,
                interaction_type=interaction_type,
                relevance_score=score,
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
    if not ENABLE_CROSSREF:
        return []
    until = datetime.now(timezone.utc).date()
    since = until - timedelta(days=LOOKBACK_DAYS)
    rows_per_journal = max(1, min(3, MAX_RESULTS // 8))
    papers: list[Paper] = []
    crossref_query = " ".join(KEYWORDS)
    for journal in JOURNALS:
        params = {
            "query.container-title": journal,
            "query.bibliographic": crossref_query,
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
            accepted, interaction_type, score, matches = accepted_paper(title, abstract, journal)
            if not title or not accepted:
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
                name = clean_text(f"{clean_text(author.get('given', ''))} {clean_text(author.get('family', ''))}")
                if name:
                    authors.append(name)
            tags = ["papers", "journal", slugify(journal_name)] + topic_tags(interaction_type, matches)
            papers.append(
                Paper(
                    source="Journal",
                    uid=f"doi:{doi or slugify(journal_name + '-' + title)}",
                    title=title,
                    authors=authors,
                    published=published,
                    abstract=abstract or "Abstract not available from Crossref metadata.",
                    paper_url=item.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
                    journal=journal_name,
                    primary_category="journal-article",
                    tags=list(dict.fromkeys(tags)),
                    matched_keywords=matches,
                    interaction_type=interaction_type,
                    relevance_score=score,
                )
            )
        time.sleep(1)
    return papers


def build_post(paper: Paper) -> tuple[str, str]:
    title = clean_text(paper.title)
    slug = slugify(title)[:90] or "paper"
    filename = f"{paper.published.isoformat()}-{slug}.md"
    tags = list(dict.fromkeys([tag for tag in paper.tags if tag]))
    categories = {
        "protein-ligand": "[Protein-Ligand, Paper Review]",
        "protein-protein": "[Protein-Protein, Paper Review]",
        "protein-peptide": "[Protein-Peptide, Paper Review]",
    }.get(paper.interaction_type, "[CADD, Paper Review]")
    description = f"{paper.interaction_type} paper from {paper.source}; matched {', '.join(paper.matched_keywords[:3]) if paper.matched_keywords else 'configured filters'}."
    front_matter = "\n".join(
        [
            "---",
            "layout: post",
            f"title: {yaml_string(title)}",
            f"date: {paper.published.isoformat()} 09:00:00 +0900",
            f"description: {yaml_string(description)}",
            f"categories: {categories}",
            f"tags: {yaml_array(tags)}",
            "math: true",
            "mermaid: true",
            f"source: {yaml_string(paper.source)}",
            f"journal: {yaml_string(paper.journal)}",
            f"interaction_type: {yaml_string(paper.interaction_type)}",
            f"relevance_score: {paper.relevance_score}",
            f"matched_keywords: {yaml_array(paper.matched_keywords)}",
            f"paper_url: {yaml_string(paper.paper_url)}",
            f"pdf_url: {yaml_string(paper.pdf_url)}",
            f"primary_category: {yaml_string(paper.primary_category)}",
            "---",
        ]
    )
    extra_link_lines = "\n".join(f"- **{name}:** [{url}]({url})" for name, url in paper.extra_links.items() if url)
    body = f"""{front_matter}

## Why this paper was selected

- **Interaction class:** `{paper.interaction_type}`
- **Relevance score:** `{paper.relevance_score}` / threshold `{MIN_RELEVANCE_SCORE}`
- **Matched keywords:** {', '.join(paper.matched_keywords) if paper.matched_keywords else 'N/A'}

{infer_problem_statement(paper)}

## Paper summary from metadata

{short_abstract_summary(paper.abstract)}

## Practical relevance

{infer_relevance_note(paper)}

## My research / CADD relevance

| Question | Initial note |
|---|---|
| Protein-ligand relevance | {'High' if paper.interaction_type == 'protein-ligand' else 'Check only if ligand scoring, docking, free energy, or ADMET is involved.'} |
| Protein-protein relevance | {'High' if paper.interaction_type == 'protein-protein' else 'Check only if interface modeling or binder ranking is involved.'} |
| Protein-peptide relevance | {'High' if paper.interaction_type == 'protein-peptide' else 'Check only if peptide-like binding, motifs, macrocycles, or permeability appear.'} |
| Experimental follow-up | Check whether the paper changes how candidates should be prioritized for synthesis or assay. |

## Paper Info

| 항목 | 내용 |
|---|---|
| Title | {title} |
| Authors | {', '.join(paper.authors) if paper.authors else 'Unknown'} |
| Venue / Source | {paper.journal or paper.source} |
| Published | {paper.published.isoformat()} |
| Interaction type | {paper.interaction_type} |
| Relevance score | {paper.relevance_score} |
| Category | {paper.primary_category or 'N/A'} |
| Link | [{paper.paper_url}]({paper.paper_url}) |
| PDF | {f'[{paper.pdf_url}]({paper.pdf_url})' if paper.pdf_url else 'N/A'} |
"""
    if extra_link_lines:
        body += f"\n## Extra Links\n\n{extra_link_lines}\n"
    body += f"""
## Abstract

{paper.abstract or 'Abstract not available from metadata.'}

---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 metadata와 abstract를 기반으로 자동 생성되었으므로, full paper 확인 후 수정이 필요할 수 있습니다.
> 오류 지적이나 피드백은 언제든 환영합니다.
{{: .prompt-info }}
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
    return sorted(unique, key=lambda paper: (paper.relevance_score, paper.published), reverse=True)


def main() -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    seen = load_seen()
    all_papers = deduplicate_papers(fetch_arxiv_papers() + fetch_biorxiv_papers() + fetch_crossref_journal_papers())
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
