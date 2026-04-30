---
layout: post
title: "Thermal conductivity of aligned polymers with kinks"
date: 2026-04-27 09:00:00 +0900
description: "Review candidate covering molecular dynamics; expand using protocol.md."
categories: [Bio, Paper Review]
tags: ["papers", "arxiv", "physics-chem-ph", "cond-mat-dis-nn", "molecular-dynamics", "core-research"]
math: true
mermaid: true
source: "arXiv"
journal: ""
paper_url: "http://arxiv.org/abs/2604.25037v1"
pdf_url: "https://arxiv.org/pdf/2604.25037v1"
primary_category: "physics.chem-ph"
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
| Title | Thermal conductivity of aligned polymers with kinks |
| Authors | Igor V. Parshin, Igor V. Rubtsov, Alexander L. Burin |
| Venue / Source | arXiv |
| Published | 2026-04-27 |
| Category | physics.chem-ph |
| Link | [http://arxiv.org/abs/2604.25037v1](http://arxiv.org/abs/2604.25037v1) |
| PDF | [https://arxiv.org/pdf/2604.25037v1](https://arxiv.org/pdf/2604.25037v1) |
| Code | To check |
| Data | To check |

## Extra Links

- **alphaXiv:** [https://www.alphaxiv.org/abs/2604.25037v1](https://www.alphaxiv.org/abs/2604.25037v1)

## Abstract

Thermal conductivity of aligned polymer molecules can be exceptionally high along the alignment direction due to energy transport through strong covalent bonds. At the same time, it is highly sensitive to molecular conformation, varying by orders of magnitude as a result of gauche kinks. Here, we theoretically investigate phonon transport in kinked polymers by numerically evaluating thermal conductivity and interpreting the results in terms of phonon scattering from randomly distributed kinks. For strongly aligned polymers with restricted deviations from a linear backbone, we find that heat transport becomes superdiffusive at long lengths, with thermal conductivity scaling as $κ\propto L^{1/3}$. At shorter lengths, thermal conductivity exhibits non-monotonic behavior: it increases at very short scales due to ballistic transport of almost all phonons, then decreases at intermediate lengths due to the Anderson localization of most phonon modes. These results are consistent with experiments and molecular dynamics simulations, and they elucidate the microscopic mechanisms governing heat transport in polymers.

---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 내용을 기반으로 작성되었으나, 부정확한 내용이 있을 수 있습니다.
> 오류 지적이나 피드백은 언제든 환영합니다.
{: .prompt-info }
