from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy

from zanhu.news.models import News
from zanhu.helpers import ajax_required, AuthorRequireView


class NewsListView(LoginRequiredMixin, ListView):
    model = News
    # queryset = News.objects.all()
    paginate_by = 20
    # page_kwarg = 'p'
    # context_object_name = 'news_list'
    # ordering = 'created_at'
    template_name = "news/news_list.html"
    # def get_ordering(self):
    #     pass
    #
    # def get_paginate_by(self, queryset):
    #     pass

    def get_queryset(self):
        return News.objects.filter(reply=False)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     """
    #     添加额外的，自定义的上下文
    #     :param object_list:
    #     :param kwargs:
    #     :return:
    #     """
    #     context = super().get_context_data()
    #     context['view'] = 100
    #     return context


class NewsDeleteView(LoginRequiredMixin, AuthorRequireView, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    slug_url_kwarg = 'slug'   # 通过url传入要删除的对象主键ID，默认值是slug
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('news:list')  # reverse_lazy可以在项目URLConf未加载前使用


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    # 用户在首页发送动态
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest('内容不能为空')


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """
    点赞，AJAX POST请求
    :param request:
    :return:
    """
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({'likes': news.count_likers()})


@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    """
    返回动态的评论， AJAX GET请求
    :param request:
    :return:
    """
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    news_html = render_to_string('news/news_single.html', {'news': news})  # 没有评论的时候
    thread_html = render_to_string('news/news_thread.html', {'thread': news.get_thread()})  # 有评论的时候
    return JsonResponse({
        'uuid': news_id,
        'news': news_html,
        'thread': thread_html,
    })


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    """
    评论， AJAX POST请求
    :param request:
    :return:
    """
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:
        return HttpResponseBadRequest('内容不能为空')

