from django.urls import path

from .views import PanelPermissionListCreate, PanelPermissionRetrieveRelation, PanelPermissionRetrieveUpdateDestroy

urlpatterns = [
    path("panel-permissions/", PanelPermissionListCreate.as_view(), name="panel_permission_list_create"),
    path("panel-permissions/<int:pk>/", PanelPermissionRetrieveUpdateDestroy.as_view(), name="panel_permission_detail"),
    path(
        "custom-system-roles/<int:custom_system_role_id>/panel-permissions/",
        PanelPermissionRetrieveRelation.as_view(),
        name="custom_system_role_panel_permissions",
    ),
]
