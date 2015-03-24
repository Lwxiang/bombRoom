# bombRoom
A simple web game.

前端注意：
----------------------------
1) 在``index.html``的各类静态资源引用前加上``{% load staticfiles %}``

2) 用``{% static 'js/jquery.min.js' %}``和``{% static 'css/index.css' %}``替换原来的url

如
```
{% load staticfiles %}
<script src="{% static 'js/jquery.min.js' %}"></script>
<link href="{% static 'css/index.css' %}" rel="stylesheet" type="text/css">
```
