from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages

from zanhu.qa.models import Question
from .forms import QuestionForm


class QuestionListView(LoginRequiredMixin, ListView):
    """
    所有问题
    """
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa/question_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionListView, self).get_context_data(*args, **kwargs)
        context['popular_tags'] = Question.objects.get_counted_tags()
        context['active'] = 'all'
        return context


class AnsweredQuestionListView(QuestionListView):

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *args, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data(*args, **kwargs)
        context['active'] = 'answered'

        return context


class UnAnsweredQuestionListView(QuestionListView):

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *args, **kwargs):
        context = super(UnAnsweredQuestionListView, self).get_context_data(*args, **kwargs)
        context['active'] = 'unanswered'

        return context


class CreateQuestionVIew(LoginRequiredMixin, CreateView):
    """
    用户创建提问
    """
    form_class = QuestionForm
    template_name = 'qa/question_form.html'
    message = '问题已提交'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateQuestionVIew, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)

        return reverse_lazy('qa:unanswered_q')


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question_detail.html'





