from rest_framework import generics

from .models import CustomSysRole
from .serializer import CustomSysRoleSerializer


class CustomSysRoleView(generics.ListAPIView):
    queryset = CustomSysRole.objects.all()
    serializer_class = CustomSysRoleSerializer


class CustomSysRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomSysRole.objects.all()
    serializer_class = CustomSysRoleSerializer
