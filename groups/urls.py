from django.urls import path

from .views import GroupListCreate, GroupListRelation, GroupRetrieveRelation, GroupRetrieveUpdateDestroy

urlpatterns = [
    path("groups/", GroupListCreate.as_view(), name="group_list_create"),
    path("groups/<int:pk>/", GroupRetrieveUpdateDestroy.as_view(), name="group_detail_update_delete"),
    path("events/<int:event_id>/group", GroupRetrieveRelation.as_view(), name="event_group_detail"),
    path("users/<int:user_id>/groups", GroupListRelation.as_view(), name="user_group_list"),
]
