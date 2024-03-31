# imported fields from #9123 where event tickets & discount codes are created.
from events.models import Event
from tickets.models import Ticket

class BadgeGeneration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Badge for {self.ticket} at {self.event}"
