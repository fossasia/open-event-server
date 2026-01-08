from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        mail = self.get_object()
        emails = request.data.get("emails")

        if not emails or not isinstance(emails, list):
            return Response(
                {"error": "emails must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            send_mail(
                subject=mail.subject,
                message=mail.body,
                from_email=None,
                recipient_list=emails,
                fail_silently=False,
            )
            mail.status = "sent"
            mail.sent_at = timezone.now()
            mail.save()
            return Response({"status": "sent"})
        except Exception as e:
            mail.status = "failed"
            mail.error = str(e)
            mail.save()
            return Response(
                {"status": "failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def post(self, request):
        serializer = EventMailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

