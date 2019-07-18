from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    template_name = 'users/user_detail.html'
    slug_url_kwarg = "username"  # url里面包含username的关键字参数

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user.username)
        context['moments_num'] = user.publisher.filter(reply=False).count()
        context['article_num'] = user.author.filter(status="P").count()
        context['comment_num'] = user.publisher.filter(reply=True).count() + user.comment_comments.all().count()
        context['quetion_num'] = user.q_author.all().count()
        context['answer_num'] = user.a_author.all().count()
        tmp = set()
        sent_num = user.sent_messages.all()
        for s in sent_num:
            tmp.add(s.recipient.username)
        recieved_num = user.received_messages.all()
        for r in recieved_num:
            tmp.add(r.sender.username)

        context['interaction_num'] = user.liked_news.all().count() + user.qa_vote.all().count() + context['comment_num'] + len(
            tmp)
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["nickname", 'email', 'picture', 'introduction', 'job_title', 'location', 'personal_url', 'weibo', 'zhihu',
              'github', 'linkedin']

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)
