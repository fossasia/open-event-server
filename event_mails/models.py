from django.db import models


class EventMail(models.Model):
    event_id = models.IntegerField(db_index=True, help_text="ID of the event from events table")
    email = models.EmailField()
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.role})"
