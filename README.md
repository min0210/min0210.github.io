# Sangmin Research Notes

A GitHub Pages research paper blog that automatically collects recent papers and turns them into Markdown review candidates.

## What this site does

- Builds a polished Jekyll blog on GitHub Pages.
- Fetches recent papers from arXiv, bioRxiv, and journal metadata through Crossref.
- Adds alphaXiv links for arXiv papers when available.
- Creates one Markdown review-candidate post per new paper.
- Tracks already-seen papers in `data/seen_papers.json`.
- Runs automatically with GitHub Actions every day and on pushes to `main`.
- Uses `protocol.md` as the writing standard for long-form technical reviews.

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

Optional environment variables:

```bash
MAX_RESULTS=25 MAX_NEW_POSTS=8 LOOKBACK_DAYS=14 python scripts/fetch_papers.py
```

## Paper selection scope

The fetcher uses two priority layers.

### Core research priority

- peptide design
- cyclic / macrocyclic peptide
- protein binder design
- protein-protein interaction modulation
- binding affinity prediction
- molecular docking
- molecular dynamics
- LC3 / LIR motif
- BST-2 / tetherin
- peptide permeability
- N-methylation
- non-canonical amino acids

### Broad CADD scouting priority

The blog also collects papers that are important or novel from a broader computer-aided drug design perspective, even if they are not directly about the core targets above.

Examples:

- structure-based drug design
- ligand-based drug design
- generative molecular design
- docking score improvement
- binding pose prediction
- binding free energy prediction
- FEP / alchemical free energy
- enhanced sampling
- ADMET / permeability / toxicity prediction
- virtual screening
- lead optimization
- retrosynthesis and synthesis-aware design
- fragment-based drug discovery
- AI for drug discovery

## Automation

The workflow in `.github/workflows/fetch-papers.yml` runs daily, runs on pushes to `main`, and can also be started manually from the GitHub Actions tab.

## Review protocol

See `protocol.md` or `/protocol/` on the site. Automatically generated posts are review candidates, not finished reviews. They should be expanded into long-form technical reviews after reading the paper, supplement, figures, and code.
