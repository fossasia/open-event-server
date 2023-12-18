from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import EventSubTopic
from .serializer import EventSubTopicSerializer


class EventSubTopicCreate(generics.CreateAPIView):
    """Allows creation of EventSubTopic."""

    serializer_class = EventSubTopicSerializer


class EventSubTopicList(generics.ListAPIView):
    """Allows listing EventSubTopic."""

    queryset = EventSubTopic.objects.all()
    serializer_class = EventSubTopicSerializer

    # Fields to allow sorting by
    ordering_fields = ["name"]


class EventSubTopicRetrieve(generics.RetrieveAPIView):
    """Allows viewing of the related EventSubTopic."""

    queryset = EventSubTopic.objects.all()
    serializer_class = EventSubTopicSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get("event_id") is not None:
            # TODO: implement fetching event sub topic by event id
            self.kwargs["pk"] = 1
        if kwargs.get("custom_placeholder_id") is not None:
            # TODO: implement fetching event sub topic by custom placeholder id
            self.kwargs["pk"] = 1

        return self.retrieve(request, *args, **kwargs)


class EventSubTopicRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of EventSubTopic."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = EventSubTopicSerializer
