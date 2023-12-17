from django.db import models


class NotificationContent(models.Model):
    type = models.CharField(max_length=200)
    target_type = models.CharField(max_length=200)
    target_id = models.IntegerField()
    target_action = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} {self.target_type} {self.target_id} {self.target_action}"
