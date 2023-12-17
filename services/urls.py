from django.urls import path

from .views import ServiceList, ServiceRetrieveUpdate

urlpatterns = [
    path("services/", ServiceList.as_view(), name="service_list"),
    path("services/<int:pk>/", ServiceRetrieveUpdate.as_view(), name="service_detail_update"),
]

# TODO: run python manage.py makemigrations
# TODO: compare with previous API and fix any issues
