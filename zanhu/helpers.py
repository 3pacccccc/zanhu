from django.core.exceptions import PermissionDenied
from functools import wraps

from django.http import HttpResponseBadRequest
from django.views.generic import View

def ajax_required(f):
    # 验证函数是否为AJAX请求

    @wraps(f)
    # 使用wraps装饰器不会改变函数F的名字以及其他信息
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():  # request.is_ajax()方法判断是否是AJAX请求
            return HttpResponseBadRequest('不是AJAX请求')
        return f(request, *args, **kwargs)

    return wrap


class AuthorRequireView(View):
    """
    验证是否为原作者，用于状态删除、文章编辑
    """

    def dispatch(self, request, *args, **kwargs):
        # 状态和文章实例有user属性
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
