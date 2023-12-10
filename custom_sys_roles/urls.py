from django.urls import path

from .views import CustomSysRoleDetail, CustomSysRoleView

urlpatterns = [
    path("<int:pk>/", CustomSysRoleDetail.as_view(), name="custom_sys_role_detail"),
    path("", CustomSysRoleView.as_view(), name="custom_sys_role_list"),
]
