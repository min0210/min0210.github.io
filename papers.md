---
layout: page
title: Papers
permalink: /papers/
---

# Papers

Automatically collected papers appear here as blog posts.

{% assign paper_posts = site.posts | where_exp: "post", "post.categories contains 'papers'" %}
{% if paper_posts.size > 0 %}
<ul>
{% for post in paper_posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span>— {{ post.date | date: "%Y-%m-%d" }}</span>
  </li>
{% endfor %}
</ul>
{% else %}
No paper posts yet. Run the paper fetch workflow from the GitHub Actions tab.
{% endif %}
