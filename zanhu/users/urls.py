from django.urls import path

from zanhu.users import views
from zanhu.users.views import (
    user_redirect_view,
    user_update_view,
    user_detail_view,
)

app_name = "users"
urlpatterns = [
    path("update/", views.UserUpdateView.as_view(), name="update"),

    path("~redirect/", view=user_redirect_view, name="redirect"),

    path("<str:username>/", view=user_detail_view, name="detail"),
]
