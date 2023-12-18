from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import Group
from .serializer import GroupSerializer


class GroupListCreate(generics.ListCreateAPIView):
    """Allows listing and creation of Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # Fields to allow sorting by
    ordering_fields = ["name"]
    # TODO: Add filtering based on name field.


class GroupRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of Group."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = GroupSerializer


class GroupRetrieveRelation(generics.RetrieveAPIView):
    """Allows viewing of the related Group."""

    permission_classes = (IsSuperAdminForUpdate,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get("event_id") is not None:
            # TODO: implement fetching group by event id
            self.kwargs["pk"] = 1

        return self.retrieve(request, *args, **kwargs)


class GroupListRelation(generics.ListAPIView):
    """Allows listing of the related Group."""

    permission_classes = (IsSuperAdminForUpdate,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # Fields to allow sorting by
    ordering_fields = ["name"]
    # TODO: Add filtering based on name field.

    def get(self, request, *args, **kwargs):
        if kwargs.get("user_id") is not None:
            # TODO: implement fetching group by user id
            self.kwargs["pk"] = 1

        return self.list(request, *args, **kwargs)
