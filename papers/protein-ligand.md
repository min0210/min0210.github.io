---
layout: page
title: Protein-ligand Papers
permalink: /papers/protein-ligand/
---

# Protein-ligand Papers

Small-molecule docking, protein-ligand pose prediction, virtual screening, binding free energy, ADMET, and lead optimization.

{% assign posts = site.posts | where: "interaction_type", "protein-ligand" %}
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
No protein-ligand papers yet.
{% endif %}

[Back to all papers]({{ '/papers/' | relative_url }})
