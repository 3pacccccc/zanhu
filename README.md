一个问答网站
=====
环境：
-----
centos7+django2.17+python3.6

涉及技术：
-----

前端：jQuery, AJAX, JS
后端：Django， cookiecutter, celery, django-test-plus, django-all-auth, django-taggit, slugify

具体操作：
-----
使用cookiecutter创建一个django项目。
集成了django-all-auth作为登录系统，使用GitHub作为第三方登录。
使用django-test-plus编写测试用例
使用slugify为文章生成生成url别名(使用文章的标题)。
使用django-taggit生成文章的标签
使用django-markdownx实现发送文章的时候在线预览效果
使用django-contrib-comments实现文章的评论功能
