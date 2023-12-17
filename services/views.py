from rest_framework import generics

from open_event_api.permissions import IsSuperAdminForUpdate

from .models import Service
from .serializer import ServiceSerializer


# TODO: Add ability to filter based on `name`.
class ServiceList(generics.ListAPIView):
    """Allows listing Service."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    # Fields to allow sorting by
    ordering_fields = ["name"]


class ServiceRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """Allows viewing and updating of Service."""

    permission_classes = (IsSuperAdminForUpdate,)
    serializer_class = ServiceSerializer
