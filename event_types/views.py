from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import EventType
from .serializer import EventTypeSerializer


class EventTypeListCreate(generics.ListCreateAPIView):
    """Allows listing and creation of EventType."""

    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

    # Fields to allow sorting by
    ordering_fields = ["name", "slug", "deleted_at"]


class EventTypeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of EventType."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = EventTypeSerializer


class EventTypeRetrieveRelation(generics.RetrieveAPIView):
    """Allows viewing of the related EventType."""

    permission_classes = (IsSuperAdminForUpdate,)
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get("event_id") is not None:
            # TODO: implement fetching event topic by event id
            self.kwargs["pk"] = 1

        return self.retrieve(request, *args, **kwargs)
