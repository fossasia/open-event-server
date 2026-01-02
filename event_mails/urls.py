from django.urls import path

from .views import EventMailListCreate, EventMailRetrieveUpdateDestroy

urlpatterns = [
    path("event-mails/", EventMailListCreate.as_view()),
    path("event-mails/<int:pk>/", EventMailRetrieveUpdateDestroy.as_view()),

]
