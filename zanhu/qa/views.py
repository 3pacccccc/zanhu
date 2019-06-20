from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages

from helpers import ajax_required
from zanhu.qa.models import Question, Answer
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


class CreateAnswerView(LoginRequiredMixin, CreateView):
    """
    回答问题
    """
    model = Answer
    fields = ['content', ]
    message = "您的问题已提交"
    template_name = 'qa/answer_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs['question_id']
        return super(CreateAnswerView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:question_detail', kwargs={"pk": self.kwargs['question_id']})


@login_required
@ajax_required
@require_http_methods(['POST'])
def question_vote(request):
    """
    给问题投票，AJAX POST请求
    """
    question_id = request.POST['question']
    value = True if request.POST['value'] == 'u' else False # U表示赞，D表示踩
    question = Question.objects.get(pk=question_id)
    users = question.votes.values_list('user', flat=True)   # 当前问题的所有投票用户

    # # 1.用户首次操作，点赞/踩
    # if request.user.pk not in users:
    #     question.votes.create(user=request.user, value=value)
    #
    # # 2.用户已经赞过，要取消赞/踩一下
    # elif question.votes.get(user=request.user).value:
    #     if value:
    #         question.votes.get(user=request.user).delete()
    #     else:
    #         question.votes.update(user=request.user, value=value)
    #
    # # 3.用户已经踩过，要取消踩/赞一下
    # else:
    #     if not value:
    #         question.votes.get(user=request.user).delete()
    #     else:
    #         question.votes.update(user=request.user, value=value)

    # 以上三步可以简化为
    if request.user.pk in users and (question.votes.get(user=request.user).value==value):
        question.votes.get(user=request.user).delete()

    else:
        question.votes.update_or_create(user=request.user, defaults={"value": value})

    return JsonResponse({'votes': question.total_votes()})


@login_required
@ajax_required
@require_http_methods(['POST'])
def answer_vote(request):
    """
    给回答投票，AJAX POST请求
    """
    answer_id = request.POST['answer']
    value = True if request.POST['value'] == 'U' else False
    answer = Answer.objects.get(uuid_id=answer_id)
    users = answer.votes.values_list('user', flat=True)

    if request.user.pk in users and (answer.votes.get(user=request.user).value==value):
        answer.votes.get(user=request.user).delete()

    else:
        answer.votes.update_or_create(user=request.user, defaults={'value': value})

    return JsonResponse({'votes': answer.total_votes()})


@login_required
@ajax_required
@require_http_methods(['POST'])
def accept_answer(request):
    """
    接受回答，AJAX_POST请求
    已经被接受的回答用户不能取消
    """
    answer_id = request.POST['answer']
    answer = Answer.objects.get(uuid_id=answer_id)

    # 如果当前登录用户不是提问者，抛出权限拒绝错误
    if answer.question.user.username != request.user.username:
        raise  PermissionDenied

    answer.accept_answer()
    return JsonResponse({'status': "true"})
