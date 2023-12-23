from django.db import models
from events.models import Event
from users.models import CustomUser

class DiscountCode(models.Model):
    code = models.CharField(max_length=2147483647)
    value = models.FloatField()
    type = models.CharField(max_length=2147483647)
    is_active = models.BooleanField(null=True, blank=True)
    tickets_number = models.IntegerField(null=True, blank=True)
    min_quantity = models.IntegerField(null=True, blank=True)
    max_quantity = models.IntegerField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_till = models.DateTimeField(null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    marketer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    used_for = models.CharField(max_length=2147483647)
    discount_url = models.CharField(max_length=2147483647, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('event', 'code', 'deleted_at'),)