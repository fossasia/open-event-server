from django.urls import path

from .views import EventSubTopicCreate, EventSubTopicList, EventSubTopicRetrieve, EventSubTopicRetrieveUpdateDestroy

urlpatterns = [
    path("event-sub-topics/", EventSubTopicCreate.as_view(), name="event_sub_topic_create"),
    path("event-sub-topics/<int:pk>/", EventSubTopicRetrieveUpdateDestroy.as_view(), name="event_sub_topic_detail"),
    path(
        "event-topics/<int:event_topic_id>/event-sub-topics", EventSubTopicList.as_view(), name="event_sub_topic_list"
    ),
    path(
        "events/<int:event_id>/event-sub-topic",
        EventSubTopicRetrieve.as_view(),
        name="event_event_sub_topic_view_detail",
    ),
    path(
        "custom-placeholders/<int:custom_placeholder_id>/event-sub-topic",
        EventSubTopicRetrieve.as_view(),
        name="custom_placeholder_event_sub_topic_view_detail",
    ),
]
