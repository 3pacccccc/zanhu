from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from zanhu.notifications.models import Notification


class NofiticationUnreadListView(LoginRequiredMixin, ListView):
    """
    未读通知列表
    """
    model = Notification
    context_object_name = 'notification_list'
    template_name = 'notifications/notification_list.html'

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    """
    将所有通知标记为已读
    """
    request.user.notifications.mark_all_as_read()
    redirect_url = request.GET.get('next')
    messages.add_message(request, messages.SUCCESS, f'用户{request.user.username}的所有通知标为已读!')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug):
    """
    根据slug标为已读
    """
    notification = get_object_or_404(Notification, slug=slug)
    notification.mark_as_read()

    redirect_url = request.GET.get('next')

    messages.add_message(request, messages.SUCCESS, f'通知{notification}标为已读')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('notifications:unread')


@login_required
def get_latest_notifications(request):
    """
    显示的未读通知
    """
    notifications = request.user.notifications.get_most_recent()
    return render(request, 'notifications/most_recent.html', {'notifications': notifications})
