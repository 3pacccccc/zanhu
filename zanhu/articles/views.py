from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django_comments.signals import comment_was_posted

from notifications.views import notification_handler
from zanhu.articles.models import Article
from .forms import ArticleForm
from zanhu.helpers import AuthorRequireView

class ArticlesListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 10
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()


class DraftListView(ArticlesListView):
    """
    草稿箱文章列表
    """
    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_create.html'
    message = '您的文章已创建成功'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        成功后跳转
        """
        messages.success(self.request, self.message)    # 在下一次请求的时候将message带给用户
        return reverse_lazy('articles:list')   # reverse_lazy可以在项目URLConf未加载前使用

class ArticleEditView(LoginRequiredMixin, AuthorRequireView, UpdateView):
    """
    编辑文章
    """
    model = Article
    message = "您的文章编辑成功"
    form_class = ArticleForm
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        编辑成功后跳转
        :return:
        """
        messages.success(self.request, self.message)
        return reverse_lazy('articles:article', kwargs={"slug": self.get_object().slug})

class ArticleDetailView(LoginRequiredMixin, DetailView):
    """
    文章详情页
    """
    model = Article
    template_name = 'articles/article_detail.html'


def notify_comment(**kwargs):
    """
    文章有评论时通知作者
    :param kwargs:
    :return:
    """
    actor = kwargs['request'].user
    obj = kwargs['comment'].comtent_object

    notification_handler(actor, obj, 'c', obj)

# 观察者模式 = 订阅[列表] + 通知(同步)
comment_was_posted.connect(receiver=notify_comment)
