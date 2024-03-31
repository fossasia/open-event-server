from django.db import models
# imported fields from #9123 where event tickets & discount codes are created.
from events.models import Event
from tickets.models import Ticket

class MailingList(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.email:
            return self.email
        else:
            return "No email specified"
