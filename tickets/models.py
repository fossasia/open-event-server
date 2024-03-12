from django.db import models

from events.models import Event


# Create your models here.
class Ticket(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_description_visible = models.BooleanField(null=True)
    type = models.CharField(max_length=255)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    sales_starts_at = models.DateTimeField()
    sales_ends_at = models.DateTimeField()
    is_hidden = models.BooleanField(null=True)
    min_order = models.IntegerField(null=True, blank=True)
    max_order = models.IntegerField(null=True, blank=True)
    event_id = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    is_fee_absorbed = models.BooleanField(null=True)
    position = models.IntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    auto_checkin_enabled = models.BooleanField(null=True)
    is_checkin_restricted = models.BooleanField(null=True)
    max_price = models.FloatField(null=True, blank=True)
    min_price = models.FloatField(default=0)
    form_id = models.CharField(max_length=255, null=True, blank=True)
    badge_id = models.CharField(max_length=255, null=True, blank=True)
