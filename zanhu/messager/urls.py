from django.urls import path

from zanhu.news import views


app_name = "messager"
urlpatterns = [
    path('', views.MessagesListView.as_view(), name='messages'),
    path("<str:username>/", views.MessagesListView.as_view(), name='ms')
]

