---
layout: page
title: Papers
permalink: /papers/
---

# Papers

논문 노트는 interaction type 기준으로 분류됩니다. 새 논문은 자동 수집 시 `protein-ligand`, `protein-protein`, `protein-peptide` 중 하나로 태깅됩니다.

<div class="card-grid">
  <a class="card category-card" href="{{ '/papers/protein-ligand/' | relative_url }}">
    <h3>Protein-ligand</h3>
    <p>Docking, pose prediction, virtual screening, binding free energy, ADMET, and lead optimization.</p>
  </a>
  <a class="card category-card" href="{{ '/papers/protein-protein/' | relative_url }}">
    <h3>Protein-protein</h3>
    <p>PPI modulation, protein binders, interface scoring, complex modeling, and protein binder design.</p>
  </a>
  <a class="card category-card" href="{{ '/papers/protein-peptide/' | relative_url }}">
    <h3>Protein-peptide</h3>
    <p>Peptide binders, cyclic peptides, LC3/LIR-like motifs, tetherin, permeability, and macrocycles.</p>
  </a>
</div>

## All paper notes

{% assign paper_posts = site.posts | where_exp: "post", "post.categories contains 'Paper Review'" %}
{% if paper_posts.size > 0 %}
<ul class="paper-index-list">
{% for post in paper_posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span>— {{ post.date | date: "%Y-%m-%d" }}</span>
    {% if post.interaction_type %}<span class="mini-chip">{{ post.interaction_type }}</span>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}
아직 paper note가 없습니다. `data/seen_papers.json`은 초기화했으므로 다음 `Fetch papers` 실행 때 새 기준으로 다시 생성됩니다.
{% endif %}
