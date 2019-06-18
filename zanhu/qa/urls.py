from django.urls import path

from zanhu.qa import views


app_name = "qa"

urlpatterns = [
    path('indexed/', views.QuestionListView.as_view(), name='all_q'),
    path('', views.UnAnsweredQuestionListView.as_view(), name='unanswered_q'),
    path('answered/', views.AnsweredQuestionListView.as_view(), name='answered_q'),
    path('ask_question/', views.CreateQuestionVIew.as_view(), name='ask_question'),
    path('question-detail/<int:pk>', views.QuestionDetailView.as_view(), name='question_detail'),

]

