from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import EventTopic
from .serializer import EventTopicSerializer


class EventTopicListCreate(generics.ListCreateAPIView):
    """Allows listing and creation of EventTopic."""

    queryset = EventTopic.objects.all()
    serializer_class = EventTopicSerializer

    # Fields to allow sorting by
    ordering_fields = ["name", "slug", "deleted_at"]


class EventTopicRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of EventTopic."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = EventTopicSerializer


class EventTopicRetrieveRelation(generics.RetrieveAPIView):
    """Allows viewing of the related EventTopic."""

    permission_classes = (IsSuperAdminForUpdate,)
    queryset = EventTopic.objects.all()
    serializer_class = EventTopicSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get("event_id") is not None:
            # TODO: implement fetching event topic by event id
            self.kwargs["pk"] = 1
        if kwargs.get("event_sub_topic_id") is not None:
            # TODO: implement fetching event topic by event sub topic id
            self.kwargs["pk"] = 1

        return self.retrieve(request, *args, **kwargs)
