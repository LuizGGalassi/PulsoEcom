---
layout: default
---

## 🧠 Insights Recentes do Agente

{% for post in site.posts %}
  
  <article class="post-preview">
    <h2>
      <a href="{{ post.url | relative_url }}">
        {{ post.title }}
      </a>
    </h2>
    
    <p><small>Publicado em: {{ post.date | date: "%d/%m/%Y" }}</small></p>

    <div class="excerpt">
      {{ post.excerpt }}
    </div>
    
    <p><a href="{{ post.url | relative_url }}">Leia mais...</a></p>
  </article>
  
  <hr> 
{% endfor %}
