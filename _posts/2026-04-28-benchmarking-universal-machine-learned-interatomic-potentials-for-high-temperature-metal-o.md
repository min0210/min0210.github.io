---
layout: post
title: "Benchmarking Universal Machine-Learned Interatomic Potentials for High-Temperature Metal-Organic Framework Chemistry"
date: 2026-04-28 09:00:00 +0900
description: "Review candidate covering molecular dynamics; expand using protocol.md."
categories: [Bio, Paper Review]
tags: ["papers", "arxiv", "cond-mat-mtrl-sci", "physics-chem-ph", "molecular-dynamics", "core-research"]
math: true
mermaid: true
source: "arXiv"
journal: ""
paper_url: "http://arxiv.org/abs/2604.25262v1"
pdf_url: "https://arxiv.org/pdf/2604.25262v1"
primary_category: "cond-mat.mtrl-sci"
---

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

- Source: arXiv
- Matched keywords: molecular dynamics
- Main reason to review:
- Main caveat to check:

## Paper Info

| 항목 | 내용 |
|---|---|
| Title | Benchmarking Universal Machine-Learned Interatomic Potentials for High-Temperature Metal-Organic Framework Chemistry |
| Authors | Connor W. Edwards, Jack D. Evans |
| Venue / Source | arXiv |
| Published | 2026-04-28 |
| Category | cond-mat.mtrl-sci |
| Link | [http://arxiv.org/abs/2604.25262v1](http://arxiv.org/abs/2604.25262v1) |
| PDF | [https://arxiv.org/pdf/2604.25262v1](https://arxiv.org/pdf/2604.25262v1) |
| Code | To check |
| Data | To check |

## Extra Links

- **alphaXiv:** [https://www.alphaxiv.org/abs/2604.25262v1](https://www.alphaxiv.org/abs/2604.25262v1)

## Abstract

Universal machine-learned interatomic potentials (uMLIPs) offer a promising approach to performing atomistic simulations at near-DFT accuracy with greatly reduced computational cost. Here, we present a new high-temperature benchmarking dataset of 40~ps ab~initio molecular dynamics (AIMD) trajectories simulated at 300, 1000, and 2000 K for nine zinc- and zirconium-based metal-organic frameworks (MOFs): ZIF-8, CALF-20, MOF-10, MOF-5, MIP-206, UiO-66, UiO-67, UiO-66-NH2, and NU-1000. These trajectories capture equilibrium dynamics, thermally induced distortions, and early-stage decomposition events, including linker degradation and metal node aggregation. Subsequently, we use this dataset to benchmark five leading uMLIPs: ORB-v3, MACE-MP-0a, MACE-MPA-0, fairchem ODAC23, and fairchem OMAT. Our results reveal that ORB-v3 and fairchem OMAT achieve the lowest energy, force, and stress errors across all temperatures. However, all models exhibit significant error under high-temperature conditions. Long-timescale molecular dynamics simulations produced with ORB-v3 demonstrate that the generative error of uMLIPs far exceeds model losses captured during static validation, highlighting the limitations of current universal models for simulating high-temperature MOF dynamics. This work provides a benchmark for assessing the robustness of uMLIPs in extreme regimes and guides future development of potentials capable of accurately modeling the chemistry of high-temperature MOF dynamics.

---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 내용을 기반으로 작성되었으나, 부정확한 내용이 있을 수 있습니다.
> 오류 지적이나 피드백은 언제든 환영합니다.
{: .prompt-info }
