from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import Role
from .serializer import RoleSerializer


class RoleView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSuperAdminForUpdate,)
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get(self, request, *args, **kwargs):
        # Warning: we need to set self.kwargs['pk'] here,
        # since the default implementation of get_object()
        # does not use the kwargs argument.
        if kwargs.get("role_invite_id") is not None:
            # TODO
            self.kwargs["pk"] = 1
        if kwargs.get("users_events_roles_id") is not None:
            # TODO
            self.kwargs["pk"] = 1
        if kwargs.get("users_groups_roles_id") is not None:
            # TODO
            self.kwargs["pk"] = 1
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
