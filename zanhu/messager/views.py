from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from zanhu.messager.models import Message

from zanhu.helpers import ajax_required

User = get_user_model()


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    paginate_by = 10
    template_name = 'messager/message_list.html'

    def get_context_data(self, *args, **kwargs):
        # 获取当前登录用户外的所有用户，按最近登录时间降序排列
        context = super(MessagesListView, self).get_context_data(*args, **kwargs)
        context['user_list'] = User.objects.filter(is_active=True).exclude(username=self.request.user).order_by(
            '-last_login')[:10]
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        # 最近私信互动的内容
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)


class ConversationListView(MessagesListView):
    """
    与指定用户的私信内容
    """

    def get_context_data(self, *args, **kwargs):
        context = super(ConversationListView, self).get_context_data(*args, **kwargs)
        context['active'] = self.kwargs['username']  # url传过来的username
        return context

    def get_queryset(self):
        active_user = get_object_or_404(User, username=self.kwargs['username'])
        return Message.objects.get_conversation(self.request.user, active_user)


@ajax_required
@login_required
@require_http_methods(['POST'])
def send_message(request):
    """
    发送消息， AJAX POST请求
    """
    sender = request.user
    recipient_username = request.POST['to']
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST['message']

    if len(message.strip()) != 0 and recipient != sender:
        msg = Message.objects.create(
            sender=sender,
            recipient=recipient,
            message=message
        )
        return render(request, 'messager/single_message.html', {"message": msg})

    return HttpResponse()

@ajax_required
@login_required
@require_http_methods(['GET'])
def receive_message(request):
    """
    接受消息，AJAX请求
    :param request:
    :return:
    """
    message_id = request.GET['message_id']
    msg = Message.objects.get(pk=message_id)
    return render(request, 'messager/single_message.html', {"message": msg})
