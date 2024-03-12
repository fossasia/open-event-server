from django.db import models

from events.models import Event
from tickets.models import Ticket


# Create your models here.
class DiscountCodeTicket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
