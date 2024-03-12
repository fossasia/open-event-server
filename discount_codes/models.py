from django.contrib.postgres.fields import CICharField
from django.db import models

from users.models import CustomUser


class DiscountCode(models.Model):
    code = CICharField(max_length=255, unique=True, null=True)
    value = models.FloatField()
    type = models.CharField(max_length=255)
    is_active = models.BooleanField(null=True, blank=True)
    tickets_number = models.IntegerField(null=True, blank=True)
    min_quantity = models.IntegerField(null=True, blank=True)
    max_quantity = models.IntegerField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_till = models.DateTimeField(null=True, blank=True)
    associated_event = models.ForeignKey("events.Event", on_delete=models.SET_NULL, null=True, blank=True)
    # Use 'associated_event' to avoid naming conflict. Using'events.Event' as a string to avoid circular import.
    created_at = models.DateTimeField(null=True, blank=True)
    marketer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    used_for = models.CharField(max_length=255)
    discount_url = models.URLField(blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
