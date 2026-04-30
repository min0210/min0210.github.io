---
layout: page
title: Protein-protein Papers
permalink: /papers/protein-protein/
---

# Protein-protein Papers

Protein-protein interaction modulation, protein binders, interface modeling, complex prediction, and binder prioritization.

{% assign posts = site.posts | where: "interaction_type", "protein-protein" %}
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
No protein-protein papers yet.
{% endif %}

[Back to all papers]({{ '/papers/' | relative_url }})
