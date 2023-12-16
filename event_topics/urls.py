from django.urls import path

from .views import EventTopicListCreate, EventTopicRetrieveRelation, EventTopicRetrieveUpdateDestroy

urlpatterns = [
    path("event-topics/", EventTopicListCreate.as_view(), name="event_topic_list_create"),
    path("event-topics/<int:pk>/", EventTopicRetrieveUpdateDestroy.as_view(), name="event_topic_detail"),
    path("events/<int:event_id>/event-topic/", EventTopicRetrieveRelation.as_view(), name="event_event_topic_detail"),
    path(
        "event-sub-topics/<int:event_sub_topic_id>/event-topic/",
        EventTopicRetrieveRelation.as_view(),
        name="event_sub_topic_event_topic_detail",
    ),
]
