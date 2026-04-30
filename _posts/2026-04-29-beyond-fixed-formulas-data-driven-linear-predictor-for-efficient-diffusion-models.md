---
layout: post
title: "Beyond Fixed Formulas: Data-Driven Linear Predictor for Efficient Diffusion Models"
date: 2026-04-29 09:00:00 +0900
description: "protein-protein paper from arXiv; matched PPI, diffusion model."
categories: [Protein-Protein, Paper Review]
tags: ["papers", "arxiv", "cs-CV", "cs-LG", "protein-protein", "ppi", "diffusion-model", "core-research"]
math: true
mermaid: true
source: "arXiv"
journal: ""
interaction_type: "protein-protein"
relevance_score: 5
matched_keywords: ["PPI", "diffusion model"]
paper_url: "http://arxiv.org/abs/2604.26365v1"
pdf_url: "https://arxiv.org/pdf/2604.26365v1"
primary_category: "cs.CV"
---

## Why this paper was selected

- **Interaction class:** `protein-protein`
- **Relevance score:** `5` / threshold `4`
- **Matched keywords:** PPI, diffusion model

This paper is relevant to protein-protein interaction modeling or modulation. For binder design, the important question is how the method represents interfaces, handles conformational flexibility, and ranks complexes or designed binders in a way that could transfer to real experimental selection.

## Paper summary from metadata

To address the high sampling cost of Diffusion Transformers (DiTs), feature caching offers a training-free acceleration method. However, existing methods rely on hand-crafted forecasting formulas that fail under aggressive skipping. We propose L2P (Learnable Linear Predictor), a simple data-driven caching framework that replaces fixed coefficients with learnable per-timestep weights.

## What to look for in the full paper

### Method

Check how the authors define the molecular or structural representation, what model or scoring function is used, and whether the method operates on sequence, structure, complex geometry, MD trajectories, or assay data.

### Validation

Check whether the paper reports only computational benchmarks or also includes wet-lab validation, prospective screening, docking pose validation, binding affinity assays, MD stability, or ADMET/permeability measurements.

### Practical relevance

Potentially useful for protein binder design, PPI modulation, interface scoring, and complex-level ranking.

## My research / CADD relevance

| Question | Initial note |
|---|---|
| Protein-ligand relevance | Check only if the method transfers to ligand scoring, docking, or ADMET. |
| Protein-protein relevance | High |
| Protein-peptide relevance | Check only if peptide-like binding, motifs, macrocycles, or permeability appear. |
| Docking / MD relevance | Not obvious from metadata. |
| Experimental follow-up | Check whether the paper changes how candidates should be prioritized for synthesis or assay. |

## Paper Info

| 항목 | 내용 |
|---|---|
| Title | Beyond Fixed Formulas: Data-Driven Linear Predictor for Efficient Diffusion Models |
| Authors | Zhirong Shen, Rui Huang, Jiacheng Liu, Chang Zou, Peiliang Cai, Shikang Zheng, Zhengyi Shi, Liang Feng, Linfeng Zhang |
| Venue / Source | arXiv |
| Published | 2026-04-29 |
| Interaction type | protein-protein |
| Relevance score | 5 |
| Category | cs.CV |
| Link | [http://arxiv.org/abs/2604.26365v1](http://arxiv.org/abs/2604.26365v1) |
| PDF | [https://arxiv.org/pdf/2604.26365v1](https://arxiv.org/pdf/2604.26365v1) |

## Extra Links

- **alphaXiv:** [https://www.alphaxiv.org/abs/2604.26365v1](https://www.alphaxiv.org/abs/2604.26365v1)

## Abstract

To address the high sampling cost of Diffusion Transformers (DiTs), feature caching offers a training-free acceleration method. However, existing methods rely on hand-crafted forecasting formulas that fail under aggressive skipping. We propose L2P (Learnable Linear Predictor), a simple data-driven caching framework that replaces fixed coefficients with learnable per-timestep weights. Rapidly trained in ~20 seconds on a single GPU, L2P accurately reconstructs current features from past trajectories. L2P significantly outperforms existing baselines: it achieves a 4.55x FLOPs reduction and 4.15x latency speedup on FLUX.1-dev, and maintains high visual fidelity under up to 7.18x acceleration on Qwen-Image models, where prior methods show noticeable quality degradation. Our results show learning linear predictors is highly effective for efficient DiT inference. Code is available at https://github.com/Aredstone/L2P-Cache.

---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 metadata와 abstract를 기반으로 자동 생성되었으므로, full paper 확인 후 수정이 필요할 수 있습니다.
> 오류 지적이나 피드백은 언제든 환영합니다.
{: .prompt-info }
