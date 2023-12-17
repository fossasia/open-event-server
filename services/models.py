from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name}"
