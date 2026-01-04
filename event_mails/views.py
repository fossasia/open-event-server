from rest_framework import generics
from .models import EventMail
from .serializer import EventMailSerializer


class EventMailListCreate(generics.ListCreateAPIView):
    """Allows listing and creation of EventMail."""

    queryset = EventMail.objects.all()
    serializer_class = EventMailSerializer


class EventMailRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Allows viewing, updating and deleting of EventMail."""

    queryset = EventMail.objects.all()
    serializer_class = EventMailSerializer


