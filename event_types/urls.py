from django.urls import path

from .views import EventTypeListCreate, EventTypeRetrieveRelation, EventTypeRetrieveUpdateDestroy

urlpatterns = [
    path("event-types/", EventTypeListCreate.as_view(), name="event_type_list_create"),
    path("event-types/<int:pk>/", EventTypeRetrieveUpdateDestroy.as_view(), name="event_type_detail"),
    path("events/<int:event_id>/event-type/", EventTypeRetrieveRelation.as_view(), name="event_event_type_detail"),
]
