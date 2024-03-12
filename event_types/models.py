from django.db import models


# Create your models here.
class EventType(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
