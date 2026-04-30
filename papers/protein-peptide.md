---
layout: page
title: Protein-peptide Papers
permalink: /papers/protein-peptide/
---

# Protein-peptide Papers

Peptide binders, cyclic and macrocyclic peptides, LC3/LIR-like motif targeting, tetherin-related interfaces, permeability, NCAA substitution, and N-methylation.

{% assign posts = site.posts | where: "interaction_type", "protein-peptide" %}
{% if posts.size > 0 %}
<ul class="paper-index-list">
{% for post in posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span>— {{ post.date | date: "%Y-%m-%d" }}</span>
    {% if post.relevance_score %}<span class="mini-chip">score {{ post.relevance_score }}</span>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}
No protein-peptide papers yet.
{% endif %}

[Back to all papers]({{ '/papers/' | relative_url }})
