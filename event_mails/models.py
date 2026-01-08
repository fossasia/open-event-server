from django.db import models


class EventMail(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
    )

    RECIPIENT_CHOICES = (
        ('attendees', 'Attendees'),
        ('speakers', 'Speakers'),
        ('all', 'All'),
    )

    event_id = models.IntegerField()
    subject = models.CharField(max_length=255)
    body = models.TextField()

    recipients = models.CharField(
        max_length=20,
        choices=RECIPIENT_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"Mail for event {self.event_id}: {self.subject}"
