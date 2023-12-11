from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import CustomSysRole
from .serializer import CustomSysRoleSerializer


class CustomSysRoleView(generics.ListAPIView):
    queryset = CustomSysRole.objects.all()
    serializer_class = CustomSysRoleSerializer


class CustomSysRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSuperAdminForUpdate,)
    queryset = CustomSysRole.objects.all()
    serializer_class = CustomSysRoleSerializer
