# min0210.github.io

A GitHub Pages research paper blog that automatically collects recent papers and turns them into Markdown posts.

## What this site does

- Builds a simple Jekyll blog on GitHub Pages.
- Fetches recent papers from arXiv.
- Creates one Markdown post per new paper.
- Tracks already-seen papers in `data/seen_papers.json`.
- Runs automatically with GitHub Actions every week.

## Local setup

```bash
bundle install
bundle exec jekyll serve
```

Then open `http://localhost:4000`.

## Fetch papers locally

```bash
python -m pip install arxiv python-slugify
python scripts/fetch_papers.py
```

## Topics

The default query focuses on peptide design, protein-protein interactions, binding affinity prediction, docking, molecular dynamics, autophagy, LC3, LIR motif, BST-2/tetherin, and computational drug design.

## Automation

The workflow in `.github/workflows/fetch-papers.yml` runs weekly and can also be started manually from the GitHub Actions tab.
