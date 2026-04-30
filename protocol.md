---
layout: page
title: Paper Review Protocol
permalink: /protocol/
---

# min0210.github.io Paper Review Protocol

이 문서는 `min0210.github.io` 블로그의 논문 리뷰 포스트 작성 프로토콜이다.

원본 `BLOG_POST_PROTOCOL.md`의 핵심 원칙인 **깊은 해설형 long-form technical review**를 유지하되, 이 블로그의 연구 방향에 맞게 peptide/protein binder, LC3/LIR, tetherin, MD, docking, 그리고 넓은 의미의 CADD 관점까지 확장한다. 원본 프로토콜은 “단순 요약이 아니라 문제의식, 핵심 수식, 모델링 선택, 구현 감각, 실험 결과, 한계까지 따라올 수 있는 리뷰”를 목표로 한다. 이 방향을 유지하면서 `min0210`의 연구축에 맞게 적용한다.

> 목표: 논문을 안 읽은 사람도 이 글 하나로 문제의식, 핵심 수식, 모델/프로토콜 설계 이유, 실험 결과, 한계, 그리고 내 연구에 어떻게 쓸 수 있는지까지 따라올 수 있는 리뷰.

---

## 0. 블로그의 연구 축

이 블로그는 두 층의 관심사를 가진다.

### A. Core research priority

가장 우선적으로 다루는 주제다.

- peptide design
- cyclic peptide / macrocyclic peptide
- protein binder design
- protein-protein interaction modulation
- binding affinity prediction
- molecular docking
- molecular dynamics simulation
- peptide permeability
- N-methylation
- non-canonical amino acid substitution
- autophagy, LC3, LIR motif
- BST-2 / tetherin
- structure-based peptide and drug design

### B. Broad CADD scouting priority

꼭 위 주제에 직접 걸리지 않더라도, CADD 관점에서 중요하거나 신박하면 다룬다.

- structure-based drug design
- ligand-based drug design
- generative molecular design
- de novo drug design
- diffusion / flow / transformer models for molecules or proteins
- docking score improvement
- protein-ligand binding pose prediction
- binding free energy prediction
- FEP / alchemical free energy / MM-PBSA / MM-GBSA
- molecular dynamics acceleration
- enhanced sampling
- active learning for drug discovery
- ADMET / permeability / toxicity prediction
- retrosynthesis and synthesis-aware design
- covalent inhibitor design
- fragment-based drug discovery
- virtual screening
- molecular representation learning
- AI for structural biology
- wet-lab validated computational design

논문 선택 기준은 단순히 “내 타깃과 직접 관련 있는가?”가 아니다. 다음 중 하나라도 만족하면 리뷰 후보가 될 수 있다.

1. 내 peptide/protein binder workflow에 직접 도움을 준다.
2. docking, MD, binding affinity, permeability, ADMET 중 하나를 개선할 수 있다.
3. CADD 전체 관점에서 방법론적으로 새롭다.
4. 실험 검증이 강해서 computational design의 실제 가능성을 보여준다.
5. 지금은 직접 쓰지 않더라도 앞으로 연구 방향을 바꿀 수 있는 아이디어가 있다.

---

## 1. 기본 원칙

모든 paper review는 다음 6가지를 지향한다.

1. **맥락**: 왜 이 문제가 중요한가.
2. **핵심 주장**: 저자들이 무엇을 새롭게 바꾸었는가.
3. **수학적/구조적 중심**: 어떤 표현, 목적함수, 확률모형, 물리 모델 위에서 문제를 푸는가.
4. **구현 감각**: 실제로 어떤 입력이 어떤 모듈을 지나 어떤 출력이 되는가.
5. **평가와 한계**: 결과가 얼마나 설득력 있고, 어디까지 믿을 수 있는가.
6. **내 연구/CADD와의 연결**: peptide design, docking, MD, LC3/LIR, tetherin, permeability, CADD workflow에 어떤 힌트를 주는가.

금지:

- 초록 번역체
- 홍보문
- 수식만 있고 해설이 없는 글
- “좋다/강하다/흥미롭다”만 반복하는 글
- 내 연구 또는 CADD 관점 연결 없이 논문 내용만 나열하는 글

권장:

- 직관 + 수식 + 구조 + 구현 감각 + 비판 + 연구 적용 가능성이 함께 있는 글

---

## 2. 글의 깊이 기준

기본 목표는 short summary가 아니라 **세미나 노트 수준의 긴 글**이다.

권장 기준:

