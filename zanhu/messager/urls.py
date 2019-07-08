from django.urls import path

from zanhu.messager import views


app_name = "messager"
urlpatterns = [
    path('', views.MessagesListView.as_view(), name='message_list'),
    path('send-message/', views.send_message, name='send_message'),
    path('receive-message/', views.receive_message, name='receive_message'),
    path("<str:username>/", views.MessagesListView.as_view(), name='ms')
]

