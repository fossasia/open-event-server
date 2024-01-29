from django.urls import path

from .views import EventSubTopicPost, EventSubTopicList,EventSubTopicRetrieveUpdateDestroy

urlpatterns = [
    path("event-sub-topics/", EventSubTopicPost.as_view(), name="event_sub_topic_list_create"),
    path("event-sub-topics/<int:pk>/", EventSubTopicRetrieveUpdateDestroy.as_view(), name="event_sub_topic_detail"),
    path("event-topics/<int:event_topic_id>/event-sub-topics/", EventSubTopicList.as_view(), name="event_sub_topic_list"),
]
