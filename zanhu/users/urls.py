from django.urls import path

from zanhu.users import views


app_name = "users"
urlpatterns = [
    path("update/", views.UserUpdateView.as_view(), name="update"),

    # path("~redirect/", view=views, name="redirect"),

    path("<str:username>/", views.UserDetailView.as_view(), name="detail"),
]
