from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import PanelPermission
from .serializer import PanelPermissionSerializer


class PanelPermissionListCreate(generics.ListCreateAPIView):
    """Allows listing and creation of PanelPermission."""

    queryset = PanelPermission.objects.all()
    serializer_class = PanelPermissionSerializer

    # Fields to allow sorting by
    ordering_fields = ["name", "slug", "deleted_at"]


class PanelPermissionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of PanelPermission."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = PanelPermissionSerializer


class PanelPermissionRetrieveRelation(generics.ListAPIView):
    """Allows viewing of the related PanelPermissions."""

    permission_classes = (IsSuperAdminForUpdate,)
    queryset = PanelPermission.objects.all()
    serializer_class = PanelPermissionSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get("custom_system_role_id") is not None:
            # TODO: implement fetching panel permission by custom system role id
            self.kwargs["pk"] = 1

        return self.retrieve(request, *args, **kwargs)