- `How It Works` 비중: 전체의 40% 이상
- 핵심 수식 또는 구조/알고리즘 설명: 중요 논문이면 3개 이상
- 코드 블록 또는 pseudocode: 1개 이상
- 결과 표 또는 핵심 수치: 1개 이상
- 한계 섹션: 반드시 포함
- 내 연구 또는 CADD 적용 가능성: 반드시 포함

자동 수집 포스트는 메타데이터 기반 초안이므로 처음부터 완성 리뷰일 필요는 없다. 자동 포스트는 “리뷰 후보 카드 + 작성 scaffold”이고, 사람이 읽은 뒤 long-form review로 확장한다.

---

## 3. 수집 소스와 역할

자동 수집은 다음 소스를 사용한다.

- arXiv: AI/ML, computational biology, protein design, docking, CADD 관련 preprint
- bioRxiv: biology, biophysics, chemical biology 관련 preprint
- alphaXiv: arXiv 논문에 대한 discussion layer 링크
- Crossref journal metadata: 관련 저널의 최신 article metadata

저널 검색은 특히 다음 성격의 저널을 우선한다.

- computational biology
- chemical biology
- medicinal chemistry
- biophysics
- structural biology
- protein science
- bioinformatics
- AI for biology
- computer-aided drug design
- molecular simulation

---

## 4. Front Matter 규칙

기본 템플릿:

```yaml
---
layout: post
title: "<PAPER TITLE>"
date: YYYY-MM-DD HH:MM:SS +0900
description: "핵심 기여 + 기술 요소 + 내 연구/CADD와의 연결을 압축한 설명"
categories: [Bio, Paper Review]
tags: [peptide-design, protein-binding, docking, molecular-dynamics, cadd]
math: true
mermaid: true
source: "arXiv | bioRxiv | Journal"
journal: "<journal or preprint server>"
paper_url: "<url>"
pdf_url: "<url>"
primary_category: "<category>"
---
```

카테고리 원칙:

- 계산/AI 중심이면 `[AI, Paper Review]`
- 생물학/구조생물학/펩타이드 중심이면 `[Bio, Paper Review]`
- CADD 방법론 중심이면 `[AI, Drug Discovery]` 또는 `[Bio, Drug Discovery]`
- 도구/블로그 자동화/코드 중심이면 `[Dev, Automation]`

태그 원칙:

- 영어 kebab-case 사용
- 예: `peptide-design`, `cyclic-peptide`, `protein-binder`, `ppi`, `binding-affinity`, `docking`, `molecular-dynamics`, `lc3`, `lir-motif`, `tetherin`, `bst-2`, `permeability`, `n-methylation`, `cadd`, `virtual-screening`, `generative-design`, `admet`, `free-energy`

---

## 5. 기본 문서 구조

```md
## Hook
## Problem
## Key Idea
## How It Works
### Overview
### Representation / Problem Formulation
### Core Mathematical or Structural Setup
### Architecture / Pipeline
### Training, Scoring, or Simulation Objective
### Inference / Docking / MD / Ranking
### Why This Might Work
## Results
## Discussion
## Limitations
## Relevance to My Research / CADD
## Conclusion
## TL;DR
## Paper Info
```

---

## 6. 섹션별 작성 규칙

### Hook

2~4문단 안에 이 논문이 왜 중요한지 납득시킨다.

포함할 것:

- 분야의 현재 병목
- 기존 접근의 한계
- 이 논문이 제안하는 핵심 변화
- 내가 왜 이 논문을 읽는지
- peptide/protein binder에 직접 관련이 없더라도 CADD 관점에서 왜 볼 가치가 있는지

### Problem

문제를 2~4개의 병목으로 나눠 설명한다.

가능한 병목:

- representation 문제
- conformational flexibility
- induced fit
- peptide permeability
- docking score와 실제 binding affinity mismatch
- MD sampling 부족
- free energy 계산 비용
- ADMET 예측 불확실성
- synthesis feasibility 부족
- data leakage 또는 benchmark 편향
- glycan/membrane/solvent exposure 같은 구조적 제약

### Key Idea

핵심 기여를 3~4개의 bullet로 압축한다. 가능하면 baseline 대비 차이를 짧은 표로 정리한다.

### How It Works

가장 중요한 섹션이다. 단순히 모델 이름을 나열하지 말고, 입력에서 출력까지 흐름을 설명한다.

반드시 포함하려고 시도할 것:

- 전체 pipeline
- 입력 representation
- scoring, objective, loss, energy, 또는 sampling rule
- docking / MD / free energy / ADMET / generative design 흐름
- 구조적 제약이 어떻게 반영되는지
- 최소 1개의 pseudocode 또는 코드 블록
- 중요한 수식은 블록 수식으로 쓰고 자연어로 해설

수식 처리 규칙:

