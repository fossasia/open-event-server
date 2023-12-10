from django.urls import path

from .views import RoleDetail, RoleView

urlpatterns = [
    path("roles/<int:pk>/", RoleDetail.as_view(), name="role_detail"),
    path("role-invites/<int:role_invite_id>/role/", RoleDetail.as_view(), name="role_invite_role_detail"),
    path(
        "users-events-roles/<int:users_events_roles_id>/role",
        RoleDetail.as_view(),
        name="users_events_role_role_detail",
    ),
    path(
        "users-groups-roles/<int:users_groups_roles_id>/role",
        RoleDetail.as_view(),
        name="users_groups_role_role_detail",
    ),
    path("roles/", RoleView.as_view(), name="roles_list"),
]
