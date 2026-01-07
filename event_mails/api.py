from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import EventMail
from .serializers import EventMailSerializer


class EventMailListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        if not event_id:
            return Response([], status=status.HTTP_200_OK)

        mails = EventMail.objects.filter(event_id=event_id)
        serializer = EventMailSerializer(mails, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventMailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

