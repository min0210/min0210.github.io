#!/usr/bin/env python3
"""Fetch recent papers from multiple public sources and create Jekyll posts.

Sources:
- arXiv metadata via the arxiv Python package
- bioRxiv metadata via the public bioRxiv API
- journal article metadata via the Crossref REST API
- alphaXiv links are added for arXiv papers as an additional discussion layer

The script uses metadata and abstracts only. It does not download or summarize PDFs.
Generated posts are review candidates that follow protocol.md.
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

# Directly aligned with the user's main research direction.
CORE_KEYWORDS = [
    "peptide design",
    "cyclic peptide",
    "macrocyclic peptide",
    "protein binder design",
    "protein-protein interaction",
    "protein protein interaction",
    "binding affinity prediction",
    "molecular docking",
    "molecular dynamics",
    "LC3",
    "LIR motif",
    "tetherin",
    "BST-2",
    "cell permeability peptide",
    "N-methylation",
    "non-canonical amino acid",
    "peptide permeability",
]

# Broader CADD scouting terms. These allow important or novel CADD papers
# even when they are not directly peptide/LC3/tetherin papers.
CADD_KEYWORDS = [
    "computer-aided drug design",
    "CADD",
    "structure-based drug design",
    "ligand-based drug design",
    "de novo drug design",
    "generative molecular design",
    "molecular generation",
    "diffusion model drug discovery",
    "flow matching molecule",
    "molecular representation learning",
    "protein-ligand binding",
    "binding pose prediction",
    "docking score",
    "virtual screening",
    "hit discovery",
    "lead optimization",
    "free energy perturbation",
    "alchemical free energy",
    "binding free energy",
    "MM-PBSA",
    "MM-GBSA",
    "enhanced sampling",
    "molecular dynamics acceleration",
    "ADMET",
    "permeability prediction",
    "toxicity prediction",
    "covalent inhibitor",
    "fragment-based drug discovery",
    "retrosynthesis",
    "synthesis-aware design",
    "active learning drug discovery",
    "AI drug discovery",
    "chemical language model",
]

KEYWORDS = CORE_KEYWORDS + CADD_KEYWORDS

ARXIV_QUERY = os.getenv(
    "ARXIV_QUERY",
    " OR ".join(f'all:"{keyword}"' for keyword in KEYWORDS),
)

# Journals that often publish computational biology, chemical biology,
# medicinal chemistry, biophysics, protein science, and CADD papers.
JOURNALS = [
    "Nature Biotechnology",
    "Nature Methods",
    "Nature Chemical Biology",
    "Nature Communications",
    "Communications Biology",
    "Science Advances",
    "Cell Systems",
    "PLOS Computational Biology",
    "Bioinformatics",
    "Briefings in Bioinformatics",
    "Nucleic Acids Research",
    "Structure",
    "Journal of Molecular Biology",
    "Protein Science",
    "Biophysical Journal",
    "Journal of Chemical Information and Modeling",
    "Journal of Medicinal Chemistry",
    "ACS Central Science",
    "ACS Chemical Biology",
    "ACS Medicinal Chemistry Letters",
    "Chemical Science",
    "Digital Discovery",
    "Drug Discovery Today",
    "Expert Opinion on Drug Discovery",
    "Molecular Informatics",
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


def matched_keywords(*texts: str) -> list[str]:
    haystack = " ".join(clean_text(text).lower() for text in texts)
    matches = []
    for keyword in KEYWORDS:
        if keyword.lower() in haystack:
            matches.append(keyword)
    return matches


def keyword_match(*texts: str) -> bool:
    return bool(matched_keywords(*texts))


def topic_tags(matches: Iterable[str]) -> list[str]:
    tags = []
    for keyword in matches:
        tag = slugify(keyword)
        if tag:
            tags.append(tag)
    if any(keyword in CORE_KEYWORDS for keyword in matches):
        tags.append("core-research")
    if any(keyword in CADD_KEYWORDS for keyword in matches):
        tags.append("cadd")
    return list(dict.fromkeys(tags))


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
        matches = matched_keywords(result.title, result.summary, " ".join(categories))
        tags = ["papers", "arxiv"] + [cat.replace(".", "-") for cat in categories[:4]] + topic_tags(matches)
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
                tags=list(dict.fromkeys(tags)),
                extra_links={"alphaXiv": f"https://www.alphaxiv.org/abs/{arxiv_id}"},
                matched_keywords=matches,
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
        category = clean_text(item.get("category", ""))
        matches = matched_keywords(title, abstract, category)
        if not matches:
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

        tags = ["papers", "biorxiv", slugify(category or "preprint")] + topic_tags(matches)
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

    # Crossref's query field is broad. We keep the query broad and then apply
    # local keyword filtering to reduce irrelevant journal hits.
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
            matches = matched_keywords(title, abstract, journal)
            if not title or not matches:
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

            tags = ["papers", "journal", slugify(journal_name)] + topic_tags(matches)
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
                    tags=list(dict.fromkeys(tags)),
                    matched_keywords=matches,
                )
            )

        time.sleep(1)

    return papers


def build_post(paper: Paper) -> tuple[str, str]:
    title = clean_text(paper.title)
    slug = slugify(title)[:90] or "paper"
    filename = f"{paper.published.isoformat()}-{slug}.md"

    tags = list(dict.fromkeys([tag for tag in paper.tags if tag]))
    categories = "[Bio, Paper Review]" if any(tag in tags for tag in ["core-research", "biorxiv"]) else "[AI, Drug Discovery]"
    description = (
        "Review candidate covering "
        + (", ".join(paper.matched_keywords[:4]) if paper.matched_keywords else paper.source)
        + "; expand using protocol.md."
    )

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

## Hook

이 포스트는 자동 수집된 리뷰 후보입니다. `protocol.md` 기준에 맞춰 논문 PDF, supplement, code, benchmark를 확인한 뒤 long-form technical review로 확장하세요.

이 논문이 중요한지 판단할 때는 두 가지 관점으로 봅니다.

1. 내 core research, 즉 peptide/protein binder, LC3/LIR, tetherin, docking, MD, permeability workflow에 직접 도움이 되는가?
2. 직접적인 주제가 아니더라도 CADD 관점에서 방법론적으로 새롭거나 실제 drug discovery workflow를 바꿀 가능성이 있는가?

## Problem

작성할 때 확인할 병목:

- 이 논문은 어떤 biological, chemical, or computational bottleneck을 다루는가?
- docking score, binding affinity, MD sampling, permeability, ADMET, synthesis feasibility 중 무엇과 연결되는가?
- 기존 방법은 어디에서 실패하거나 비효율적인가?

## Key Idea

- 핵심 아이디어 1:
- 핵심 아이디어 2:
- 핵심 아이디어 3:
- baseline 대비 가장 큰 차이:

## How It Works

### Overview

전체 pipeline을 입력 → representation → model/scoring/simulation → output 순서로 정리합니다.

### Representation / Problem Formulation

분자, 단백질, peptide, complex, conformer, trajectory, assay data가 어떻게 표현되는지 정리합니다.

### Core Mathematical or Structural Setup

핵심 수식, energy, score, probability, loss, docking objective, free-energy estimator, sampling rule을 정리합니다.

### Architecture / Pipeline

모듈별 역할을 설명합니다.

```python
# Pseudocode placeholder
inputs = load_molecular_or_structural_inputs()
representations = encode(inputs)
scores_or_samples = model_or_protocol(representations)
ranked_candidates = rank(scores_or_samples)
```

### Training, Scoring, or Simulation Objective

모델의 loss, docking score, free energy objective, MD protocol, or selection criterion을 정리합니다.

### Inference / Docking / MD / Ranking

실제 후보를 어떻게 생성하고 ranking하는지 설명합니다.

### Why This Might Work

이 접근이 왜 기존 방법보다 나을 수 있는지 inductive bias, physics, data, representation 관점에서 설명합니다.

## Results

확인할 것:

- main benchmark와 metric
- ablation
- generalization / OOD
- docking success rate or enrichment factor
- binding affinity correlation or free energy error
- MD stability, RMSD, contact persistence
- ADMET or permeability metric
- wet-lab validation 여부

## Discussion

논문 claim과 내 해석을 구분해서 적습니다.

- 실제 CADD workflow에서 어느 단계에 들어갈 수 있는가?
- peptide/protein binder design에 직접 연결되는가?
- 직접 연결되지 않는다면 왜 그래도 중요한가?

## Limitations

- benchmark가 제한적인가?
- wet-lab validation이 있는가?
- induced fit, membrane, glycan, solvent exposure, cofactor를 고려했는가?
- docking/MD/free energy 조건이 충분한가?
- synthesis feasibility 또는 medicinal chemistry constraints를 고려했는가?
- code/data 공개 여부는 어떤가?

## Relevance to My Research / CADD

### Direct relevance

- peptide design:
- protein binder design:
- LC3/LIR:
- BST-2/tetherin:
- docking / MD:
- permeability / N-methylation / NCAA:

### Broader CADD relevance

- virtual screening:
- hit discovery / hit expansion:
- lead optimization:
- ADMET:
- free energy / MD:
- synthesis-aware design:

## Conclusion

이 논문에서 가져갈 점을 한 문단으로 정리합니다.

## TL;DR

- Source: {paper.source}
- Matched keywords: {', '.join(paper.matched_keywords) if paper.matched_keywords else 'N/A'}
- Main reason to review:
- Main caveat to check:

## Paper Info

| 항목 | 내용 |
|---|---|
| Title | {title} |
| Authors | {', '.join(paper.authors) if paper.authors else 'Unknown'} |
| Venue / Source | {paper.journal or paper.source} |
| Published | {paper.published.isoformat()} |
| Category | {paper.primary_category or 'N/A'} |
| Link | [{paper.paper_url}]({paper.paper_url}) |
| PDF | {f'[{paper.pdf_url}]({paper.pdf_url})' if paper.pdf_url else 'N/A'} |
| Code | To check |
| Data | To check |
"""

    if extra_link_lines:
        body += f"\n## Extra Links\n\n{extra_link_lines}\n"

    body += f"""
## Abstract

{paper.abstract or 'Abstract not available from metadata.'}

---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 내용을 기반으로 작성되었으나, 부정확한 내용이 있을 수 있습니다.
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
