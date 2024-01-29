from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate
from rest_framework.exceptions import PermissionDenied

from .serializer import EventSubTopicSerializer
from .models import EventSubTopic,EventTopic

class EventSubTopicPost(generics.CreateAPIView):
    """
    Create event sub topics
    """
    serializer_class = EventSubTopicSerializer

    def perform_create(self, serializer):
        """
        Custom method to perform additional actions on object creation
        """
        event_topic = self.request.data.get('event_topic')
        if not event_topic:
            raise serializer.ValidationError({'event_topic': 'This field is required.'})
        serializer.save()


class EventSubTopicList(generics.ListAPIView):
    """
    List event sub topics
    """
    serializer_class = EventSubTopicSerializer

    def get_queryset(self):
        queryset = EventSubTopic.objects.all()

        event_topic_id = self.kwargs.get('event_topic_id')
        if event_topic_id:
            event_topic = EventTopic.objects.all() 
            if event_topic:
                queryset = queryset.all()

        return queryset
    
class EventSubTopicRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete event sub topics
    """
    queryset = EventSubTopic.objects.all()
    serializer_class = EventSubTopicSerializer
    permission_classes = [IsSuperAdminForUpdate]

    def put(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail='Admin access is required.')

        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail='Admin access is required.')

        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail='Admin access is required.')

        return super().delete(request, *args, **kwargs)
    
