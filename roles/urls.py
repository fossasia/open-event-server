from django.urls import path

from .views import RoleView

urlpatterns = [
    path("", RoleView.as_view(), name="roles_list"),
]
