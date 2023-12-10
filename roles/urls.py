from django.urls import path

from .views import RoleDetail, RoleView

urlpatterns = [
    path("/<int:pk>/", RoleDetail.as_view(), name="role_detail"),
    path("", RoleView.as_view(), name="roles_list"),
]
