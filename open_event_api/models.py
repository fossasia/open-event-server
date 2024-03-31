from django.db import models

class MailingList(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.email:
            return self.email
        else:
            return "No email specified"

