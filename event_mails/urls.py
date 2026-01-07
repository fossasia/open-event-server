from django.urls import path
from .api import EventMailListCreateView

urlpatterns = [
    path("", EventMailListCreateView.as_view(), name="event-mails"),
]


