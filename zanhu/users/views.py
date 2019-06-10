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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["nickname", 'email', 'picture', 'introduction', 'job_title', 'location', 'personal_url', 'weibo', 'zhihu',
              'github', 'linkedin']


    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)