1. 먼저 의미를 설명한다.
2. 수식을 별도 블록으로 제시한다.
3. 각 항을 설명한다.
4. 이 수식이 논문에서 왜 중요한지 말한다.

### Results

숫자 나열 금지. 결과는 반드시 해석한다.

체크할 것:

- main benchmark
- ablation
- generalization / OOD
- runtime / compute
- docking success rate
- binding affinity correlation
- enrichment factor / hit rate
- free energy error
- ADMET metric
- wet-lab validation 여부
- MD stability / RMSD / contact persistence
- permeability 또는 cell assay 여부

### Discussion

내 해석이 들어가도 된다. 단, 사실과 의견을 구분한다.

포함 권장:

- 왜 이 접근이 먹혔는가
- 기존 peptide/protein/CADD 방법과 무엇이 다른가
- 실제 실험이나 simulation으로 이어질 수 있는가
- 내 LC3/LIR, tetherin, cyclic peptide, permeability 프로젝트에 줄 수 있는 힌트
- CADD workflow에서 어느 단계에 넣을 수 있는가

### Limitations

한계를 독립 섹션으로 분리한다.

가능하면 아래를 확인한다.

- benchmark가 제한적인가
- wet-lab validation이 있는가
- docking/MD/free energy 조건이 충분한가
- cofactor, glycan, membrane, solvent exposure, induced fit을 고려했는가
- baseline 비교가 공정한가
- 코드와 데이터가 공개되어 재현 가능한가
- medicinal chemistry / synthesis feasibility를 고려했는가

### Relevance to My Research / CADD

이 블로그에서는 이 섹션을 반드시 포함한다.

질문:

- 이 논문이 peptide design workflow에 어떤 개선점을 줄 수 있는가?
- cyclic peptide, N-methylation, NCAA 치환, permeability 개선과 연결되는가?
- docking 후 MD refinement 또는 binding affinity prediction에 쓸 수 있는가?
- LC3/LIR motif 또는 BST-2/tetherin interface 설계에 적용 가능한가?
- CADD 전체 관점에서 어느 단계에 들어가는가?
- virtual screening, hit expansion, lead optimization, ADMET, free energy, synthesis planning 중 어디에 도움이 되는가?
- 실험 후보 선정 기준을 바꿀 수 있는가?

---

## 7. 품질 체크리스트

최소 기준:

- [ ] front matter 완비
- [ ] `How It Works`가 글의 중심
- [ ] 수식 또는 구조 설명 3개 이상
- [ ] 코드 블록 또는 pseudocode 1개 이상
- [ ] 결과 표/수치 포함
- [ ] `Limitations` 존재
- [ ] `Relevance to My Research / CADD` 존재
- [ ] `Paper Info` 존재
- [ ] 마지막 고정 블록 존재

깊은 리뷰 기준:

- [ ] 핵심 theorem/lemma/설계 이유가 설명됨
- [ ] notation과 직관이 연결됨
- [ ] 결과 해석이 비판적임
- [ ] baseline 대비 차이가 명확함
- [ ] 구현 또는 simulation 감각이 생김
- [ ] 실제 peptide design 또는 CADD workflow에 어떤 영향을 줄지 설명됨

---

## 8. 마지막 고정 블록

```md
---

> 이 글은 LLM(Large Language Model)의 도움을 받아 작성되었습니다.
> 논문의 내용을 기반으로 작성되었으나, 부정확한 내용이 있을 수 있습니다.
> 오류 지적이나 피드백은 언제든 환영합니다.
{: .prompt-info }
```

---

## 9. 자동 수집 포스트의 역할

자동 수집 포스트는 완성 리뷰가 아니라 **리뷰 후보 초안**이다.

자동 생성 시 포함할 것:

- 논문 메타데이터
- abstract
- alphaXiv 링크가 있으면 포함
- long-form review scaffold
- 내 연구/CADD와의 연결 질문
- Paper Info table
- 마지막 고정 블록

자동 생성 후 사람이 해야 할 것:

1. 논문 PDF와 supplement를 읽는다.
2. 핵심 figure를 `assets/img/posts/<slug>/`에 저장한다.
3. `How It Works`와 `Results`를 실제 내용으로 채운다.
4. 한계와 내 연구/CADD 적용 가능성을 비판적으로 쓴다.

---

## 10. 최종 요약

`min0210.github.io`의 논문 리뷰는 앞으로 **peptide/protein binder 설계 연구와 넓은 CADD 관점에 실제로 도움이 되는 long-form technical review**를 표준으로 한다. 핵심은 논문을 많이 모으는 것이 아니라, 중요한 논문을 깊게 읽고 내 workflow에 연결하는 것이다.
